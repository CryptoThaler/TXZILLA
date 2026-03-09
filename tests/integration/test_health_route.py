from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_route():
    response = client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"]["reachable"] is True
    assert payload["database"]["dialect"] == "sqlite"


def test_live_route():
    response = client.get("/live")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "TXZILLA API"


def test_ready_route_returns_200_for_reachable_dev_runtime():
    response = client.get("/ready")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"]["reachable"] is True
