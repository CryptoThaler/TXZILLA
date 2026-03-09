from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_score_route():
    response = client.post("/score", json={
        "list_price": 400000,
        "estimated_rent": 3000,
        "taxes_monthly": 500,
        "insurance_monthly": 100,
        "maintenance_monthly": 150,
        "hoa_monthly": 50,
        "vacancy_reserve_monthly": 100,
        "management_cost_monthly": 150,
        "appreciation_score": 80,
        "market_growth_score": 75,
        "risk_inverse_score": 85,
        "liquidity_score": 70
    })
    assert response.status_code == 200
    assert "investment_score" in response.json()
