from app.schemas.analysis_schema import (
    InvestmentAnalysisResponse,
    LandTransitionResponse,
    MarketContextResponse,
    PropertyAnalysisReport,
    RiskAssessmentResponse,
    ValuationResponse,
)
from app.schemas.property_schema import PropertyDetail


class ReportAgent:
    name = "report_agent"

    def compile(
        self,
        property_detail: PropertyDetail,
        market_context: MarketContextResponse,
        valuation: ValuationResponse,
        risk: RiskAssessmentResponse,
        investment: InvestmentAnalysisResponse,
        land_transition: LandTransitionResponse,
    ) -> PropertyAnalysisReport:
        return PropertyAnalysisReport(
            property=property_detail,
            market=market_context,
            valuation=valuation,
            risk=risk,
            land_transition=land_transition,
            investment=investment,
        )
