from typing import Optional

from app.repositories.market_repository import MarketRepository
from app.schemas.analysis_schema import MarketContextResponse, MarketFeatureValue
from app.schemas.property_schema import PropertyDetail


DEFAULT_APPRECIATION_SCORE = 50.0
DEFAULT_MARKET_GROWTH_SCORE = 50.0
DEFAULT_LIQUIDITY_SCORE = 50.0
DEFAULT_TARGET_CAP_RATE = 0.065
DEFAULT_MARKET_GROWTH_RATE = 0.03


class MarketService:
    def __init__(self, repository: Optional[MarketRepository] = None) -> None:
        self.repository = repository or MarketRepository()

    def build_market_context(self, property_detail: PropertyDetail) -> MarketContextResponse:
        bedroom_count = (
            int(property_detail.bedrooms) if property_detail.bedrooms is not None else None
        )
        rental_market = self.repository.get_rental_market(
            region_key=property_detail.region_key,
            property_type=property_detail.property_type,
            bedroom_count=bedroom_count,
        )
        features = self.repository.list_market_features(property_detail.region_key)

        feature_lookup = {feature["feature_name"]: feature["feature_value"] for feature in features}
        assumptions: list[str] = []

        if not rental_market:
            assumptions.append("rental_market_missing_defaulted")

        appreciation_score = feature_lookup.get(
            "appreciation_score",
            DEFAULT_APPRECIATION_SCORE,
        )
        market_growth_score = feature_lookup.get(
            "market_growth_score",
            DEFAULT_MARKET_GROWTH_SCORE,
        )
        liquidity_score = feature_lookup.get("liquidity_score", DEFAULT_LIQUIDITY_SCORE)
        target_cap_rate = feature_lookup.get("target_cap_rate", DEFAULT_TARGET_CAP_RATE)
        market_growth_rate = feature_lookup.get(
            "market_growth_rate",
            DEFAULT_MARKET_GROWTH_RATE,
        )

        if "appreciation_score" not in feature_lookup:
            assumptions.append("appreciation_score_defaulted")
        if "market_growth_score" not in feature_lookup:
            assumptions.append("market_growth_score_defaulted")
        if "liquidity_score" not in feature_lookup:
            assumptions.append("liquidity_score_defaulted")
        if "target_cap_rate" not in feature_lookup:
            assumptions.append("target_cap_rate_defaulted")
        if "market_growth_rate" not in feature_lookup:
            assumptions.append("market_growth_rate_defaulted")

        median_rent = (
            rental_market["median_rent"]
            if rental_market
            else property_detail.estimated_rent or 0.0
        )
        vacancy_rate = rental_market["vacancy_rate"] if rental_market else None
        growth_yoy = rental_market["growth_yoy"] if rental_market else None

        return MarketContextResponse(
            region_key=property_detail.region_key,
            property_type=property_detail.property_type,
            bedroom_count=bedroom_count,
            median_rent=median_rent,
            vacancy_rate=vacancy_rate,
            growth_yoy=growth_yoy,
            appreciation_score=round(appreciation_score, 2),
            market_growth_score=round(market_growth_score, 2),
            liquidity_score=round(liquidity_score, 2),
            target_cap_rate=round(target_cap_rate, 4),
            market_growth_rate=round(market_growth_rate, 4),
            features=[
                MarketFeatureValue(
                    feature_name=feature["feature_name"],
                    feature_value=feature["feature_value"],
                    value_unit=feature["value_unit"],
                    effective_date=feature["effective_date"],
                )
                for feature in features
            ],
            assumptions=assumptions,
        )
