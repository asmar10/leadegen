from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.repositories.base import BaseRepository
from app.models.search import SearchJob, SearchResult, SearchStatus
from app.models.store import Store


class SearchRepository(BaseRepository[SearchJob]):
    def __init__(self, db: Session):
        super().__init__(db, SearchJob)

    def get_with_results(self, id: int) -> Optional[SearchJob]:
        """Get search job with store results loaded."""
        return (
            self.db.query(SearchJob)
            .options(joinedload(SearchJob.results).joinedload(SearchResult.store))
            .filter(SearchJob.id == id)
            .first()
        )

    def get_stores_for_search(self, search_id: int) -> list[Store]:
        """Get all stores found in a search."""
        results = (
            self.db.query(SearchResult)
            .options(joinedload(SearchResult.store))
            .filter(SearchResult.search_id == search_id)
            .all()
        )
        return [r.store for r in results]

    def add_store_to_search(self, search_id: int, store_id: int) -> SearchResult:
        """Add a store to search results."""
        result = SearchResult(search_id=search_id, store_id=store_id)
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def update_status(
        self,
        search_id: int,
        status: SearchStatus,
        error_message: Optional[str] = None,
    ) -> Optional[SearchJob]:
        """Update search job status."""
        search = self.get(search_id)
        if not search:
            return None

        search.status = status

        if status == SearchStatus.RUNNING:
            search.started_at = datetime.utcnow()
        elif status in (SearchStatus.COMPLETED, SearchStatus.FAILED):
            search.completed_at = datetime.utcnow()

        if error_message:
            search.error_message = error_message

        self.db.commit()
        self.db.refresh(search)
        return search

    def increment_stores_found(self, search_id: int) -> Optional[SearchJob]:
        """Increment the stores found counter."""
        search = self.get(search_id)
        if search:
            search.stores_found += 1
            self.db.commit()
            self.db.refresh(search)
        return search

    def get_recent(self, limit: int = 10) -> list[SearchJob]:
        """Get recent search jobs."""
        return (
            self.db.query(SearchJob)
            .order_by(SearchJob.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_pending(self) -> list[SearchJob]:
        """Get pending search jobs."""
        return (
            self.db.query(SearchJob)
            .filter(SearchJob.status == SearchStatus.PENDING)
            .order_by(SearchJob.created_at.asc())
            .all()
        )
