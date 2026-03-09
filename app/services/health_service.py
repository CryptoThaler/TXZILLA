from typing import Optional

from app.repositories.bootstrap_repository import DatabaseBootstrapRepository
from app.schemas.health_schema import DatabaseHealth, HealthResponse, LivenessResponse
from app.settings import Settings, get_settings


def get_health_report(
    repository: Optional[DatabaseBootstrapRepository] = None,
    settings: Optional[Settings] = None,
) -> HealthResponse:
    resolved_settings = settings or get_settings()
    inspection = (repository or DatabaseBootstrapRepository()).inspect_bootstrap()

    status = "ok"
    if not inspection.reachable:
        status = "degraded"
    elif inspection.dialect == "postgresql" and not inspection.bootstrap_ready:
        status = "degraded"

    return HealthResponse(
        status=status,
        service=resolved_settings.app_name,
        environment=resolved_settings.app_env,
        version=resolved_settings.app_version,
        database=DatabaseHealth(
            dialect=inspection.dialect,
            reachable=inspection.reachable,
            bootstrap_verified=inspection.bootstrap_verified,
            bootstrap_ready=inspection.bootstrap_ready,
            required_extensions=inspection.required_extensions,
            present_extensions=inspection.present_extensions,
            required_schema=inspection.required_schema,
            schema_present=inspection.schema_present,
            required_tables=inspection.required_tables,
            present_tables=inspection.present_tables,
            missing_tables=inspection.missing_tables,
            detail=inspection.detail,
        ),
    )


def get_liveness_report(settings: Optional[Settings] = None) -> LivenessResponse:
    resolved_settings = settings or get_settings()
    return LivenessResponse(
        status="ok",
        service=resolved_settings.app_name,
        environment=resolved_settings.app_env,
        version=resolved_settings.app_version,
    )


def is_ready(report: HealthResponse) -> bool:
    return report.status == "ok"
