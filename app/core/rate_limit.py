import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status

from app.core.config import settings
from app.core.errors import error_response

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, *, limit: int, window_seconds: int) -> bool:
        now = time.time()
        hits = self._hits[key]
        window_start = now - window_seconds
        while hits and hits[0] < window_start:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True

    def reset(self) -> None:
        self._hits.clear()


rate_limiter = InMemoryRateLimiter()


async def rate_limit_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.method not in WRITE_METHODS:
        return await call_next(request)

    client_host = request.client.host if request.client else "unknown"
    key = f"{client_host}:{request.method}:{request.url.path}"
    if not rate_limiter.allow(
        key,
        limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    ):
        return error_response(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="rate_limit_exceeded",
            message="Too many requests",
            request_id=getattr(request.state, "request_id", None),
        )
    return await call_next(request)
