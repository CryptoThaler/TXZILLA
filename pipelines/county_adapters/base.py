from dataclasses import asdict, dataclass, field
from typing import Any


CANONICAL_CAD_FIELDS = (
    "source_name",
    "source_record_id",
    "county",
    "parcel_number",
    "address",
    "city",
    "state",
    "postal_code",
    "latitude",
    "longitude",
    "property_type",
    "bedrooms",
    "bathrooms",
    "building_area_sqft",
    "lot_size_acres",
    "estimated_rent",
    "taxes_monthly",
    "insurance_monthly",
    "maintenance_monthly",
    "hoa_monthly",
    "vacancy_reserve_monthly",
    "management_cost_monthly",
    "zoning_code",
    "land_use_code",
    "owner_name",
    "ownership_start_date",
    "mailing_address",
    "tax_year",
    "assessed_total_value",
    "assessed_land_value",
    "assessed_improvement_value",
    "taxable_value",
    "tax_amount_annual",
    "parcel_resolution_confidence",
    "source_observed_at",
)


@dataclass(frozen=True)
class CountySource:
    label: str
    url: str
    access_method: str
    format: str
    priority: int
    notes: str


@dataclass(frozen=True)
class CountyProcedureStep:
    order: int
    title: str
    description: str
    gate: str


@dataclass(frozen=True)
class CountyAdapterSpec:
    county: str
    display_name: str
    region_key: str
    bulk_sources: list[CountySource] = field(default_factory=list)
    clerk_sources: list[CountySource] = field(default_factory=list)
    procedure: list[CountyProcedureStep] = field(default_factory=list)
    field_aliases: dict[str, list[str]] = field(default_factory=dict)
    required_exact_fields: list[str] = field(default_factory=lambda: ["parcel_number"])
    formalization_strategy: list[str] = field(default_factory=list)
    refresh_cad: str = "daily"
    refresh_clerk: str = "weekly"

    def to_dict(self) -> dict[str, Any]:
        return {
            "county": self.county,
            "display_name": self.display_name,
            "region_key": self.region_key,
            "bulk_sources": [asdict(source) for source in self.bulk_sources],
            "clerk_sources": [asdict(source) for source in self.clerk_sources],
            "procedure": [asdict(step) for step in self.procedure],
            "field_aliases": self.field_aliases,
            "required_exact_fields": self.required_exact_fields,
            "formalization_strategy": self.formalization_strategy,
            "refresh_cad": self.refresh_cad,
            "refresh_clerk": self.refresh_clerk,
        }


class CountyAdapter:
    spec: CountyAdapterSpec

    def normalize_record(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}

        for canonical_field in CANONICAL_CAD_FIELDS:
            if canonical_field in raw_record:
                normalized[canonical_field] = raw_record[canonical_field]
                continue

            for alias in self.spec.field_aliases.get(canonical_field, []):
                if alias in raw_record:
                    normalized[canonical_field] = raw_record[alias]
                    break

        normalized.setdefault("county", self.spec.county)
        normalized.setdefault("state", "TX")

        missing_exact_fields = [
            field_name
            for field_name in self.spec.required_exact_fields
            if not normalized.get(field_name)
        ]
        if missing_exact_fields:
            raise ValueError(
                f"{self.spec.county} input missing exact-match fields: "
                + ", ".join(missing_exact_fields)
            )

        return normalized

    def describe(self) -> dict[str, Any]:
        return self.spec.to_dict()
