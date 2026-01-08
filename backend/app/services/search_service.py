from typing import Optional
import math

from app.repositories.search_repository import SearchRepository
from app.repositories.store_repository import StoreRepository
from app.schemas.search import (
    SearchJobCreate,
    SearchJobResponse,
    SearchJobWithResults,
    SearchJobListResponse,
)
from app.schemas.store import StoreResponse
from app.models.search import SearchJob, SearchStatus


class SearchService:
    def __init__(
        self,
        search_repo: SearchRepository,
        store_repo: StoreRepository,
    ):
        self.search_repo = search_repo
        self.store_repo = store_repo

    def create_search(self, search_data: SearchJobCreate) -> SearchJob:
        """Create a new search job."""
        return self.search_repo.create(search_data.model_dump())

    def get_search(self, search_id: int) -> Optional[SearchJob]:
        return self.search_repo.get(search_id)

    def get_search_with_results(self, search_id: int) -> Optional[SearchJobWithResults]:
        """Get search job with all found stores."""
        search = self.search_repo.get(search_id)
        if not search:
            return None

        stores = self.search_repo.get_stores_for_search(search_id)

        return SearchJobWithResults(
            id=search.id,
            query=search.query,
            niche=search.niche,
            location=search.location,
            status=search.status,
            stores_found=search.stores_found,
            error_message=search.error_message,
            created_at=search.created_at,
            started_at=search.started_at,
            completed_at=search.completed_at,
            stores=[StoreResponse.model_validate(s) for s in stores],
        )

    def list_searches(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> SearchJobListResponse:
        skip = (page - 1) * page_size
        items = self.search_repo.get_all(skip=skip, limit=page_size)
        total = self.search_repo.count()
        pages = math.ceil(total / page_size) if total > 0 else 1

        return SearchJobListResponse(
            items=[SearchJobResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    def get_recent_searches(self, limit: int = 10) -> list[SearchJobResponse]:
        """Get recent search jobs."""
        searches = self.search_repo.get_recent(limit)
        return [SearchJobResponse.model_validate(s) for s in searches]

    def update_search_status(
        self,
        search_id: int,
        status: SearchStatus,
        error_message: Optional[str] = None,
    ) -> Optional[SearchJob]:
        return self.search_repo.update_status(search_id, status, error_message)

    def add_store_to_search(self, search_id: int, store_id: int) -> None:
        """Add a store to search results and increment counter."""
        self.search_repo.add_store_to_search(search_id, store_id)
        self.search_repo.increment_stores_found(search_id)

    def delete_search(self, search_id: int) -> bool:
        return self.search_repo.delete(search_id)
