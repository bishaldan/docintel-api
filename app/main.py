from fastapi import FastAPI

from app.api.v1 import documents, health
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import request_id_middleware
from app.core.rate_limit import rate_limit_middleware


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.state.logger = configure_logging()
    app.middleware("http")(request_id_middleware)
    app.middleware("http")(rate_limit_middleware)
    register_exception_handlers(app)
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
    return app


app = create_app()
