from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.provider_schema import ProviderIngestionRequest


class ManifestLinkResponse(BaseModel):
    href: str
    text: str


class CountyDatasetCandidateResponse(BaseModel):
    dataset_key: str
    label: str
    url: str
    matched_text: str


class CountyManifestInspectRequest(BaseModel):
    html: str = Field(min_length=1)
    source_url: Optional[str] = None


class CountyManifestInspectResponse(BaseModel):
    county: str
    source_url: str
    discovered_links: list[ManifestLinkResponse] = Field(default_factory=list)
    dataset_candidates: list[CountyDatasetCandidateResponse] = Field(default_factory=list)


class CountyPrepareRequest(BaseModel):
    dataset_key: str
    source_observed_at: str
    provider_name: Optional[str] = None
    rows: list[dict[str, Any]] = Field(default_factory=list)


class CountyPrepareResponse(BaseModel):
    request: ProviderIngestionRequest
