from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.store_repository import StoreRepository
from app.repositories.search_repository import SearchRepository
from app.services.store_service import StoreService
from app.services.search_service import SearchService


def get_store_repository(db: Session = Depends(get_db)) -> StoreRepository:
    return StoreRepository(db)


def get_search_repository(db: Session = Depends(get_db)) -> SearchRepository:
    return SearchRepository(db)


def get_store_service(
    store_repo: StoreRepository = Depends(get_store_repository),
) -> StoreService:
    return StoreService(store_repo)


def get_search_service(
    search_repo: SearchRepository = Depends(get_search_repository),
    store_repo: StoreRepository = Depends(get_store_repository),
) -> SearchService:
    return SearchService(search_repo, store_repo)
