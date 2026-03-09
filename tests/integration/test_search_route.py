from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_search_route_filters_by_region_and_price():
    response = client.get(
        "/search",
        params={
            "region_key": "central_texas",
            "query": "Mission Ridge",
            "max_list_price": 400000,
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] >= 1
    assert payload["items"][0]["property_id"] == "prop-bexar-001"


def test_property_detail_route_returns_nested_listing():
    response = client.get("/properties/prop-bexar-001")
    assert response.status_code == 200

    payload = response.json()
    assert payload["active_listing"]["list_price"] == 365000.0
    assert payload["last_transaction"]["sale_price"] == 330000.0
