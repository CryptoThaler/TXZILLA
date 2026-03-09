from typing import Optional

from app.schemas.analysis_schema import PropertyAnalysisReport
from app.services.investment_service import build_investment_analysis
from app.services.land_transition_service import build_land_transition_assessment
from app.services.market_service import MarketService
from app.services.property_service import PropertyService
from app.services.risk_service import RiskService
from app.services.valuation_service import build_valuation


class ReportService:
    def __init__(
        self,
        property_service: Optional[PropertyService] = None,
        market_service: Optional[MarketService] = None,
        risk_service: Optional[RiskService] = None,
    ) -> None:
        self.property_service = property_service or PropertyService()
        self.market_service = market_service or MarketService()
        self.risk_service = risk_service or RiskService()

    def build_property_report(self, property_id: str) -> PropertyAnalysisReport:
        property_detail = self.property_service.get_property_detail(property_id)
        if property_detail is None:
            raise ValueError("Property not found")

        market_context = self.market_service.build_market_context(property_detail)
        valuation = build_valuation(property_detail, market_context)
        risk = self.risk_service.build_risk_assessment(property_detail)
        land_transition = build_land_transition_assessment(property_detail)
        investment = build_investment_analysis(
            property_detail=property_detail,
            market_context=market_context,
            valuation=valuation,
            risk=risk,
        )

        return PropertyAnalysisReport(
            property=property_detail,
            market=market_context,
            valuation=valuation,
            risk=risk,
            land_transition=land_transition,
            investment=investment,
        )
