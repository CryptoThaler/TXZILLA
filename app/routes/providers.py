from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.provider_schema import (
    ProviderArtifactSummary,
    ProviderIngestionRequest,
    ProviderIngestionResponse,
    ProviderRunSummary,
)
from app.services.provider_ingestion_service import ProviderIngestionService


router = APIRouter(tags=["providers"])
service = ProviderIngestionService()


@router.post("/providers/ingest", response_model=ProviderIngestionResponse)
def ingest_provider_payload(request: ProviderIngestionRequest) -> ProviderIngestionResponse:
    return service.ingest(request)


@router.get("/providers/runs", response_model=list[ProviderRunSummary])
def list_provider_runs(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[ProviderRunSummary]:
    return service.list_runs(limit=limit)


@router.get("/providers/runs/{provider_run_id}/artifacts", response_model=list[ProviderArtifactSummary])
def list_provider_run_artifacts(provider_run_id: str) -> list[ProviderArtifactSummary]:
    return service.list_run_artifacts(provider_run_id=provider_run_id)


@router.get("/providers/artifacts", response_model=list[ProviderArtifactSummary])
def list_provider_artifacts(
    limit: int = Query(default=20, ge=1, le=100),
    county: Optional[str] = Query(default=None),
    dataset_key: Optional[str] = Query(default=None),
) -> list[ProviderArtifactSummary]:
    return service.list_artifacts(limit=limit, county=county, dataset_key=dataset_key)
