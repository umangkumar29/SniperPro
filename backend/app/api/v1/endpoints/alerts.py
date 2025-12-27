from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.product import (
    Product, Alert, AlertCreate, AlertRead
)

router = APIRouter()


@router.post("/", response_model=AlertRead)
async def create_alert(
    alert_in: AlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a price alert for a product.
    - User will be notified when price drops to or below target price.
    """
    # Verify product exists
    result = await db.execute(
        select(Product).where(Product.id == alert_in.product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create alert
    new_alert = Alert(
        product_id=alert_in.product_id,
        target_price=alert_in.target_price,
        contact_method=alert_in.contact_method,
        contact_value=alert_in.contact_value,
        is_active=True
    )
    
    db.add(new_alert)
    await db.commit()
    await db.refresh(new_alert)
    
    return new_alert


@router.get("/product/{product_id}", response_model=List[AlertRead])
async def get_product_alerts(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all alerts for a specific product."""
    result = await db.execute(
        select(Alert)
        .where(Alert.product_id == product_id)
        .where(Alert.is_active == True)
        .order_by(Alert.created_at.desc())
    )
    alerts = result.scalars().all()
    return alerts


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete/deactivate an alert."""
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = False
    await db.commit()
    
    return {"message": "Alert deactivated successfully"}


@router.get("/", response_model=List[AlertRead])
async def list_active_alerts(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List all active alerts."""
    result = await db.execute(
        select(Alert)
        .where(Alert.is_active == True)
        .order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    alerts = result.scalars().all()
    return alerts
