from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.websocket import manager
from app.core.rate_limit import RateLimitMiddleware
from app.core.dependencies import get_db
from app.core.health import get_full_health_status, check_database, check_redis, check_celery
from app.api.routes import stores_router, searches_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    yield
    # Shutdown - clean up connections
    pass


app = FastAPI(
    title=settings.app_name,
    description="API for discovering and extracting Shopify store data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    requests_per_hour=1000,
)

# Include routers
app.include_router(stores_router, prefix=settings.api_prefix)
app.include_router(searches_router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    """Simple health check endpoint for load balancers."""
    return {"status": "healthy"}


@app.get("/health/detailed")
async def health_check_detailed(db: Session = Depends(get_db)):
    """
    Detailed health check endpoint.

    Returns status of all system components including database, Redis, and Celery workers.
    """
    return await get_full_health_status(db)


@app.get("/health/db")
async def health_check_db(db: Session = Depends(get_db)):
    """Check database health."""
    return await check_database(db)


@app.get("/health/redis")
async def health_check_redis():
    """Check Redis health."""
    return await check_redis()


@app.get("/health/celery")
async def health_check_celery():
    """Check Celery workers health."""
    return await check_celery()


@app.websocket("/ws/search/{search_id}")
async def websocket_search(websocket: WebSocket, search_id: int):
    """
    WebSocket endpoint for real-time search updates.

    Connect to receive updates for a specific search job.
    Messages sent:
    - {"type": "search_update", "search_id": int, "status": str, "stores_found": int}
    - {"type": "store_found", "search_id": int, "store": {...}}
    """
    await manager.connect(websocket, search_id)
    try:
        while True:
            # Keep connection alive, handle any client messages
            data = await websocket.receive_text()
            # Client can send ping to keep alive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, search_id)


@app.websocket("/ws")
async def websocket_global(websocket: WebSocket):
    """
    Global WebSocket endpoint for all updates.

    Connect to receive all search updates across the application.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
