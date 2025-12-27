from fastapi import APIRouter
from app.api.v1.endpoints import products, alerts, analytics

api_router = APIRouter()

api_router.include_router(
    products.router, 
    prefix="/products", 
    tags=["products"]
)

api_router.include_router(
    alerts.router, 
    prefix="/alerts", 
    tags=["alerts"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)
