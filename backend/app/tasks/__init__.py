from app.tasks.celery_app import celery_app
from app.tasks.search_tasks import (
    run_search_task,
    scrape_store_details,
    scrape_instagram_profile,
    scrape_tiktok_profile,
)

__all__ = [
    "celery_app",
    "run_search_task",
    "scrape_store_details",
    "scrape_instagram_profile",
    "scrape_tiktok_profile",
]
