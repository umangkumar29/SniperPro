import asyncio
import sys
from sqlalchemy import text
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

async def migrate():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async with engine.begin() as conn:
        print("Migrating: Adding image_url to products table...")
        try:
            await conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url VARCHAR"))
            print("Migration complete!")
        except Exception as e:
            print(f"Migration failed: {e}")
            
    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(migrate())
