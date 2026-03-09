from app.schemas.analysis_schema import (
    InvestmentAnalysisResponse,
    MarketContextResponse,
    RiskAssessmentResponse,
    ValuationResponse,
)
from app.schemas.property_schema import PropertyDetail
from app.services.investment_service import build_investment_analysis


class InvestmentAgent:
    name = "investment_agent"

    def evaluate(
        self,
        property_detail: PropertyDetail,
        market_context: MarketContextResponse,
        valuation: ValuationResponse,
        risk: RiskAssessmentResponse,
    ) -> InvestmentAnalysisResponse:
        return build_investment_analysis(property_detail, market_context, valuation, risk)
