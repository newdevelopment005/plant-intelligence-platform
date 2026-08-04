"""Simple in-memory rate limiter middleware."""
import time
from collections import defaultdict

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP rate limiter using a sliding window counter.

    Default: 100 requests per minute per IP.
    Auth endpoints: 10 requests per minute per IP.
    """

    def __init__(self, app, default_limit: int = 100, auth_limit: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.default_limit = default_limit
        self.auth_limit = auth_limit
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_auth_endpoint(self, path: str) -> bool:
        return "/auth/login" in path or "/auth/register" in path or "/auth/refresh" in path

    def _cleanup_old_entries(self, client_ip: str, now: float):
        cutoff = now - self.window_seconds
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > cutoff
        ]

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.time()

        self._cleanup_old_entries(client_ip, now)

        limit = self.auth_limit if self._is_auth_endpoint(request.url.path) else self.default_limit
        current_count = len(self._requests[client_ip])

        if current_count >= limit:
            retry_after = int(self.window_seconds - (now - self._requests[client_ip][0]))
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": f"Rate limit exceeded. Try again in {retry_after}s.",
                    }
                },
                headers={"Retry-After": str(retry_after)},
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
