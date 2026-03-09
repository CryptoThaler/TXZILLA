from typing import Optional

from app.schemas.analysis_schema import MarketContextResponse
from app.schemas.property_schema import PropertyDetail
from app.services.market_service import MarketService


class MarketIntelligenceAgent:
    name = "market_intelligence_agent"

    def __init__(self, service: Optional[MarketService] = None) -> None:
        self.service = service or MarketService()

    def evaluate(self, property_detail: PropertyDetail) -> MarketContextResponse:
        return self.service.build_market_context(property_detail)
