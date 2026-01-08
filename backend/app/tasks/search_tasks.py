from celery import shared_task

from app.db.database import SessionLocal
from app.repositories.search_repository import SearchRepository
from app.repositories.store_repository import StoreRepository
from app.models.search import SearchStatus


@shared_task(bind=True, max_retries=3)
def run_search_task(self, search_id: int):
    """
    Execute a search job.

    This task will be expanded in Phase 2 to:
    1. Use Google scraper to find Shopify stores
    2. Extract store data using Shopify scraper
    3. Optionally scrape social media profiles
    4. Save results to database
    """
    db = SessionLocal()

    try:
        search_repo = SearchRepository(db)
        store_repo = StoreRepository(db)

        # Update status to running
        search_repo.update_status(search_id, SearchStatus.RUNNING)

        search = search_repo.get(search_id)
        if not search:
            return {"error": "Search not found"}

        # TODO: Implement in Phase 2
        # 1. Build search query from niche + location
        # 2. Scrape Google for Shopify stores
        # 3. For each found URL:
        #    - Check if it's a Shopify store
        #    - Extract store data
        #    - Save to database
        #    - Link to search results

        # Placeholder: Mark as completed
        search_repo.update_status(search_id, SearchStatus.COMPLETED)

        return {
            "search_id": search_id,
            "status": "completed",
            "stores_found": search.stores_found,
        }

    except Exception as e:
        search_repo.update_status(
            search_id,
            SearchStatus.FAILED,
            error_message=str(e),
        )
        raise self.retry(exc=e, countdown=60)

    finally:
        db.close()


@shared_task
def scrape_store_details(store_id: int):
    """
    Scrape/update details for a specific store.

    Will be implemented in Phase 2.
    """
    db = SessionLocal()

    try:
        store_repo = StoreRepository(db)
        store = store_repo.get(store_id)

        if not store:
            return {"error": "Store not found"}

        # TODO: Implement in Phase 2
        # 1. Scrape Shopify store for updated info
        # 2. Extract social media links
        # 3. Optionally scrape social profiles
        # 4. Update store record

        return {"store_id": store_id, "status": "completed"}

    finally:
        db.close()
