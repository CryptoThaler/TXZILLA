from pydantic import BaseModel, Field


class RegionResponse(BaseModel):
    region_key: str
    display_name: str
    counties: list[str] = Field(default_factory=list)
