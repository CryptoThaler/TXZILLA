from fastapi import APIRouter, Body, HTTPException

from app.schemas.county_adapter_schema import CountyAdapterResponse
from app.schemas.county_execution_schema import (
    CountyManifestInspectRequest,
    CountyManifestInspectResponse,
    CountyPrepareRequest,
    CountyPrepareResponse,
)
from app.schemas.county_pipeline_schema import CountyPipelinePlanResponse
from app.schemas.county_sync_schema import CountySyncRequest, CountySyncResponse
from app.services.county_adapter_service import (
    get_county_pipeline_plan,
    get_supported_county,
    list_county_pipeline_plans,
    list_supported_counties,
)
from app.services.county_execution_service import (
    inspect_county_manifest,
    prepare_county_ingestion_request,
)
from app.services.county_sync_service import CountySyncService


router = APIRouter(tags=["counties"])
sync_service = CountySyncService()


@router.get("/counties/adapters", response_model=list[CountyAdapterResponse])
def get_county_adapters() -> list[CountyAdapterResponse]:
    return list_supported_counties()


@router.get("/counties/adapters/{county}", response_model=CountyAdapterResponse)
def get_county_adapter(county: str) -> CountyAdapterResponse:
    adapter = get_supported_county(county)
    if adapter is None:
        raise HTTPException(status_code=404, detail="County adapter not found")
    return adapter


@router.get("/counties/pipelines", response_model=list[CountyPipelinePlanResponse])
def get_county_pipeline_plans() -> list[CountyPipelinePlanResponse]:
    return list_county_pipeline_plans()


@router.get("/counties/pipelines/{county}", response_model=CountyPipelinePlanResponse)
def get_county_pipeline(county: str) -> CountyPipelinePlanResponse:
    plan = get_county_pipeline_plan(county)
    if plan is None:
        raise HTTPException(status_code=404, detail="County pipeline not found")
    return plan


@router.post(
    "/counties/pipelines/{county}/inspect-manifest",
    response_model=CountyManifestInspectResponse,
)
def inspect_pipeline_manifest(
    county: str,
    request: CountyManifestInspectRequest,
) -> CountyManifestInspectResponse:
    try:
        return inspect_county_manifest(
            county=county,
            html=request.html,
            source_url=request.source_url,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/counties/pipelines/{county}/prepare-ingestion",
    response_model=CountyPrepareResponse,
)
def prepare_pipeline_ingestion(
    county: str,
    request: CountyPrepareRequest,
) -> CountyPrepareResponse:
    try:
        return prepare_county_ingestion_request(county=county, request=request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/counties/pipelines/{county}/run-sync",
    response_model=CountySyncResponse,
)
def run_pipeline_sync(
    county: str,
    request: CountySyncRequest = Body(default_factory=CountySyncRequest),
) -> CountySyncResponse:
    try:
        return sync_service.run(county=county, request=request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
