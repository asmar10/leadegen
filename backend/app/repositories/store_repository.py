from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.repositories.base import BaseRepository
from app.models.store import Store


class StoreRepository(BaseRepository[Store]):
    def __init__(self, db: Session):
        super().__init__(db, Store)

    def get_by_domain(self, domain: str) -> Optional[Store]:
        return self.db.query(Store).filter(Store.domain == domain).first()

    def get_by_url(self, url: str) -> Optional[Store]:
        return self.db.query(Store).filter(Store.url == url).first()

    def search(
        self,
        query: Optional[str] = None,
        niche: Optional[str] = None,
        country: Optional[str] = None,
        has_email: Optional[bool] = None,
        has_instagram: Optional[bool] = None,
        has_tiktok: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Store], int]:
        """Search stores with filtering."""
        q = self.db.query(Store)

        if query:
            search_term = f"%{query}%"
            q = q.filter(
                or_(
                    Store.store_name.ilike(search_term),
                    Store.domain.ilike(search_term),
                    Store.description.ilike(search_term),
                )
            )

        if niche:
            q = q.filter(Store.niche.ilike(f"%{niche}%"))

        if country:
            q = q.filter(Store.country.ilike(f"%{country}%"))

        if has_email is True:
            q = q.filter(Store.email.isnot(None), Store.email != "")

        if has_instagram is True:
            q = q.filter(Store.instagram.isnot(None), Store.instagram != "")

        if has_tiktok is True:
            q = q.filter(Store.tiktok.isnot(None), Store.tiktok != "")

        total = q.count()
        items = q.order_by(Store.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    def get_or_create(self, domain: str, defaults: dict) -> tuple[Store, bool]:
        """Get existing store or create new one."""
        store = self.get_by_domain(domain)
        if store:
            return store, False

        store_data = {"domain": domain, **defaults}
        store = self.create(store_data)
        return store, True

    def get_niches(self) -> list[str]:
        """Get distinct niches."""
        result = (
            self.db.query(Store.niche)
            .filter(Store.niche.isnot(None))
            .distinct()
            .all()
        )
        return [r[0] for r in result if r[0]]

    def get_countries(self) -> list[str]:
        """Get distinct countries."""
        result = (
            self.db.query(Store.country)
            .filter(Store.country.isnot(None))
            .distinct()
            .all()
        )
        return [r[0] for r in result if r[0]]
