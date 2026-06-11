def test_health_check(client):
    response = client.get("/api/v1/health", headers={"X-Request-ID": "docintel-test"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"] == "docintel-test"

