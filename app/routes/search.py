from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.property_schema import PropertyDetail, SearchResponse
from app.services.property_service import PropertyService


router = APIRouter(tags=["search"])
service = PropertyService()


@router.get("/search", response_model=SearchResponse)
def search_properties(
    query: Optional[str] = None,
    county: Optional[str] = None,
    city: Optional[str] = None,
    region_key: Optional[str] = None,
    max_list_price: Optional[float] = Query(default=None, gt=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> SearchResponse:
    return service.search_properties(
        query=query,
        county=county,
        city=city,
        region_key=region_key,
        max_list_price=max_list_price,
        limit=limit,
    )


@router.get("/properties/{property_id}", response_model=PropertyDetail)
def get_property(property_id: str) -> PropertyDetail:
    property_detail = service.get_property_detail(property_id)
    if property_detail is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Property not found")
    return property_detail
