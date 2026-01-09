import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimiter:
    """Simple in-memory rate limiter using sliding window."""

    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        # Dict of client_id -> list of (timestamp, count) for minute window
        self._minute_requests: Dict[str, list] = defaultdict(list)
        # Dict of client_id -> list of (timestamp, count) for hour window
        self._hour_requests: Dict[str, list] = defaultdict(list)

    def _clean_old_requests(self, requests: list, window_seconds: int) -> list:
        """Remove requests outside the time window."""
        cutoff = time.time() - window_seconds
        return [r for r in requests if r > cutoff]

    def is_allowed(self, client_id: str) -> Tuple[bool, dict]:
        """
        Check if a request from client_id is allowed.

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = time.time()

        # Clean and count minute requests
        self._minute_requests[client_id] = self._clean_old_requests(
            self._minute_requests[client_id], 60
        )
        minute_count = len(self._minute_requests[client_id])

        # Clean and count hour requests
        self._hour_requests[client_id] = self._clean_old_requests(
            self._hour_requests[client_id], 3600
        )
        hour_count = len(self._hour_requests[client_id])

        # Check limits
        rate_info = {
            "minute_limit": self.requests_per_minute,
            "minute_remaining": max(0, self.requests_per_minute - minute_count),
            "hour_limit": self.requests_per_hour,
            "hour_remaining": max(0, self.requests_per_hour - hour_count),
        }

        if minute_count >= self.requests_per_minute:
            rate_info["retry_after"] = 60
            return False, rate_info

        if hour_count >= self.requests_per_hour:
            rate_info["retry_after"] = 3600
            return False, rate_info

        # Record this request
        self._minute_requests[client_id].append(now)
        self._hour_requests[client_id].append(now)

        return True, rate_info


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI."""

    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute, requests_per_hour)
        # Paths to exclude from rate limiting
        self.excluded_paths = {"/health", "/docs", "/redoc", "/openapi.json", "/"}

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier."""
        # Use X-Forwarded-For if behind proxy, otherwise use client host
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Skip WebSocket connections
        if request.url.path.startswith("/ws"):
            return await call_next(request)

        client_id = self._get_client_id(request)
        is_allowed, rate_info = self.limiter.is_allowed(client_id)

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": rate_info.get("retry_after", 60),
                },
                headers={
                    "Retry-After": str(rate_info.get("retry_after", 60)),
                    "X-RateLimit-Limit-Minute": str(rate_info["minute_limit"]),
                    "X-RateLimit-Remaining-Minute": str(rate_info["minute_remaining"]),
                },
            )

        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit-Minute"] = str(rate_info["minute_limit"])
        response.headers["X-RateLimit-Remaining-Minute"] = str(rate_info["minute_remaining"])

        return response
