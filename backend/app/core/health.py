"""Health check utilities for monitoring system status."""

from datetime import datetime
from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session
import redis

from app.core.config import get_settings

settings = get_settings()


async def check_database(db: Session) -> dict[str, Any]:
    """Check database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "latency_ms": 0,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


async def check_redis() -> dict[str, Any]:
    """Check Redis connectivity."""
    try:
        r = redis.from_url(settings.redis_url)
        start = datetime.now()
        r.ping()
        latency = (datetime.now() - start).total_seconds() * 1000
        info = r.info()
        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


async def check_celery() -> dict[str, Any]:
    """Check Celery worker status."""
    try:
        from app.tasks.celery_app import celery_app

        # Inspect active workers
        inspect = celery_app.control.inspect(timeout=2.0)

        stats = inspect.stats()
        if stats:
            worker_count = len(stats)
            worker_names = list(stats.keys())

            # Get active tasks
            active = inspect.active() or {}
            active_tasks = sum(len(tasks) for tasks in active.values())

            return {
                "status": "healthy",
                "workers": worker_count,
                "worker_names": worker_names,
                "active_tasks": active_tasks,
            }
        else:
            return {
                "status": "degraded",
                "message": "No workers available",
                "workers": 0,
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def get_system_info() -> dict[str, Any]:
    """Get basic system information."""
    import platform
    import os

    return {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
    }


async def get_full_health_status(db: Session) -> dict[str, Any]:
    """Get comprehensive health status of all components."""
    db_status = await check_database(db)
    redis_status = await check_redis()
    celery_status = await check_celery()

    # Determine overall status
    all_healthy = all(
        status.get("status") == "healthy"
        for status in [db_status, redis_status, celery_status]
    )

    any_unhealthy = any(
        status.get("status") == "unhealthy"
        for status in [db_status, redis_status, celery_status]
    )

    if all_healthy:
        overall_status = "healthy"
    elif any_unhealthy:
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "redis": redis_status,
            "celery": celery_status,
        },
        "system": get_system_info(),
    }
