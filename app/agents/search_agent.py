from typing import Optional

from app.schemas.property_schema import PropertyDetail, SearchResponse
from app.services.property_service import PropertyService


class SearchAgent:
    name = "search_agent"

    def __init__(self, service: Optional[PropertyService] = None) -> None:
        self.service = service or PropertyService()

    def search(self, **filters) -> SearchResponse:
        return self.service.search_properties(**filters)

    def get_property(self, property_id: str) -> PropertyDetail:
        property_detail = self.service.get_property_detail(property_id)
        if property_detail is None:
            raise ValueError(f"Unknown property: {property_id}")
        return property_detail
