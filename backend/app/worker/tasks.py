from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio

from app.worker.celery_app import celery_app
from app.core.config import settings
from app.models.product import Product, PriceHistory, Alert
from app.scraper.factory import ScraperFactory
from app.scraper.utils import get_stealth_context, apply_stealth, simulate_human_behavior
from app.services.notification import NotificationService

from sqlalchemy.pool import NullPool

# Create async engine for worker
# Use NullPool to prevent connections from being tied to closed event loops in Celery tasks
worker_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    poolclass=NullPool
)
WorkerSessionLocal = sessionmaker(worker_engine, class_=AsyncSession, expire_on_commit=False)


def run_async(coro):
    """Helper to run async code in sync Celery task."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _scrape_product_async(url: str) -> Optional[dict]:
    """Async function to scrape a product."""
    from playwright.async_api import async_playwright
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            context = await get_stealth_context(browser)
            page = await context.new_page()
            await apply_stealth(page)
            
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await simulate_human_behavior(page)
            
            scraper = ScraperFactory.get_scraper(url)
            result = await scraper.scrape(page, url)
            
            await context.close()
            await browser.close()
            
            return {
                "title": result.title,
                "price": result.price,
                "currency": result.currency,
                "availability": result.availability,
                "image_url": result.image_url
            }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


async def _update_product_price_async(product_id: int, scraped_data: dict):
    """Update product price in database."""
    async with WorkerSessionLocal() as session:
        # Get product
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            return
        
        # Update product
        product.current_price = scraped_data["price"]
        product.is_available = scraped_data["availability"]
        # Update image if it changed (or was missing)
        if scraped_data.get("image_url"):
            product.image_url = scraped_data["image_url"]
        product.updated_at = datetime.utcnow()
        
        # Add price history entry
        price_entry = PriceHistory(
            product_id=product_id,
            price=scraped_data["price"],
            currency=scraped_data["currency"],
            scraped_at=datetime.utcnow()
        )
        session.add(price_entry)
        
        await session.commit()
        
        return product.current_price


async def _check_alerts_async(product_id: int, current_price: float):
    """Check if any alerts should be triggered."""
    async with WorkerSessionLocal() as session:
        # Get active alerts for this product
        result = await session.execute(
            select(Alert, Product)
            .join(Product, Alert.product_id == Product.id)
            .where(Alert.product_id == product_id)
            .where(Alert.is_active == True)
            .where(Alert.triggered_at == None)
        )
        rows = result.all()
        
        triggered_alerts = []
        for alert, product in rows:
            if current_price <= alert.target_price:
                # Price dropped below target!
                alert.triggered_at = datetime.utcnow()
                triggered_alerts.append({
                    "alert_id": alert.id,
                    "contact_method": alert.contact_method,
                    "contact_value": alert.contact_value,
                    "target_price": alert.target_price,
                    "current_price": current_price,
                    "product_name": product.name,
                    "product_url": product.url
                })
        
        await session.commit()
        return triggered_alerts


async def _get_all_products_async():
    """Get all tracked products."""
    async with WorkerSessionLocal() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return [(p.id, p.url, p.name) for p in products]


# ============ CELERY TASKS ============

@celery_app.task(bind=True, name="app.worker.tasks.scrape_product")
def scrape_product(self, product_id: int, url: str):
    """
    Task: Scrape a single product and update its price.
    """
    print(f"[Task] Scraping product {product_id}: {url}")
    
    # Scrape the product
    scraped_data = run_async(_scrape_product_async(url))
    
    if not scraped_data:
        print(f"[Task] Failed to scrape product {product_id}")
        return {"status": "failed", "product_id": product_id}
    
    # Update database
    current_price = run_async(_update_product_price_async(product_id, scraped_data))
    
    # Check alerts
    triggered_alerts = run_async(_check_alerts_async(product_id, current_price))
    
    # Send notifications for triggered alerts
    for alert in triggered_alerts:
        send_notification.delay(alert)
    
    print(f"[Task] Product {product_id} updated. Price: {current_price}")
    return {
        "status": "success",
        "product_id": product_id,
        "price": current_price,
        "alerts_triggered": len(triggered_alerts)
    }


@celery_app.task(bind=True, name="app.worker.tasks.check_all_prices")
def check_all_prices(self):
    """
    Periodic Task: Check prices for all tracked products.
    Runs every 30 minutes via Celery Beat.
    """
    print("[Periodic Task] Checking all product prices...")
    
    products = run_async(_get_all_products_async())
    
    print(f"[Periodic Task] Found {len(products)} products to check")
    
    # Queue individual scrape tasks for each product
    for product_id, url, name in products:
        scrape_product.delay(product_id, url)
    
    return {"status": "queued", "products_count": len(products)}


@celery_app.task(bind=True, name="app.worker.tasks.send_notification")
def send_notification(self, alert_data: dict):
    """
    Task: Send notification to user when price drops.
    """
    contact_method = alert_data["contact_method"]
    current_price = alert_data["current_price"]
    target_price = alert_data["target_price"]
    product_name = alert_data.get("product_name", "Product")
    product_url = alert_data.get("product_url", "")
    
    # Format message
    message = NotificationService.format_alert_message(
        product_name, current_price, target_price, product_url
    )
    
    print(f"[Notification] Sending {contact_method} alert...")
    
    if contact_method == "telegram":
        success = NotificationService.send_telegram_message(
            message=message,
            chat_id=alert_data.get("contact_value") # Use user's specific chat_id if stored
        )
        return {"status": "sent", "success": success}
    
    return {"status": "skipped", "reason": "method_not_supported"}
