from typing import Optional

from celery import Celery

from app.schemas.county_sync_schema import CountySyncRequest
from app.services.county_job_service import CountyJobService
from app.settings import Settings, get_settings


def configure_celery_app(celery: Celery, settings: Settings) -> Celery:
    celery.conf.timezone = settings.app_timezone
    celery.conf.enable_utc = True
    celery.conf.beat_schedule = {}
    if settings.enable_background_jobs and settings.county_sync_task_enabled:
        celery.conf.beat_schedule["county-ready-syncs"] = {
            "task": "txzilla.counties.run_ready_syncs",
            "schedule": int(settings.county_sync_interval_hours) * 3600,
        }
    return celery


celery_app = configure_celery_app(
    Celery("txzilla", broker=get_settings().redis_url),
    get_settings(),
)


@celery_app.task(name="txzilla.counties.run_sync")
def run_county_sync_task(county: str, request_payload: Optional[dict] = None) -> dict:
    service = CountyJobService()
    request = CountySyncRequest(**request_payload) if request_payload else CountySyncRequest()
    response = service.run_county_sync(county=county, request=request)
    return response.model_dump(mode="json")


@celery_app.task(name="txzilla.counties.run_ready_syncs")
def run_ready_county_syncs_task() -> list[dict]:
    service = CountyJobService()
    return [response.model_dump(mode="json") for response in service.run_ready_county_syncs()]
