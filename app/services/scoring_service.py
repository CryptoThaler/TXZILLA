from app.schemas.score_schema import ScoreRequest


CASH_FLOW_NORMALIZER = 3000.0
SCORING_WEIGHTS = {
    "cash_flow": 0.30,
    "appreciation": 0.25,
    "market_growth": 0.20,
    "risk_inverse": 0.15,
    "liquidity": 0.10,
}


def score_property(p: ScoreRequest) -> dict:
    assumptions: list[str] = []
    acquisition_basis = p.acquisition_basis
    if acquisition_basis is None:
        acquisition_basis = p.list_price
        assumptions.append("acquisition_basis_defaulted_to_list_price")

    monthly_cash_flow = (
        p.estimated_rent
        - p.taxes_monthly
        - p.insurance_monthly
        - p.maintenance_monthly
        - p.hoa_monthly
        - p.vacancy_reserve_monthly
        - p.management_cost_monthly
    )
    annual_noi = monthly_cash_flow * 12
    cap_rate = annual_noi / acquisition_basis if acquisition_basis else 0.0
    cash_flow_score = max(
        0.0,
        min(100.0, (monthly_cash_flow / CASH_FLOW_NORMALIZER) * 100.0),
    )
    total_score = (
        SCORING_WEIGHTS["cash_flow"] * cash_flow_score
        + SCORING_WEIGHTS["appreciation"] * p.appreciation_score
        + SCORING_WEIGHTS["market_growth"] * p.market_growth_score
        + SCORING_WEIGHTS["risk_inverse"] * p.risk_inverse_score
        + SCORING_WEIGHTS["liquidity"] * p.liquidity_score
    )
    return {
        "monthly_cash_flow": round(monthly_cash_flow, 2),
        "annual_noi": round(annual_noi, 2),
        "cap_rate": round(cap_rate, 4),
        "cash_flow_score": round(cash_flow_score, 2),
        "investment_score": round(total_score, 2),
        "assumptions": assumptions,
    }
