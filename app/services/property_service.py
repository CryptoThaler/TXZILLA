from typing import Optional

from app.repositories.property_repository import PropertyRepository
from app.schemas.property_schema import PropertyDetail, PropertySummary, SearchResponse
from app.services.region_service import get_region


class PropertyService:
    def __init__(self, repository: Optional[PropertyRepository] = None) -> None:
        self.repository = repository or PropertyRepository()

    def search_properties(
        self,
        query: Optional[str] = None,
        county: Optional[str] = None,
        city: Optional[str] = None,
        region_key: Optional[str] = None,
        max_list_price: Optional[float] = None,
        limit: int = 20,
    ) -> SearchResponse:
        items = [
            PropertySummary(**record)
            for record in self.repository.list_properties(
                query=query,
                county=county,
                city=city,
                region_key=region_key,
                max_list_price=max_list_price,
                limit=limit,
            )
        ]
        region = get_region(region_key) if region_key else None
        return SearchResponse(
            total=len(items),
            items=items,
            region_key=region_key,
            counties=region.counties if region else [],
        )

    def get_property_detail(self, property_id: str) -> Optional[PropertyDetail]:
        record = self.repository.get_property(property_id)
        if not record:
            return None
        return PropertyDetail(**record)
