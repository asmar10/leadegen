from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class SearchStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SearchJob(Base):
    __tablename__ = "search_jobs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(500), nullable=False)
    niche = Column(String(255), nullable=True, index=True)
    location = Column(String(255), nullable=True, index=True)
    status = Column(Enum(SearchStatus), default=SearchStatus.PENDING, nullable=False, index=True)
    stores_found = Column(Integer, default=0)
    error_message = Column(String(1000), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    results = relationship("SearchResult", back_populates="search_job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SearchJob {self.id}: {self.query}>"


class SearchResult(Base):
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("search_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    search_job = relationship("SearchJob", back_populates="results")
    store = relationship("Store", back_populates="search_results")

    def __repr__(self):
        return f"<SearchResult search={self.search_id} store={self.store_id}>"
