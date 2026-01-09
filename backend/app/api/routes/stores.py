from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_store_service
from app.services.store_service import StoreService
from app.schemas.store import (
    StoreCreate,
    StoreUpdate,
    StoreResponse,
    StoreListResponse,
)
from app.tasks.search_tasks import scrape_store_details

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("", response_model=StoreListResponse)
def list_stores(
    query: Optional[str] = Query(None, description="Search query"),
    niche: Optional[str] = Query(None, description="Filter by niche"),
    country: Optional[str] = Query(None, description="Filter by country"),
    has_email: Optional[bool] = Query(None, description="Filter stores with email"),
    has_instagram: Optional[bool] = Query(None, description="Filter stores with Instagram"),
    has_tiktok: Optional[bool] = Query(None, description="Filter stores with TikTok"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    store_service: StoreService = Depends(get_store_service),
):
    """List stores with optional filtering."""
    return store_service.search_stores(
        query=query,
        niche=niche,
        country=country,
        has_email=has_email,
        has_instagram=has_instagram,
        has_tiktok=has_tiktok,
        page=page,
        page_size=page_size,
    )


@router.get("/filters")
def get_filter_options(
    store_service: StoreService = Depends(get_store_service),
):
    """Get available filter options (niches, countries)."""
    return store_service.get_filter_options()


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: int,
    store_service: StoreService = Depends(get_store_service),
):
    """Get a specific store by ID."""
    store = store_service.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.post("", response_model=StoreResponse, status_code=201)
def create_store(
    store_data: StoreCreate,
    store_service: StoreService = Depends(get_store_service),
):
    """Create a new store."""
    existing = store_service.get_store_by_domain(store_data.domain)
    if existing:
        raise HTTPException(status_code=400, detail="Store with this domain already exists")
    return store_service.create_store(store_data)


@router.patch("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    store_data: StoreUpdate,
    store_service: StoreService = Depends(get_store_service),
):
    """Update a store."""
    store = store_service.update_store(store_id, store_data)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.post("/{store_id}/rescrape")
def rescrape_store(
    store_id: int,
    scrape_social: bool = Query(False, description="Also scrape social media profiles"),
    store_service: StoreService = Depends(get_store_service),
):
    """
    Queue a rescrape of the store to update its data.

    Optionally scrape social media profiles for additional data.
    """
    store = store_service.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Queue the scrape task
    scrape_store_details.delay(store_id, scrape_social=scrape_social)

    return {"message": "Rescrape queued", "store_id": store_id}


@router.delete("/{store_id}", status_code=204)
def delete_store(
    store_id: int,
    store_service: StoreService = Depends(get_store_service),
):
    """Delete a store."""
    if not store_service.delete_store(store_id):
        raise HTTPException(status_code=404, detail="Store not found")
