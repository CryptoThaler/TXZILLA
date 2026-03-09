from functools import lru_cache
from typing import Optional

from sqlalchemy import Column, Date, DateTime, Float, Integer, MetaData, Numeric, String, Table, Text


@lru_cache(maxsize=4)
def get_public_record_tables(schema_name: Optional[str]) -> dict[str, Table]:
    metadata = MetaData(schema=schema_name)

    properties = Table(
        "properties",
        metadata,
        Column("property_id", String(64), primary_key=True),
        Column("parcel_number", Text, nullable=False),
        Column("county", Text, nullable=False),
        Column("region_key", Text, nullable=True),
        Column("property_type", Text, nullable=False),
        Column("address_line1", Text, nullable=False),
        Column("city", Text, nullable=False),
        Column("state", String(2), nullable=False),
        Column("postal_code", Text, nullable=True),
        Column("latitude", Float, nullable=False),
        Column("longitude", Float, nullable=False),
        Column("bedrooms", Float, nullable=True),
        Column("bathrooms", Float, nullable=True),
        Column("building_area_sqft", Float, nullable=True),
        Column("lot_size_acres", Float, nullable=True),
        Column("estimated_rent", Numeric(12, 2), nullable=True),
        Column("taxes_monthly", Numeric(12, 2), nullable=False),
        Column("insurance_monthly", Numeric(12, 2), nullable=False),
        Column("maintenance_monthly", Numeric(12, 2), nullable=False),
        Column("hoa_monthly", Numeric(12, 2), nullable=False),
        Column("vacancy_reserve_monthly", Numeric(12, 2), nullable=False),
        Column("management_cost_monthly", Numeric(12, 2), nullable=False),
        Column("zoning_code", Text, nullable=True),
        Column("land_use_code", Text, nullable=True),
        Column("parcel_resolution_confidence", Numeric(4, 3), nullable=False),
        Column("source_name", Text, nullable=False),
        Column("source_record_id", Text, nullable=False),
        Column("source_observed_at", DateTime(timezone=True), nullable=False),
        Column("source_fetched_at", DateTime(timezone=True), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
        Column("updated_at", DateTime(timezone=True), nullable=False),
    )

    assessment_history = Table(
        "assessment_history",
        metadata,
        Column("assessment_id", String(36), primary_key=True),
        Column("property_id", String(64), nullable=False),
        Column("tax_year", Integer, nullable=False),
        Column("assessed_total_value", Numeric(14, 2), nullable=False),
        Column("assessed_land_value", Numeric(14, 2), nullable=True),
        Column("assessed_improvement_value", Numeric(14, 2), nullable=True),
        Column("taxable_value", Numeric(14, 2), nullable=True),
        Column("tax_amount_annual", Numeric(14, 2), nullable=True),
        Column("source_name", Text, nullable=False),
        Column("source_record_id", Text, nullable=False),
        Column("source_observed_at", DateTime(timezone=True), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )

    ownership_history = Table(
        "ownership_history",
        metadata,
        Column("ownership_id", String(36), primary_key=True),
        Column("property_id", String(64), nullable=False),
        Column("owner_name", Text, nullable=False),
        Column("ownership_start_date", Date, nullable=True),
        Column("ownership_end_date", Date, nullable=True),
        Column("mailing_address", Text, nullable=True),
        Column("source_name", Text, nullable=False),
        Column("source_record_id", Text, nullable=False),
        Column("source_observed_at", DateTime(timezone=True), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )

    return {
        "metadata": metadata,
        "properties": properties,
        "assessment_history": assessment_history,
        "ownership_history": ownership_history,
    }
