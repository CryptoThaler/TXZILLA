from app.schemas.analysis_schema import MarketContextResponse, ValuationResponse
from app.schemas.property_schema import PropertyDetail
from app.services.valuation_service import build_valuation


class ValuationAgent:
    name = "valuation_agent"

    def evaluate(
        self,
        property_detail: PropertyDetail,
        market_context: MarketContextResponse,
    ) -> ValuationResponse:
        return build_valuation(property_detail, market_context)
