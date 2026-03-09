from typing import Optional

from app.schemas.analysis_schema import RiskAssessmentResponse
from app.schemas.property_schema import PropertyDetail
from app.services.risk_service import RiskService


class RiskAgent:
    name = "risk_agent"

    def __init__(self, service: Optional[RiskService] = None) -> None:
        self.service = service or RiskService()

    def evaluate(self, property_detail: PropertyDetail) -> RiskAssessmentResponse:
        return self.service.build_risk_assessment(property_detail)
