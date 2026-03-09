from typing import Iterable


def standardize_mls_record(raw_record: dict, fetched_at: str) -> dict:
    return {
        "source_name": raw_record["source_name"],
        "source_record_id": raw_record["source_record_id"],
        "parcel_number": raw_record.get("parcel_number"),
        "county": raw_record["county"],
        "address_line1": raw_record["address"],
        "city": raw_record["city"],
        "listing_status": raw_record["listing_status"],
        "list_price": float(raw_record["list_price"]),
        "listed_at": raw_record["listed_at"],
        "removed_at": raw_record.get("removed_at"),
        "days_on_market": raw_record.get("days_on_market"),
        "bedrooms": raw_record.get("bedrooms"),
        "bathrooms": raw_record.get("bathrooms"),
        "building_area_sqft": raw_record.get("building_area_sqft"),
        "lot_size_acres": raw_record.get("lot_size_acres"),
        "source_observed_at": raw_record["source_observed_at"],
        "source_fetched_at": fetched_at,
        "raw_lineage": {
            "layer": "raw",
            "payload": raw_record,
        },
    }


def curate_mls_record(standardized_record: dict, property_id: str) -> dict:
    curated = dict(standardized_record)
    curated["property_id"] = property_id
    curated["curation_layer"] = "curated"
    return curated


def ingest_mls(records: Iterable[dict], fetched_at: str) -> dict:
    raw_records = list(records)
    standardized_records = [
        standardize_mls_record(record, fetched_at=fetched_at) for record in raw_records
    ]
    return {
        "raw": raw_records,
        "standardized": standardized_records,
    }
