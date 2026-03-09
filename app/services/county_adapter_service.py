from typing import Optional

from app.schemas.county_adapter_schema import CountyAdapterResponse
from app.schemas.county_pipeline_schema import CountyPipelinePlanResponse
from pipelines.county_adapters import get_county_adapter, list_county_adapters
from pipelines.county_pipeline import (
    build_county_pipeline_plan,
    list_priority_county_pipeline_plans,
)


def list_supported_counties() -> list[CountyAdapterResponse]:
    return [
        CountyAdapterResponse(**adapter.describe())
        for adapter in list_county_adapters()
    ]


def get_supported_county(county: str) -> Optional[CountyAdapterResponse]:
    adapter = get_county_adapter(county)
    if adapter is None:
        return None
    return CountyAdapterResponse(**adapter.describe())


def list_county_pipeline_plans() -> list[CountyPipelinePlanResponse]:
    return [
        CountyPipelinePlanResponse(**plan.to_dict())
        for plan in list_priority_county_pipeline_plans()
    ]


def get_county_pipeline_plan(county: str) -> Optional[CountyPipelinePlanResponse]:
    plan = build_county_pipeline_plan(county)
    if plan is None:
        return None
    return CountyPipelinePlanResponse(**plan.to_dict())
