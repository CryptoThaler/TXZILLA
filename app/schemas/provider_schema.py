from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ProviderIngestionRequest(BaseModel):
    provider_name: str = Field(min_length=1)
    provider_type: Literal["cad", "mls", "listing_feed"]
    region_key: Optional[str] = None
    fetched_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    records: list[dict[str, Any]] = Field(default_factory=list)


class ProviderRunSummary(BaseModel):
    provider_run_id: str
    provider_name: str
    provider_type: str
    region_key: Optional[str] = None
    fetched_at: datetime
    completed_at: Optional[datetime] = None
    run_status: str
    record_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


class ProviderArtifactSummary(BaseModel):
    provider_run_artifact_id: str
    provider_run_id: str
    county: Optional[str] = None
    dataset_key: str
    source_url: str
    local_path: str
    checksum_sha256: str
    media_type: Optional[str] = None
    bytes_downloaded: int
    created_at: datetime


class ProviderIngestionResponse(BaseModel):
    run: ProviderRunSummary
    stored_raw_properties: int
    stored_raw_listings: int
    canonical_properties_upserted: int
    assessment_records_written: int
    ownership_records_written: int
    matched_records: int
    review_records: int
    unmatched_records: int
    notes: list[str] = Field(default_factory=list)
