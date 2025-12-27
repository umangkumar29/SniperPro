from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Async engine for FastAPI
async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=True,  # Set to False in production
    future=True
)

# Async session factory
async_session_factory = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_session():
    """Dependency to get async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables."""
    async with async_engine.begin() as conn:
        # Import all models to register them
        from app.models.product import Product, PriceHistory, Alert
        await conn.run_sync(SQLModel.metadata.create_all)

async def close_db():
    """Close database connections."""
    await async_engine.dispose()
