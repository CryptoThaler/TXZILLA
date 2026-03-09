from app.schemas.score_schema import ScoreRequest
from app.services.scoring_service import score_property


def test_score_property_returns_expected_keys():
    request = ScoreRequest(
        list_price=400000,
        estimated_rent=3000,
        taxes_monthly=500,
        insurance_monthly=100,
        maintenance_monthly=150,
        hoa_monthly=50,
        vacancy_reserve_monthly=100,
        management_cost_monthly=150,
        appreciation_score=80,
        market_growth_score=75,
        risk_inverse_score=85,
        liquidity_score=70,
    )
    result = score_property(request)
    assert "investment_score" in result
    assert "cap_rate" in result
    assert result["monthly_cash_flow"] == 1950
    assert result["investment_score"] == 74.25
    assert result["assumptions"] == ["acquisition_basis_defaulted_to_list_price"]


def test_score_property_uses_explicit_acquisition_basis_without_assumption():
    request = ScoreRequest(
        list_price=400000,
        acquisition_basis=350000,
        estimated_rent=3000,
        taxes_monthly=500,
        insurance_monthly=100,
        maintenance_monthly=150,
        hoa_monthly=50,
        vacancy_reserve_monthly=100,
        management_cost_monthly=150,
        appreciation_score=80,
        market_growth_score=75,
        risk_inverse_score=85,
        liquidity_score=70,
    )
    result = score_property(request)
    assert result["cap_rate"] == 0.0669
    assert result["assumptions"] == []
