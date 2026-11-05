from fastapi.testclient import TestClient

from news_api.main import app

client = TestClient(app)


def test_health_returns_ok(prepared_db) -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "api"
    assert body["checks"]["db"] is True
    assert body["checks"]["migrations"] is True
