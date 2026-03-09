from pydantic import BaseModel, Field


class CountySourceResponse(BaseModel):
    label: str
    url: str
    access_method: str
    format: str
    priority: int
    notes: str


class CountyProcedureStepResponse(BaseModel):
    order: int
    title: str
    description: str
    gate: str


class CountyAdapterResponse(BaseModel):
    county: str
    display_name: str
    region_key: str
    bulk_sources: list[CountySourceResponse] = Field(default_factory=list)
    clerk_sources: list[CountySourceResponse] = Field(default_factory=list)
    procedure: list[CountyProcedureStepResponse] = Field(default_factory=list)
    field_aliases: dict[str, list[str]] = Field(default_factory=dict)
    required_exact_fields: list[str] = Field(default_factory=list)
    formalization_strategy: list[str] = Field(default_factory=list)
    refresh_cad: str
    refresh_clerk: str
