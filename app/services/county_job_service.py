from typing import Optional

from app.schemas.county_sync_schema import CountySyncRequest, CountySyncResponse
from app.services.county_sync_service import CountySyncService
from pipelines.county_pipeline import list_priority_county_pipeline_plans


class CountyJobService:
    def __init__(self, sync_service: Optional[CountySyncService] = None) -> None:
        self.sync_service = sync_service or CountySyncService()

    def run_county_sync(
        self,
        county: str,
        request: Optional[CountySyncRequest] = None,
    ) -> CountySyncResponse:
        return self.sync_service.run(county=county, request=request)

    def run_ready_county_syncs(self) -> list[CountySyncResponse]:
        responses: list[CountySyncResponse] = []
        for plan in list_priority_county_pipeline_plans():
            if plan.readiness != "ready_now":
                continue
            responses.append(
                self.sync_service.run(
                    county=plan.county,
                    request=CountySyncRequest(dataset_key=plan.datasets[0].dataset_key),
                )
            )
        return responses
