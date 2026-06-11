from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    request_id: str | None,
    details: Any = None,
) -> JSONResponse:
    content: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    if details is not None:
        content["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=content)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return error_response(
            status_code=exc.status_code,
            code="http_error",
            message=str(exc.detail),
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="validation_error",
            message="Request validation failed",
            request_id=getattr(request.state, "request_id", None),
            details=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        request.app.state.logger.exception("Unhandled exception", extra={"request_id": request_id})
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="internal_server_error",
            message="An unexpected error occurred",
            request_id=request_id,
        )

