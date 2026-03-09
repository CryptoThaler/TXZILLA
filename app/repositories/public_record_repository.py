from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import desc, select, update
from sqlalchemy.engine import Engine

from app.database import get_engine
from app.models.public_record_models import get_public_record_tables


def _decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def _normalize_datetime_input(value):
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def _normalize_date_input(value):
    if isinstance(value, str):
        return date.fromisoformat(value)
    return value


class PublicRecordRepository:
    def __init__(self, engine: Optional[Engine] = None) -> None:
        self.engine = engine or get_engine()
        schema_name = None if self.engine.dialect.name == "sqlite" else "real_estate"
        tables = get_public_record_tables(schema_name)
        self.metadata = tables["metadata"]
        self.properties = tables["properties"]
        self.assessment_history = tables["assessment_history"]
        self.ownership_history = tables["ownership_history"]

    def ensure_storage(self) -> None:
        self.metadata.create_all(self.engine)

    def upsert_properties(self, records: list[dict]) -> int:
        if not records:
            return 0

        self.ensure_storage()
        now = datetime.now(timezone.utc)
        count = 0
        with self.engine.begin() as connection:
            for record in records:
                property_id = record["property_id"]
                existing = connection.execute(
                    select(self.properties.c.property_id).where(
                        self.properties.c.property_id == property_id
                    )
                ).first()
                payload = {
                    "property_id": property_id,
                    "parcel_number": record["parcel_number"],
                    "county": record["county"],
                    "region_key": record.get("region_key"),
                    "property_type": record.get("property_type", "single_family"),
                    "address_line1": record["address_line1"],
                    "city": record["city"],
                    "state": record.get("state", "TX"),
                    "postal_code": record.get("postal_code"),
                    "latitude": record["latitude"],
                    "longitude": record["longitude"],
                    "bedrooms": record.get("bedrooms"),
                    "bathrooms": record.get("bathrooms"),
                    "building_area_sqft": record.get("building_area_sqft"),
                    "lot_size_acres": record.get("lot_size_acres"),
                    "estimated_rent": record.get("estimated_rent"),
                    "taxes_monthly": record.get("taxes_monthly", 0.0),
                    "insurance_monthly": record.get("insurance_monthly", 0.0),
                    "maintenance_monthly": record.get("maintenance_monthly", 0.0),
                    "hoa_monthly": record.get("hoa_monthly", 0.0),
                    "vacancy_reserve_monthly": record.get("vacancy_reserve_monthly", 0.0),
                    "management_cost_monthly": record.get("management_cost_monthly", 0.0),
                    "zoning_code": record.get("zoning_code"),
                    "land_use_code": record.get("land_use_code"),
                    "parcel_resolution_confidence": record.get(
                        "parcel_resolution_confidence",
                        1.0,
                    ),
                    "source_name": record["source_name"],
                    "source_record_id": record["source_record_id"],
                    "source_observed_at": _normalize_datetime_input(
                        record["source_observed_at"]
                    ),
                    "source_fetched_at": _normalize_datetime_input(
                        record["source_fetched_at"]
                    ),
                    "updated_at": now,
                }

                if existing:
                    connection.execute(
                        update(self.properties)
                        .where(self.properties.c.property_id == property_id)
                        .values(**payload)
                    )
                else:
                    payload["created_at"] = now
                    connection.execute(self.properties.insert().values(**payload))
                count += 1
        return count

    def insert_assessment_history(self, records: list[dict]) -> int:
        if not records:
            return 0

        self.ensure_storage()
        now = datetime.now(timezone.utc)
        payloads = [
            {
                "assessment_id": str(uuid4()),
                "property_id": record["property_id"],
                "tax_year": record["tax_year"],
                "assessed_total_value": record["assessed_total_value"],
                "assessed_land_value": record.get("assessed_land_value"),
                "assessed_improvement_value": record.get("assessed_improvement_value"),
                "taxable_value": record.get("taxable_value"),
                "tax_amount_annual": record.get("tax_amount_annual"),
                "source_name": record["source_name"],
                "source_record_id": record["source_record_id"],
                "source_observed_at": _normalize_datetime_input(record["source_observed_at"]),
                "created_at": now,
            }
            for record in records
        ]
        with self.engine.begin() as connection:
            connection.execute(self.assessment_history.insert(), payloads)
        return len(payloads)

    def insert_ownership_history(self, records: list[dict]) -> int:
        if not records:
            return 0

        self.ensure_storage()
        now = datetime.now(timezone.utc)
        payloads = [
            {
                "ownership_id": str(uuid4()),
                "property_id": record["property_id"],
                "owner_name": record["owner_name"],
                "ownership_start_date": _normalize_date_input(record.get("ownership_start_date")),
                "ownership_end_date": _normalize_date_input(record.get("ownership_end_date")),
                "mailing_address": record.get("mailing_address"),
                "source_name": record["source_name"],
                "source_record_id": record["source_record_id"],
                "source_observed_at": _normalize_datetime_input(record["source_observed_at"]),
                "created_at": now,
            }
            for record in records
        ]
        with self.engine.begin() as connection:
            connection.execute(self.ownership_history.insert(), payloads)
        return len(payloads)

    def list_properties(self) -> list[dict]:
        self.ensure_storage()
        with self.engine.begin() as connection:
            rows = connection.execute(select(self.properties)).mappings()
            return [self._coerce_row(dict(row)) for row in rows]

    def get_property(self, property_id: str) -> Optional[dict]:
        self.ensure_storage()
        with self.engine.begin() as connection:
            row = connection.execute(
                select(self.properties).where(self.properties.c.property_id == property_id)
            ).mappings().first()
            if row is None:
                return None

            property_record = self._coerce_row(dict(row))
            property_record["latest_assessment"] = self.get_latest_assessment(property_id)
            property_record["ownership_history"] = self.list_ownership_history(property_id)
            return property_record

    def get_latest_assessment(self, property_id: str) -> Optional[dict]:
        self.ensure_storage()
        with self.engine.begin() as connection:
            row = connection.execute(
                select(self.assessment_history)
                .where(self.assessment_history.c.property_id == property_id)
                .order_by(desc(self.assessment_history.c.tax_year))
                .limit(1)
            ).mappings().first()
            return self._coerce_row(dict(row)) if row else None

    def list_ownership_history(self, property_id: str) -> list[dict]:
        self.ensure_storage()
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(self.ownership_history)
                .where(self.ownership_history.c.property_id == property_id)
                .order_by(desc(self.ownership_history.c.source_observed_at))
            ).mappings()
            return [self._coerce_row(dict(row)) for row in rows]

    def _coerce_row(self, row: dict) -> dict:
        coerced = {}
        for key, value in row.items():
            value = _decimal_to_float(value)
            if isinstance(value, (datetime, date)):
                coerced[key] = value.isoformat()
            else:
                coerced[key] = value
        return coerced
