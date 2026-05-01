from __future__ import annotations

import time
from dataclasses import dataclass
from hashlib import sha256

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from pigenus.core.config import Settings


@dataclass
class Window:
    started_at: float
    count: int = 0


class InMemoryFixedWindowLimiter:
    def __init__(self, *, requests_per_minute: int) -> None:
        self.requests_per_minute = requests_per_minute
        self._windows: dict[str, Window] = {}

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        window = self._windows.get(key)
        if window is None or now - window.started_at >= 60:
            self._windows[key] = Window(started_at=now, count=1)
            return True
        if window.count >= self.requests_per_minute:
            return False
        window.count += 1
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings
        self.limiter = InMemoryFixedWindowLimiter(
            requests_per_minute=settings.rate_limit_requests_per_minute
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.settings.rate_limit_enabled or request.url.path == "/health":
            return await call_next(request)
        key = self._key_for(request)
        if not self.limiter.allow(key):
            return JSONResponse(
                {"detail": "rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": "60"},
            )
        return await call_next(request)

    def _key_for(self, request: Request) -> str:
        auth = request.headers.get("authorization", "")
        if auth:
            fingerprint = sha256(auth.encode("utf-8")).hexdigest()[:24]
            return f"auth:{fingerprint}"
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
