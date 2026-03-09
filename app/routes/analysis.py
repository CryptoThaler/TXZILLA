from fastapi import APIRouter, HTTPException

from app.schemas.analysis_schema import PropertyAnalysisReport
from app.services.report_service import ReportService


router = APIRouter(tags=["analysis"])
service = ReportService()


@router.get("/analyze/{property_id}", response_model=PropertyAnalysisReport)
def analyze_property(property_id: str) -> PropertyAnalysisReport:
    try:
        return service.build_property_report(property_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
