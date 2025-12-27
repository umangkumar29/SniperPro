from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api.deps import get_db
from app.analytics import analyze_price, get_price_trend, calculate_savings

router = APIRouter()


class PriceAnalysisResponse(BaseModel):
    """Response model for price analysis."""
    product_id: int
    product_name: str
    current_price: float
    
    avg_7_day: float | None
    avg_30_day: float | None
    avg_90_day: float | None
    
    min_price_30_day: float | None
    max_price_30_day: float | None
    
    is_fake_sale: bool
    fake_sale_confidence: float
    real_discount_percentage: float | None
    
    recommendation: str


class PriceTrendPoint(BaseModel):
    date: str
    price: float


class SavingsCalculation(BaseModel):
    actual_savings_per_unit: float
    actual_savings_total: float
    actual_discount_percentage: float
    is_worth_buying: bool


@router.get("/{product_id}/analysis", response_model=PriceAnalysisResponse)
async def analyze_product_price(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a product's price to detect fake sales.
    
    Returns:
    - Moving averages (7, 30, 90 days)
    - Fake sale detection with confidence score
    - Real discount percentage
    - Buy recommendation
    """
    try:
        analysis = await analyze_price(db, product_id)
        return PriceAnalysisResponse(
            product_id=analysis.product_id,
            product_name=analysis.product_name,
            current_price=analysis.current_price,
            avg_7_day=analysis.avg_7_day,
            avg_30_day=analysis.avg_30_day,
            avg_90_day=analysis.avg_90_day,
            min_price_30_day=analysis.min_price_30_day,
            max_price_30_day=analysis.max_price_30_day,
            is_fake_sale=analysis.is_fake_sale,
            fake_sale_confidence=analysis.fake_sale_confidence,
            real_discount_percentage=analysis.real_discount_percentage,
            recommendation=analysis.recommendation
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{product_id}/trend", response_model=List[PriceTrendPoint])
async def get_product_price_trend(
    product_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """
    Get price history for charting.
    
    Args:
        product_id: Product ID
        days: Number of days of history (default 30)
    
    Returns:
        List of {date, price} for Plotly/charts
    """
    trend = await get_price_trend(db, product_id, days)
    
    if not trend:
        raise HTTPException(status_code=404, detail="No price history found")
    
    return trend


@router.get("/{product_id}/savings")
async def calculate_product_savings(
    product_id: int,
    quantity: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate actual savings for a product.
    
    Compares current price to 30-day average to show
    real savings (not inflated "discounts").
    """
    try:
        analysis = await analyze_price(db, product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    if not analysis.avg_30_day:
        raise HTTPException(
            status_code=400, 
            detail="Insufficient price history for savings calculation"
        )
    
    savings = calculate_savings(
        current_price=analysis.current_price,
        avg_price=analysis.avg_30_day,
        quantity=quantity
    )
    
    return {
        "product_id": product_id,
        "product_name": analysis.product_name,
        "current_price": analysis.current_price,
        "avg_30_day_price": analysis.avg_30_day,
        "quantity": quantity,
        **savings
    }
