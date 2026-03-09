from app.schemas.analysis_schema import (
    InvestmentAnalysisResponse,
    MarketContextResponse,
    RiskAssessmentResponse,
    ValuationResponse,
)
from app.schemas.property_schema import PropertyDetail
from app.schemas.score_schema import ScoreRequest
from app.services.scoring_service import score_property


FORMULA_VERSION = "baseline_v1"


def build_investment_analysis(
    property_detail: PropertyDetail,
    market_context: MarketContextResponse,
    valuation: ValuationResponse,
    risk: RiskAssessmentResponse,
) -> InvestmentAnalysisResponse:
    acquisition_basis = None
    if property_detail.active_listing:
        acquisition_basis = property_detail.active_listing.list_price
    elif property_detail.latest_assessment:
        acquisition_basis = property_detail.latest_assessment.assessed_total_value
    elif property_detail.last_transaction and property_detail.last_transaction.sale_price:
        acquisition_basis = property_detail.last_transaction.sale_price

    if acquisition_basis is None:
        raise ValueError("A listing, assessment, or transaction anchor is required.")

    appreciation_score = min(
        100.0,
        max(0.0, market_context.appreciation_score + (valuation.discount_to_value * 100.0)),
    )

    score_request = ScoreRequest(
        list_price=acquisition_basis,
        acquisition_basis=acquisition_basis,
        estimated_rent=property_detail.estimated_rent or market_context.median_rent,
        taxes_monthly=property_detail.taxes_monthly,
        insurance_monthly=property_detail.insurance_monthly,
        maintenance_monthly=property_detail.maintenance_monthly,
        hoa_monthly=property_detail.hoa_monthly,
        vacancy_reserve_monthly=property_detail.vacancy_reserve_monthly,
        management_cost_monthly=property_detail.management_cost_monthly,
        appreciation_score=appreciation_score,
        market_growth_score=market_context.market_growth_score,
        risk_inverse_score=risk.risk_inverse_score,
        liquidity_score=market_context.liquidity_score,
    )
    scoring_output = score_property(score_request)

    assumptions = list(scoring_output["assumptions"])
    assumptions.extend(valuation.assumptions)
    assumptions.extend(risk.assumptions)
    assumptions.extend(market_context.assumptions)

    return InvestmentAnalysisResponse(
        formula_version=FORMULA_VERSION,
        acquisition_basis=acquisition_basis,
        monthly_cash_flow=scoring_output["monthly_cash_flow"],
        annual_noi=scoring_output["annual_noi"],
        cap_rate=scoring_output["cap_rate"],
        cash_flow_score=scoring_output["cash_flow_score"],
        appreciation_score=round(appreciation_score, 2),
        market_growth_score=market_context.market_growth_score,
        risk_inverse_score=risk.risk_inverse_score,
        liquidity_score=market_context.liquidity_score,
        investment_score=scoring_output["investment_score"],
        assumptions=assumptions,
    )
