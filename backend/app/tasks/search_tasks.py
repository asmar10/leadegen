import asyncio
import os
from datetime import datetime
from celery import shared_task

from app.db.database import SessionLocal
from app.repositories.search_repository import SearchRepository
from app.repositories.store_repository import StoreRepository
from app.models.search import SearchStatus
from app.scrapers import GoogleScraper, ShopifyScraper, SerpAPIScraper, InstagramScraper, TikTokScraper


def run_async(coro):
    """Helper to run async code in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(bind=True, max_retries=3)
def run_search_task(self, search_id: int):
    """
    Execute a search job.

    1. Search Google for Shopify stores matching niche/location
    2. Validate and scrape each found URL
    3. Extract store data and save to database
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

        # Run the async scraping logic
        result = run_async(_execute_search(
            search_id=search_id,
            query=search.query,
            niche=search.niche,
            location=search.location,
            search_repo=search_repo,
            store_repo=store_repo,
        ))

        return result

    except Exception as e:
        search_repo.update_status(
            search_id,
            SearchStatus.FAILED,
            error_message=str(e),
        )
        raise self.retry(exc=e, countdown=60)

    finally:
        db.close()


async def _execute_search(
    search_id: int,
    query: str,
    niche: str | None,
    location: str | None,
    search_repo: SearchRepository,
    store_repo: StoreRepository,
) -> dict:
    """Async search execution."""

    # Choose search method: SerpAPI if available, otherwise Playwright
    serpapi_key = os.getenv("SERPAPI_KEY")

    if serpapi_key:
        searcher = SerpAPIScraper(api_key=serpapi_key)
        search_query = searcher._build_search_query(niche or query, location)
        urls = await searcher.search(search_query, max_results=50)
    else:
        searcher = GoogleScraper()
        try:
            urls = await searcher.search_shopify_stores(
                niche=niche or query,
                location=location,
                max_results=50,
            )
        finally:
            await searcher.close()

    if not urls:
        search_repo.update_status(search_id, SearchStatus.COMPLETED)
        return {"search_id": search_id, "status": "completed", "stores_found": 0}

    # Scrape each URL for Shopify store data
    shopify_scraper = ShopifyScraper()
    stores_found = 0

    try:
        for url in urls:
            try:
                # Check if store already exists
                from urllib.parse import urlparse
                domain = urlparse(url).netloc.replace("www.", "")

                existing = store_repo.get_by_domain(domain)
                if existing:
                    # Link existing store to search
                    search_repo.add_store_to_search(search_id, existing.id)
                    search_repo.increment_stores_found(search_id)
                    stores_found += 1
                    continue

                # Scrape the store
                store_data = await shopify_scraper.scrape(url)

                if store_data.get("error") or not store_data.get("is_shopify"):
                    continue

                # Create store record
                social = store_data.get("social_links", {})
                store = store_repo.create({
                    "url": store_data["url"],
                    "domain": store_data["domain"],
                    "store_name": store_data.get("store_name"),
                    "email": store_data.get("email"),
                    "phone": store_data.get("phone"),
                    "country": store_data.get("country"),
                    "niche": niche,
                    "description": store_data.get("description"),
                    "instagram": social.get("instagram"),
                    "tiktok": social.get("tiktok"),
                    "facebook": social.get("facebook"),
                    "twitter": social.get("twitter"),
                    "last_scraped_at": datetime.utcnow(),
                })

                # Link to search results
                search_repo.add_store_to_search(search_id, store.id)
                search_repo.increment_stores_found(search_id)
                stores_found += 1

            except Exception:
                # Continue with next URL on individual failures
                continue

    finally:
        await shopify_scraper.close()

    # Mark search as completed
    search_repo.update_status(search_id, SearchStatus.COMPLETED)

    return {
        "search_id": search_id,
        "status": "completed",
        "stores_found": stores_found,
    }


@shared_task(bind=True, max_retries=2)
def scrape_store_details(self, store_id: int, scrape_social: bool = False):
    """
    Scrape/update details for a specific store.

    Optionally scrapes social media profiles for additional data.
    """
    db = SessionLocal()

    try:
        store_repo = StoreRepository(db)
        store = store_repo.get(store_id)

        if not store:
            return {"error": "Store not found"}

        result = run_async(_scrape_store(store, store_repo, scrape_social))
        return result

    except Exception as e:
        raise self.retry(exc=e, countdown=30)

    finally:
        db.close()


async def _scrape_store(store, store_repo: StoreRepository, scrape_social: bool) -> dict:
    """Async store scraping."""
    shopify_scraper = ShopifyScraper()

    try:
        # Scrape store page
        store_data = await shopify_scraper.scrape(store.url)

        if store_data.get("error"):
            return {"store_id": store.id, "error": store_data["error"]}

        # Prepare update data
        social = store_data.get("social_links", {})
        update_data = {
            "store_name": store_data.get("store_name") or store.store_name,
            "email": store_data.get("email") or store.email,
            "phone": store_data.get("phone") or store.phone,
            "country": store_data.get("country") or store.country,
            "description": store_data.get("description") or store.description,
            "instagram": social.get("instagram") or store.instagram,
            "tiktok": social.get("tiktok") or store.tiktok,
            "facebook": social.get("facebook") or store.facebook,
            "twitter": social.get("twitter") or store.twitter,
            "last_scraped_at": datetime.utcnow(),
        }

        # Optionally scrape social media for more data
        if scrape_social:
            social_data = await _scrape_social_profiles(
                instagram=update_data.get("instagram"),
                tiktok=update_data.get("tiktok"),
            )
            # Could extract email from social bios, etc.
            if social_data.get("email") and not update_data.get("email"):
                update_data["email"] = social_data["email"]

        # Update store
        store_repo.update(store, update_data)

        return {"store_id": store.id, "status": "updated"}

    finally:
        await shopify_scraper.close()


async def _scrape_social_profiles(
    instagram: str | None,
    tiktok: str | None,
) -> dict:
    """Scrape social profiles for additional data."""
    data = {}

    if instagram:
        ig_scraper = InstagramScraper()
        try:
            ig_data = await ig_scraper.scrape(instagram)
            if ig_data.get("email"):
                data["email"] = ig_data["email"]
            if ig_data.get("bio_link"):
                data["instagram_bio_link"] = ig_data["bio_link"]
        finally:
            await ig_scraper.close()

    if tiktok:
        tt_scraper = TikTokScraper()
        try:
            tt_data = await tt_scraper.scrape(tiktok)
            if tt_data.get("email") and not data.get("email"):
                data["email"] = tt_data["email"]
            if tt_data.get("bio_link"):
                data["tiktok_bio_link"] = tt_data["bio_link"]
        finally:
            await tt_scraper.close()

    return data


@shared_task
def scrape_instagram_profile(handle: str) -> dict:
    """Standalone task to scrape an Instagram profile."""
    return run_async(_scrape_instagram(handle))


async def _scrape_instagram(handle: str) -> dict:
    scraper = InstagramScraper()
    try:
        return await scraper.scrape(handle)
    finally:
        await scraper.close()


@shared_task
def scrape_tiktok_profile(handle: str) -> dict:
    """Standalone task to scrape a TikTok profile."""
    return run_async(_scrape_tiktok(handle))


async def _scrape_tiktok(handle: str) -> dict:
    scraper = TikTokScraper()
    try:
        return await scraper.scrape(handle)
    finally:
        await scraper.close()
