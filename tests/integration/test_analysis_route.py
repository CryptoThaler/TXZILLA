from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_route_returns_full_report():
    response = client.get("/analyze/prop-bexar-001")
    assert response.status_code == 200

    payload = response.json()
    assert payload["property"]["property_id"] == "prop-bexar-001"
    assert payload["valuation"]["estimated_value"] == 400621.5
    assert payload["risk"]["risk_inverse_score"] == 75.8
    assert payload["investment"]["investment_score"] == 64.39


def test_regions_route_returns_configured_regions():
    response = client.get("/regions")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["region_key"] == "central_texas"
