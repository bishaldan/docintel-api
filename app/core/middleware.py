import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response


async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-MS"] = str(round((time.perf_counter() - start) * 1000, 2))
    return response

