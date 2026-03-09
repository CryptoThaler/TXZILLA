from datetime import datetime, timezone
from typing import Optional

from app.schemas.provider_schema import ProviderIngestionRequest
from pipelines.county_adapters import get_county_adapter
from pipelines.county_pipeline import build_county_pipeline_plan


def build_provider_request_from_county_export(
    county: str,
    dataset_key: str,
    rows: list[dict],
    source_observed_at: str,
    provider_name: Optional[str] = None,
    fetched_at: Optional[datetime] = None,
) -> ProviderIngestionRequest:
    adapter = get_county_adapter(county)
    plan = build_county_pipeline_plan(county)
    if adapter is None or plan is None:
        raise ValueError(f"Unsupported county pipeline: {county}")

    dataset_keys = {dataset.dataset_key for dataset in plan.datasets}
    if dataset_key not in dataset_keys:
        raise ValueError(f"{county} dataset not configured: {dataset_key}")

    normalized_records: list[dict] = []
    for row in rows:
        prepared = dict(row)
        prepared.setdefault("county", adapter.spec.county)
        prepared.setdefault("source_observed_at", source_observed_at)
        prepared.setdefault("source_name", provider_name or dataset_key)
        prepared.setdefault(
            "source_record_id",
            row.get("source_record_id")
            or row.get("prop_id")
            or row.get("acct")
            or row.get("account")
            or row.get("parcel_number"),
        )
        normalized_records.append(adapter.normalize_record(prepared))

    return ProviderIngestionRequest(
        provider_name=provider_name or dataset_key,
        provider_type="cad",
        region_key=plan.region_key,
        fetched_at=fetched_at or datetime.now(timezone.utc),
        metadata={
            "county": adapter.spec.county,
            "dataset_key": dataset_key,
            "execution_mode": "bulk_export",
        },
        records=normalized_records,
    )
