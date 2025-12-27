from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class Platform(str, Enum):
    AMAZON = "amazon"
    FLIPKART = "flipkart"
    MYNTRA = "myntra"
    UNKNOWN = "unknown"

class ProductBase(SQLModel):
    """Base product fields shared between create and read."""
    url: str = Field(index=True, unique=True)
    name: str
    current_price: float
    currency: str = "INR"
    platform: Platform = Platform.UNKNOWN
    is_available: bool = True
    image_url: Optional[str] = None

class Product(ProductBase, table=True):
    """Product table in database."""
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    price_history: List["PriceHistory"] = Relationship(back_populates="product")
    alerts: List["Alert"] = Relationship(back_populates="product")

class ProductCreate(SQLModel):
    """Schema for creating a new product (user input)."""
    url: str

class ProductRead(ProductBase):
    """Schema for reading product data."""
    id: int
    created_at: datetime
    updated_at: datetime
    image_url: Optional[str] = None

class ProductWithHistory(ProductRead):
    """Product with price history included."""
    price_history: List["PriceHistoryRead"] = []


# --- Price History Models ---
class PriceHistoryBase(SQLModel):
    """Base price history fields."""
    price: float
    currency: str = "INR"

class PriceHistory(PriceHistoryBase, table=True):
    """Price history table - stores historical prices for time-series analysis."""
    __tablename__ = "price_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    scraped_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationship
    product: Optional[Product] = Relationship(back_populates="price_history")

class PriceHistoryRead(PriceHistoryBase):
    """Schema for reading price history."""
    id: int
    scraped_at: datetime


# --- Alert Models ---
class AlertBase(SQLModel):
    """Base alert fields."""
    target_price: float
    contact_method: str = "telegram"  # telegram, sms, email
    contact_value: str  # telegram chat_id, phone number, or email
    is_active: bool = True

class Alert(AlertBase, table=True):
    """Alert table - stores user price alerts."""
    __tablename__ = "alerts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    triggered_at: Optional[datetime] = None
    
    # Relationship
    product: Optional[Product] = Relationship(back_populates="alerts")

class AlertCreate(SQLModel):
    """Schema for creating an alert."""
    product_id: int
    target_price: float
    contact_method: str = "telegram"
    contact_value: str

class AlertRead(AlertBase):
    """Schema for reading alert data."""
    id: int
    product_id: int
    created_at: datetime
    triggered_at: Optional[datetime]


# Update forward references
ProductWithHistory.model_rebuild()
