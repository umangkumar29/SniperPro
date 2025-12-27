from typing import List, Optional
import traceback
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.api.deps import get_db
from app.models.product import (
    Product, ProductCreate, ProductRead, ProductWithHistory,
    PriceHistory, PriceHistoryRead,
    Alert, AlertCreate, AlertRead,
    Platform
)
from app.scraper.factory import ScraperFactory
from app.scraper.utils import get_stealth_context, apply_stealth, simulate_human_behavior

ERROR_PRODUCT_NOT_FOUND = "Product not found"


router = APIRouter()

def detect_platform(url: str) -> Platform:
    """Detect e-commerce platform from URL."""
    url_lower = url.lower()
    if "amazon" in url_lower:
        return Platform.AMAZON
    elif "flipkart" in url_lower:
        return Platform.FLIPKART
    elif "myntra" in url_lower:
        return Platform.MYNTRA
    return Platform.UNKNOWN


@router.post("/track", response_model=ProductRead)
async def track_product(
    product_in: ProductCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Start tracking a new product.
    - Checks if product already exists by URL
    - If new, scrapes current price and saves to database
    - Returns product data
    """
    # Check if product already exists
    result = await db.execute(
        select(Product).where(Product.url == product_in.url)
    )
    existing_product = result.scalar_one_or_none()
    
    if existing_product:
        return existing_product
    
    # Scrape product data
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            )
            context = await get_stealth_context(browser)
            page = await context.new_page()
            await apply_stealth(page)
            
            await page.goto(product_in.url, wait_until="domcontentloaded", timeout=60000)
            await simulate_human_behavior(page)
            
            scraper = ScraperFactory.get_scraper(product_in.url)
            scraped_data = await scraper.scrape(page, product_in.url)
            
            await context.close()
            await browser.close()
        
        # Create product in database
        platform = detect_platform(product_in.url)
        new_product = Product(
            url=product_in.url,
            name=scraped_data.title,
            current_price=scraped_data.price,
            currency=scraped_data.currency,
            platform=platform,
            is_available=scraped_data.availability,
            image_url=scraped_data.image_url
        )
        
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        
        # Add first price history entry
        price_entry = PriceHistory(
            product_id=new_product.id,
            price=scraped_data.price,
            currency=scraped_data.currency
        )
        db.add(price_entry)
        await db.commit()
        
        return new_product
        
    except Exception as e:
        traceback.print_exc()
        print(f"!!! SCRAPING ERROR: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to scrape product: {type(e).__name__} - {str(e)}")


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get product details by ID."""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.get("/{product_id}/history", response_model=List[PriceHistoryRead])
async def get_price_history(
    product_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get price history for a product (for charts)."""
    # First check if product exists
    product_result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    if not product_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get price history
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.scraped_at.desc())
        .limit(limit)
    )
    history = result.scalars().all()
    
    return history


@router.get("/", response_model=List[ProductRead])
async def list_products(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List all tracked products."""
    result = await db.execute(
        select(Product)
        .order_by(Product.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    products = result.scalars().all()
    return products


@router.post("/{product_id}/refresh")
async def refresh_product_price(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger a price refresh for a product.
    This queues a background task to scrape the latest price.
    """
    # Verify product exists
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Queue the scrape task
    from app.worker.tasks import scrape_product
    task = scrape_product.delay(product_id, product.url)
    
    return {
        "message": "Price refresh queued",
        "product_id": product_id,
        "task_id": task.id
    }


@router.post("/refresh-all")
async def refresh_all_prices():
    """
    Manually trigger price refresh for ALL tracked products.
    This queues background tasks via Celery.
    """
    from app.worker.tasks import check_all_prices
    task = check_all_prices.delay()
    
    return {
        "message": "Price refresh for all products queued",
        "task_id": task.id
    }

