from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, EmailStr


class StoreBase(BaseModel):
    url: str
    domain: str
    store_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    niche: Optional[str] = None
    description: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    store_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    niche: Optional[str] = None
    description: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None


class StoreResponse(StoreBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_scraped_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StoreListResponse(BaseModel):
    items: list[StoreResponse]
    total: int
    page: int
    page_size: int
    pages: int
