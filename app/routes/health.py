from fastapi import APIRouter, Response, status

from app.schemas.health_schema import HealthResponse, LivenessResponse
from app.services.health_service import get_health_report, get_liveness_report, is_ready


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return get_health_report()


@router.get("/live", response_model=LivenessResponse)
def live() -> LivenessResponse:
    return get_liveness_report()


@router.get("/ready", response_model=HealthResponse)
def ready(response: Response) -> HealthResponse:
    report = get_health_report()
    response.status_code = status.HTTP_200_OK if is_ready(report) else status.HTTP_503_SERVICE_UNAVAILABLE
    return report
