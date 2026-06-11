from fastapi import FastAPI

from app.api.v1 import documents, health
from app.core.config import settings
from app.core.middleware import request_id_middleware


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.middleware("http")(request_id_middleware)
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
    return app


app = create_app()

