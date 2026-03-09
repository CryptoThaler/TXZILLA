from typing import Optional

from app.schemas.county_execution_schema import (
    CountyManifestInspectResponse,
    CountyPrepareRequest,
    CountyPrepareResponse,
)
from pipelines.county_manifest import build_manifest_snapshot
from pipelines.county_procedures import build_provider_request_from_county_export


def inspect_county_manifest(
    county: str,
    html: str,
    source_url: Optional[str] = None,
) -> CountyManifestInspectResponse:
    snapshot = build_manifest_snapshot(county=county, html=html, source_url=source_url)
    return CountyManifestInspectResponse(**snapshot.to_dict())


def prepare_county_ingestion_request(county: str, request: CountyPrepareRequest) -> CountyPrepareResponse:
    provider_request = build_provider_request_from_county_export(
        county=county,
        dataset_key=request.dataset_key,
        rows=request.rows,
        source_observed_at=request.source_observed_at,
        provider_name=request.provider_name,
    )
    return CountyPrepareResponse(request=provider_request)
