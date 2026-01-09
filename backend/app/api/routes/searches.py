from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_search_service
from app.services.search_service import SearchService
from app.schemas.search import (
    SearchJobCreate,
    SearchJobResponse,
    SearchJobWithResults,
    SearchJobListResponse,
)
from app.tasks.search_tasks import run_search_task

router = APIRouter(prefix="/searches", tags=["searches"])


@router.get("", response_model=SearchJobListResponse)
def list_searches(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search_service: SearchService = Depends(get_search_service),
):
    """List all search jobs."""
    return search_service.list_searches(page=page, page_size=page_size)


@router.get("/recent", response_model=list[SearchJobResponse])
def get_recent_searches(
    limit: int = Query(10, ge=1, le=50, description="Number of recent searches"),
    search_service: SearchService = Depends(get_search_service),
):
    """Get recent search jobs."""
    return search_service.get_recent_searches(limit=limit)


@router.get("/{search_id}", response_model=SearchJobResponse)
def get_search(
    search_id: int,
    search_service: SearchService = Depends(get_search_service),
):
    """Get a specific search job."""
    search = search_service.get_search(search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    return search


@router.get("/{search_id}/results", response_model=SearchJobWithResults)
def get_search_results(
    search_id: int,
    search_service: SearchService = Depends(get_search_service),
):
    """Get a search job with its results."""
    search = search_service.get_search_with_results(search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    return search


@router.post("", response_model=SearchJobResponse, status_code=201)
def create_search(
    search_data: SearchJobCreate,
    search_service: SearchService = Depends(get_search_service),
):
    """
    Create a new search job.

    The search will be queued and executed asynchronously.
    Poll the search status endpoint to check progress.
    """
    search = search_service.create_search(search_data)

    # Queue the Celery task
    run_search_task.delay(search.id)

    return search


@router.post("/{search_id}/retry", response_model=SearchJobResponse)
def retry_search(
    search_id: int,
    search_service: SearchService = Depends(get_search_service),
):
    """Retry a failed search job."""
    from app.models.search import SearchStatus

    search = search_service.get_search(search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    if search.status not in (SearchStatus.FAILED, SearchStatus.COMPLETED):
        raise HTTPException(
            status_code=400,
            detail="Can only retry failed or completed searches"
        )

    # Reset status and re-queue
    search_service.update_search_status(search_id, SearchStatus.PENDING)
    run_search_task.delay(search_id)

    return search_service.get_search(search_id)


@router.delete("/{search_id}", status_code=204)
def delete_search(
    search_id: int,
    search_service: SearchService = Depends(get_search_service),
):
    """Delete a search job."""
    if not search_service.delete_search(search_id):
        raise HTTPException(status_code=404, detail="Search not found")
