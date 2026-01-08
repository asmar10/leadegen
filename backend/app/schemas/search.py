from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.search import SearchStatus
from app.schemas.store import StoreResponse


class SearchJobBase(BaseModel):
    query: str
    niche: Optional[str] = None
    location: Optional[str] = None


class SearchJobCreate(SearchJobBase):
    pass


class SearchJobResponse(SearchJobBase):
    id: int
    status: SearchStatus
    stores_found: int
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SearchJobWithResults(SearchJobResponse):
    stores: list[StoreResponse] = []


class SearchJobListResponse(BaseModel):
    items: list[SearchJobResponse]
    total: int
    page: int
    page_size: int
    pages: int
