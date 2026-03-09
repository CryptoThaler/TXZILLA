from fastapi import APIRouter

from app.schemas.region_schema import RegionResponse
from app.services.region_service import list_regions


router = APIRouter(tags=["regions"])


@router.get("/regions", response_model=list[RegionResponse])
def get_regions() -> list[RegionResponse]:
    return list_regions()
