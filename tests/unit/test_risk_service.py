from app.services.property_service import PropertyService
from app.services.risk_service import RiskService


def test_risk_service_uses_weighted_layers_and_confidence_penalty():
    property_detail = PropertyService().get_property_detail("prop-bexar-001")
    assert property_detail is not None

    assessment = RiskService().build_risk_assessment(property_detail)

    assert assessment.parcel_confidence_penalty == 0.4
    assert assessment.overall_risk_score == 24.2
    assert assessment.risk_inverse_score == 75.8
    assert len(assessment.layers) == 4
