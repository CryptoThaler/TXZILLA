from app.schemas.analysis_schema import LandTransitionResponse
from app.schemas.property_schema import PropertyDetail
from app.services.land_transition_service import build_land_transition_assessment


class LandTransitionAgent:
    name = "land_transition_agent"

    def evaluate(self, property_detail: PropertyDetail) -> LandTransitionResponse:
        return build_land_transition_assessment(property_detail)
