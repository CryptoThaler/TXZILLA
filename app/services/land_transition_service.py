from app.schemas.analysis_schema import LandTransitionResponse
from app.schemas.property_schema import PropertyDetail


def build_land_transition_assessment(property_detail: PropertyDetail) -> LandTransitionResponse:
    assumptions: list[str] = []

    utility_access_score = 60.0
    for feature in property_detail.land_features:
        if feature.feature_name == "utility_access_score" and feature.feature_value is not None:
            utility_access_score = feature.feature_value
            break

    if property_detail.lot_size_acres is None:
        assumptions.append("lot_size_missing_defaulted")
        acreage_score = 25.0
    else:
        acreage_score = min(100.0, property_detail.lot_size_acres * 100.0)

    zoning_bonus = 10.0 if property_detail.zoning_code and property_detail.zoning_code.startswith("SF") else 0.0
    transition_score = min(
        100.0,
        round(0.5 * utility_access_score + 0.35 * acreage_score + zoning_bonus, 2),
    )

    strategy = "hold"
    if transition_score >= 70:
        strategy = "redevelop"
    elif transition_score >= 55:
        strategy = "gentle_density"

    return LandTransitionResponse(
        transition_score=transition_score,
        strategy=strategy,
        assumptions=assumptions,
    )
