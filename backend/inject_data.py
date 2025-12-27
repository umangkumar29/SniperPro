import asyncio
import sys
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.product import Product, PriceHistory
from app.core.config import settings

# Setup DB connection
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def inject_history(product_id: int):
    async with AsyncSessionLocal() as session:
        # Get product
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        
        if not product:
            print(f"Product {product_id} not found!")
            return

        print(f"Injecting history for: {product.name[:50]}...")
        current_price = product.current_price
        
        # Generate 30 days of data
        history_points = []
        base_price = current_price * 1.2 # Assume it was 20% more expensive before
        
        for i in range(30, 0, -1):
            # Create a realistic fluctuation trend
            # Slowly dropping price with some noise
            day_price = base_price * (1 - (0.005 * (30-i))) # Gradual drop
            noise = random.uniform(-0.02, 0.02) * day_price
            final_price = round(day_price + noise, 2)
            
            # Ensure the last point matches current price close enough
            if i == 1: 
                final_price = current_price

            point = PriceHistory(
                product_id=product.id,
                price=final_price,
                currency="INR",
                scraped_at=datetime.utcnow() - timedelta(days=i)
            )
            history_points.append(point)
            
        session.add_all(history_points)
        await session.commit()
        print(f"Successfully added {len(history_points)} historical data points!")

async def main():
    # Fetch the most recent product ID to inject data into
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product).order_by(Product.id.desc()).limit(1))
        product = result.scalar_one_or_none()
        if product:
             await inject_history(product.id)
        else:
            print("No products found in DB.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
