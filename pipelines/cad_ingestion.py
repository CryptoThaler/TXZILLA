from typing import Iterable
from uuid import uuid5, NAMESPACE_URL

from pipelines.county_adapters import get_county_adapter


def build_property_id(county: str, parcel_number: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"txzilla:{county.lower()}:{parcel_number}"))


def standardize_cad_record(raw_record: dict, fetched_at: str) -> dict:
    return {
        "property_id": build_property_id(raw_record["county"], raw_record["parcel_number"]),
        "source_name": raw_record["source_name"],
        "source_record_id": raw_record["source_record_id"],
        "county": raw_record["county"],
        "parcel_number": raw_record["parcel_number"],
        "address_line1": raw_record["address"],
        "city": raw_record["city"],
        "state": raw_record.get("state", "TX"),
        "postal_code": raw_record.get("postal_code"),
        "latitude": float(raw_record["latitude"]),
        "longitude": float(raw_record["longitude"]),
        "property_type": raw_record.get("property_type", "single_family"),
        "bedrooms": raw_record.get("bedrooms"),
        "bathrooms": raw_record.get("bathrooms"),
        "building_area_sqft": raw_record.get("building_area_sqft"),
        "lot_size_acres": raw_record.get("lot_size_acres"),
        "estimated_rent": raw_record.get("estimated_rent"),
        "taxes_monthly": raw_record.get("taxes_monthly", 0.0),
        "insurance_monthly": raw_record.get("insurance_monthly", 0.0),
        "maintenance_monthly": raw_record.get("maintenance_monthly", 0.0),
        "hoa_monthly": raw_record.get("hoa_monthly", 0.0),
        "vacancy_reserve_monthly": raw_record.get("vacancy_reserve_monthly", 0.0),
        "management_cost_monthly": raw_record.get("management_cost_monthly", 0.0),
        "zoning_code": raw_record.get("zoning_code"),
        "land_use_code": raw_record.get("land_use_code"),
        "owner_name": raw_record.get("owner_name"),
        "ownership_start_date": raw_record.get("ownership_start_date"),
        "mailing_address": raw_record.get("mailing_address"),
        "tax_year": raw_record.get("tax_year"),
        "assessed_total_value": raw_record.get("assessed_total_value"),
        "assessed_land_value": raw_record.get("assessed_land_value"),
        "assessed_improvement_value": raw_record.get("assessed_improvement_value"),
        "taxable_value": raw_record.get("taxable_value"),
        "tax_amount_annual": raw_record.get("tax_amount_annual"),
        "parcel_resolution_confidence": raw_record.get("parcel_resolution_confidence", 1.0),
        "source_observed_at": raw_record["source_observed_at"],
        "source_fetched_at": fetched_at,
        "raw_lineage": {
            "layer": "raw",
            "payload": raw_record,
        },
    }


def prepare_cad_record(raw_record: dict) -> dict:
    county = raw_record.get("county")
    if county:
        adapter = get_county_adapter(str(county))
        if adapter is not None:
            return adapter.normalize_record(raw_record)
    return raw_record


def curate_cad_record(standardized_record: dict, region_key: str) -> dict:
    curated = dict(standardized_record)
    curated["region_key"] = region_key
    curated["curation_layer"] = "curated"
    return curated


def ingest_cad(records: Iterable[dict], fetched_at: str, region_key: str) -> dict:
    raw_records = list(records)
    standardized_records = [
        standardize_cad_record(
            prepare_cad_record(record),
            fetched_at=fetched_at,
        )
        for record in raw_records
    ]
    curated_records = [
        curate_cad_record(record, region_key=region_key) for record in standardized_records
    ]
    return {
        "raw": raw_records,
        "standardized": standardized_records,
        "curated": curated_records,
    }
