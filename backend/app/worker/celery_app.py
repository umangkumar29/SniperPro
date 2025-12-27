from celery import Celery
from app.core.config import settings
import sys
import asyncio

# Fix for Playwright on Windows in Celery
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Create Celery app
celery_app = Celery(
    "price_sniper",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.autodiscover_tasks(['app.worker'])

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "check-all-prices-every-15-minutes": {
            "task": "app.worker.tasks.check_all_prices",
            "schedule": 15 * 60,  # 15 minutes in seconds
        },
    },
    
    # Task settings
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_concurrency=2,  # Limit concurrent scraping
)
