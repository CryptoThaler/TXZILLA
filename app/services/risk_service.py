from typing import Optional

from app.repositories.risk_repository import RiskRepository
from app.schemas.analysis_schema import RiskAssessmentResponse, RiskLayerResponse
from app.schemas.property_schema import PropertyDetail


RISK_LAYER_WEIGHTS = {
    "flood": 0.40,
    "wildfire": 0.25,
    "drought": 0.20,
    "water_stress": 0.15,
}
PARCEL_CONFIDENCE_PENALTY_FACTOR = 20.0


class RiskService:
    def __init__(self, repository: Optional[RiskRepository] = None) -> None:
        self.repository = repository or RiskRepository()

    def build_risk_assessment(
        self,
        property_detail: PropertyDetail,
    ) -> RiskAssessmentResponse:
        raw_layers = self.repository.list_risk_layers(property_detail.property_id)
        layer_lookup = {layer["risk_layer"]: layer for layer in raw_layers}
        assumptions: list[str] = []
        weighted_score = 0.0

        layers: list[RiskLayerResponse] = []
        for risk_layer, weight in RISK_LAYER_WEIGHTS.items():
            layer = layer_lookup.get(risk_layer)
            if layer is None:
                assumptions.append(f"missing_{risk_layer}_treated_as_zero")
                continue

            weighted_score += weight * float(layer["risk_score"])
            layers.append(
                RiskLayerResponse(
                    risk_layer=layer["risk_layer"],
                    risk_level=layer["risk_level"],
                    risk_score=float(layer["risk_score"]),
                    source_name=layer["source_name"],
                    source_record_id=layer["source_record_id"],
                    effective_date=layer["effective_date"],
                )
            )

        parcel_confidence_penalty = (
            (1.0 - property_detail.parcel_resolution_confidence)
            * PARCEL_CONFIDENCE_PENALTY_FACTOR
        )
        overall_risk_score = min(100.0, weighted_score + parcel_confidence_penalty)
        risk_inverse_score = max(0.0, 100.0 - overall_risk_score)

        return RiskAssessmentResponse(
            overall_risk_score=round(overall_risk_score, 2),
            risk_inverse_score=round(risk_inverse_score, 2),
            parcel_confidence_penalty=round(parcel_confidence_penalty, 2),
            layers=layers,
            assumptions=assumptions,
        )
