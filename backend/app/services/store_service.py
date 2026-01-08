from typing import Optional
import math

from app.repositories.store_repository import StoreRepository
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse, StoreListResponse
from app.models.store import Store


class StoreService:
    def __init__(self, store_repo: StoreRepository):
        self.store_repo = store_repo

    def get_store(self, store_id: int) -> Optional[Store]:
        return self.store_repo.get(store_id)

    def get_store_by_domain(self, domain: str) -> Optional[Store]:
        return self.store_repo.get_by_domain(domain)

    def create_store(self, store_data: StoreCreate) -> Store:
        return self.store_repo.create(store_data.model_dump())

    def update_store(self, store_id: int, store_data: StoreUpdate) -> Optional[Store]:
        store = self.store_repo.get(store_id)
        if not store:
            return None

        update_data = store_data.model_dump(exclude_unset=True)
        return self.store_repo.update(store, update_data)

    def delete_store(self, store_id: int) -> bool:
        return self.store_repo.delete(store_id)

    def search_stores(
        self,
        query: Optional[str] = None,
        niche: Optional[str] = None,
        country: Optional[str] = None,
        has_email: Optional[bool] = None,
        has_instagram: Optional[bool] = None,
        has_tiktok: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> StoreListResponse:
        skip = (page - 1) * page_size

        items, total = self.store_repo.search(
            query=query,
            niche=niche,
            country=country,
            has_email=has_email,
            has_instagram=has_instagram,
            has_tiktok=has_tiktok,
            skip=skip,
            limit=page_size,
        )

        pages = math.ceil(total / page_size) if total > 0 else 1

        return StoreListResponse(
            items=[StoreResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    def get_or_create_store(self, domain: str, defaults: dict) -> tuple[Store, bool]:
        return self.store_repo.get_or_create(domain, defaults)

    def get_filter_options(self) -> dict:
        """Get available filter options."""
        return {
            "niches": self.store_repo.get_niches(),
            "countries": self.store_repo.get_countries(),
        }
