from pydantic import BaseModel, Field


class ParserProfileResponse(BaseModel):
    parser_kind: str
    archive_format: str
    geometry_expected: bool
    layout_binding_required: bool
    exact_match_fields: list[str] = Field(default_factory=list)
    review_trigger_fields: list[str] = Field(default_factory=list)


class DatasetManifestResponse(BaseModel):
    dataset_key: str
    label: str
    county: str
    url: str
    cadence: str
    priority: int
    parser_profile: ParserProfileResponse
    purpose: str
    status: str
    notes: str


class CountyPipelinePlanResponse(BaseModel):
    county: str
    display_name: str
    region_key: str
    readiness: str
    fastest_path: str
    accuracy_controls: list[str] = Field(default_factory=list)
    datasets: list[DatasetManifestResponse] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
