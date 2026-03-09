from typing import Optional

from app.repositories.public_record_repository import PublicRecordRepository
from app.repositories.seed_data import (
    LAND_FEATURE_RECORDS,
    LISTING_RECORDS,
    PROPERTY_RECORDS,
    TRANSACTION_RECORDS,
)


class PropertyRepository:
    def __init__(
        self,
        public_record_repository: Optional[PublicRecordRepository] = None,
    ) -> None:
        self.public_record_repository = public_record_repository or PublicRecordRepository()

    def list_property_catalog(self) -> list[dict]:
        public_records = {
            record["property_id"]: record
            for record in self.public_record_repository.list_properties()
        }
        merged = {record["property_id"]: dict(record) for record in PROPERTY_RECORDS}
        merged.update(public_records)
        return list(merged.values())

    def list_properties(
        self,
        query: Optional[str] = None,
        county: Optional[str] = None,
        city: Optional[str] = None,
        region_key: Optional[str] = None,
        max_list_price: Optional[float] = None,
        limit: int = 20,
    ) -> list[dict]:
        lowered_query = query.lower() if query else None
        results: list[dict] = []
        property_catalog = self.list_property_catalog()
        for property_record in property_catalog:
            listing = self.get_active_listing(property_record["property_id"])
            latest_assessment = self.public_record_repository.get_latest_assessment(
                property_record["property_id"]
            )

            if lowered_query:
                haystack = " ".join(
                    [
                        property_record["address_line1"],
                        property_record["city"],
                        property_record["county"],
                    ]
                ).lower()
                if lowered_query not in haystack:
                    continue

            if county and property_record["county"].lower() != county.lower():
                continue
            if city and property_record["city"].lower() != city.lower():
                continue
            if region_key and property_record["region_key"] != region_key:
                continue
            if max_list_price is not None:
                comparable_value = None
                if listing:
                    comparable_value = listing["list_price"]
                elif latest_assessment:
                    comparable_value = latest_assessment["assessed_total_value"]
                if comparable_value is None or comparable_value > max_list_price:
                    continue

            results.append(
                self._build_property_summary(
                    property_record,
                    listing,
                    latest_assessment,
                )
            )

        return results[:limit]

    def get_property(self, property_id: str) -> Optional[dict]:
        public_record = self.public_record_repository.get_property(property_id)
        if public_record:
            detail = dict(public_record)
            detail["active_listing"] = self.get_active_listing(property_id)
            detail["last_transaction"] = self.get_latest_transaction(property_id)
            detail["land_features"] = self.list_land_features(property_id)
            return detail

        for property_record in PROPERTY_RECORDS:
            if property_record["property_id"] != property_id:
                continue

            detail = dict(property_record)
            detail["active_listing"] = self.get_active_listing(property_id)
            detail["last_transaction"] = self.get_latest_transaction(property_id)
            detail["land_features"] = self.list_land_features(property_id)
            detail["latest_assessment"] = None
            detail["ownership_history"] = []
            return detail

        return None

    def get_active_listing(self, property_id: str) -> Optional[dict]:
        matches = [
            listing
            for listing in LISTING_RECORDS
            if listing["property_id"] == property_id and listing["listing_status"] == "active"
        ]
        if not matches:
            return None
        return sorted(matches, key=lambda item: item["listed_at"], reverse=True)[0]

    def get_latest_transaction(self, property_id: str) -> Optional[dict]:
        matches = [
            transaction
            for transaction in TRANSACTION_RECORDS
            if transaction["property_id"] == property_id
        ]
        if not matches:
            return None
        return sorted(matches, key=lambda item: item["recorded_date"], reverse=True)[0]

    def list_land_features(self, property_id: str) -> list[dict]:
        return [
            feature
            for feature in LAND_FEATURE_RECORDS
            if feature["property_id"] == property_id
        ]

    def _build_property_summary(
        self,
        property_record: dict,
        listing: Optional[dict],
        latest_assessment: Optional[dict],
    ) -> dict:
        return {
            "property_id": property_record["property_id"],
            "address_line1": property_record["address_line1"],
            "city": property_record["city"],
            "county": property_record["county"],
            "region_key": property_record["region_key"],
            "property_type": property_record["property_type"],
            "bedrooms": property_record["bedrooms"],
            "bathrooms": property_record["bathrooms"],
            "building_area_sqft": property_record["building_area_sqft"],
            "estimated_rent": property_record["estimated_rent"],
            "active_listing": listing,
            "latest_assessment": latest_assessment,
        }
