from typing import Optional

from app.repositories.seed_data import MARKET_FEATURE_RECORDS, RENTAL_MARKET_RECORDS


class MarketRepository:
    def get_rental_market(
        self,
        region_key: str,
        property_type: str,
        bedroom_count: Optional[int] = None,
    ) -> Optional[dict]:
        exact_match = None

        for record in RENTAL_MARKET_RECORDS:
            if record["region_key"] != region_key or record["property_type"] != property_type:
                continue
            if bedroom_count is not None and record["bedroom_count"] == bedroom_count:
                exact_match = record
                break
            if bedroom_count is None and exact_match is None:
                exact_match = record

        if exact_match:
            return exact_match

        for record in RENTAL_MARKET_RECORDS:
            if record["region_key"] == region_key and record["property_type"] == property_type:
                return record

        return None

    def list_market_features(self, region_key: str) -> list[dict]:
        return [
            feature
            for feature in MARKET_FEATURE_RECORDS
            if feature["region_key"] == region_key
        ]
