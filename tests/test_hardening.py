from app.core.config import settings
from app.core.rate_limit import rate_limiter


def test_validation_errors_use_consistent_shape(client):
    response = client.post("/api/v1/documents")

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["request_id"]


def test_not_found_errors_use_consistent_shape(client):
    response = client.get("/api/v1/documents/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "http_error"


def test_upload_rate_limit_returns_consistent_error(client):
    original_limit = settings.rate_limit_requests
    original_window = settings.rate_limit_window_seconds
    settings.rate_limit_requests = 1
    settings.rate_limit_window_seconds = 60
    rate_limiter.reset()
    try:
        first_response = client.post(
            "/api/v1/documents",
            files={"file": ("one.txt", b"Date: 2026-06-11", "text/plain")},
        )
        second_response = client.post(
            "/api/v1/documents",
            files={"file": ("two.txt", b"Date: 2026-06-11", "text/plain")},
        )
    finally:
        settings.rate_limit_requests = original_limit
        settings.rate_limit_window_seconds = original_window
        rate_limiter.reset()

    assert first_response.status_code == 201
    assert second_response.status_code == 429
    assert second_response.json()["error"]["code"] == "rate_limit_exceeded"

