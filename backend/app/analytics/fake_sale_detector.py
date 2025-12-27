"""
Fake Sale Detection Algorithm

A "fake sale" is when an e-commerce site:
1. Inflates the price before a sale
2. Then shows a "discount" back to the original price

We detect this by:
1. Calculating the 30-day moving average price
2. Comparing current "sale" price to the average
3. If the "discounted" price is >= average, it's likely fake

Example:
- Product normally sells at ₹10,000
- Before sale: Price raised to ₹15,000
- During sale: "50% off!" → ₹7,500
- But 30-day average shows: ₹10,000
- Real discount = 25%, not 50%
"""

from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, PriceHistory


@dataclass
class PriceAnalysis:
    """Result of price analysis for a product."""
    product_id: int
    product_name: str
    current_price: float
    
    # Moving averages
    avg_7_day: Optional[float]
    avg_30_day: Optional[float]
    avg_90_day: Optional[float]
    
    # Price range
    min_price_30_day: Optional[float]
    max_price_30_day: Optional[float]
    
    # Analysis results
    is_fake_sale: bool
    fake_sale_confidence: float  # 0.0 to 1.0
    real_discount_percentage: Optional[float]
    
    # Recommendation
    recommendation: str
    

async def get_price_stats(
    session: AsyncSession, 
    product_id: int,
    days: int = 30
) -> dict:
    """Get price statistics for a product over N days."""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    result = await session.execute(
        select(
            func.avg(PriceHistory.price).label("avg_price"),
            func.min(PriceHistory.price).label("min_price"),
            func.max(PriceHistory.price).label("max_price"),
            func.count(PriceHistory.id).label("data_points")
        )
        .where(PriceHistory.product_id == product_id)
        .where(PriceHistory.scraped_at >= cutoff_date)
    )
    
    row = result.one()
    
    return {
        "avg": float(row.avg_price) if row.avg_price else None,
        "min": float(row.min_price) if row.min_price else None,
        "max": float(row.max_price) if row.max_price else None,
        "data_points": row.data_points
    }


async def analyze_price(
    session: AsyncSession,
    product_id: int
) -> PriceAnalysis:
    """
    Analyze a product's price to detect fake sales.
    
    Returns detailed analysis including:
    - Moving averages (7, 30, 90 days)
    - Fake sale detection
    - Real discount percentage
    - Buy recommendation
    """
    
    # Get product
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise ValueError(f"Product {product_id} not found")
    
    current_price = product.current_price
    
    # Get stats for different time periods
    stats_7 = await get_price_stats(session, product_id, days=7)
    stats_30 = await get_price_stats(session, product_id, days=30)
    stats_90 = await get_price_stats(session, product_id, days=90)
    
    # Calculate fake sale detection
    is_fake_sale = False
    fake_sale_confidence = 0.0
    real_discount_percentage = None
    recommendation = "Insufficient data"
    
    # Need at least 1 data point for basic analysis
    if stats_30["data_points"] >= 1 and stats_30["avg"]:
        avg_30 = stats_30["avg"]
        
        # If we only have 1 data point, we can't really judge trends yet
        if stats_30["data_points"] == 1:
             is_fake_sale = False
             fake_sale_confidence = 0.0
             real_discount_percentage = 0.0
             recommendation = "🆕 First track! We're building history."
        else:
             # Calculate how current price compares to average
             price_vs_avg = (avg_30 - current_price) / avg_30 * 100
             
             if price_vs_avg < 0:
                 # Current price is HIGHER than average - definitely not a good deal
                 is_fake_sale = True
                 fake_sale_confidence = min(abs(price_vs_avg) / 20, 1.0)  # Scale to 0-1
                 real_discount_percentage = price_vs_avg  # Negative = premium
                 recommendation = f"⚠️ OVERPRICED! {abs(price_vs_avg):.1f}% above 30-day avg"
                 
             elif price_vs_avg < 5:
                 # Current price is within 5% of average - not a real sale
                 is_fake_sale = True
                 fake_sale_confidence = 0.8
                 real_discount_percentage = price_vs_avg
                 recommendation = f"😐 FAKE SALE! Only {price_vs_avg:.1f}% below avg."
                 
             elif price_vs_avg < 10:
                 # 5-10% below average - marginal deal
                 is_fake_sale = False
                 fake_sale_confidence = 0.3
                 real_discount_percentage = price_vs_avg
                 recommendation = f"🤔 Okay deal. {price_vs_avg:.1f}% below average. Could wait for better."
                 
             elif price_vs_avg < 20:
                 # 10-20% below average - good deal
                 is_fake_sale = False
                 fake_sale_confidence = 0.0
                 real_discount_percentage = price_vs_avg
                 recommendation = f"✅ GOOD DEAL! {price_vs_avg:.1f}% below 30-day average."
                 
             else:
                 # 20%+ below average - excellent deal
                 is_fake_sale = False
                 fake_sale_confidence = 0.0
                 real_discount_percentage = price_vs_avg
                 
                 # Check if it's the lowest price ever
                 if stats_90["min"] and current_price <= stats_90["min"]:
                     recommendation = f"🔥 BEST PRICE EVER! {price_vs_avg:.1f}% below average. BUY NOW!"
                 else:
                     recommendation = f"🎉 GREAT DEAL! {price_vs_avg:.1f}% below average."
    
    return PriceAnalysis(
        product_id=product_id,
        product_name=product.name,
        current_price=current_price,
        avg_7_day=stats_7["avg"],
        avg_30_day=stats_30["avg"],
        avg_90_day=stats_90["avg"],
        min_price_30_day=stats_30["min"],
        max_price_30_day=stats_30["max"],
        is_fake_sale=is_fake_sale,
        fake_sale_confidence=fake_sale_confidence,
        real_discount_percentage=real_discount_percentage,
        recommendation=recommendation
    )


async def get_price_trend(
    session: AsyncSession,
    product_id: int,
    days: int = 30
) -> List[dict]:
    """
    Get price history for charting.
    Returns list of {date, price} for Plotly/charts.
    """
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    result = await session.execute(
        select(PriceHistory.scraped_at, PriceHistory.price)
        .where(PriceHistory.product_id == product_id)
        .where(PriceHistory.scraped_at >= cutoff_date)
        .order_by(PriceHistory.scraped_at.asc())
    )
    
    history = result.all()
    
    return [
        {
            "date": row.scraped_at.isoformat(),
            "price": row.price
        }
        for row in history
    ]


def calculate_savings(
    current_price: float,
    avg_price: float,
    quantity: int = 1
) -> dict:
    """Calculate actual savings vs claimed savings."""
    
    actual_savings = (avg_price - current_price) * quantity
    actual_percentage = (avg_price - current_price) / avg_price * 100
    
    return {
        "actual_savings_per_unit": round(actual_savings / quantity, 2),
        "actual_savings_total": round(actual_savings, 2),
        "actual_discount_percentage": round(actual_percentage, 2),
        "is_worth_buying": actual_percentage > 10
    }
