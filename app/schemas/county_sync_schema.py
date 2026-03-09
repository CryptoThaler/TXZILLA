from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.provider_schema import ProviderIngestionResponse


class CountyRunArtifactResponse(BaseModel):
    source_url: str
    local_path: str
    checksum_sha256: str
    media_type: Optional[str] = None
    bytes_downloaded: int


class CountySyncRequest(BaseModel):
    dataset_key: Optional[str] = None
    max_records: Optional[int] = Field(default=None, gt=0)
    source_observed_at: Optional[str] = None


class CountySyncResponse(BaseModel):
    county: str
    dataset_key: str
    manifest_source_url: str
    artifact: CountyRunArtifactResponse
    provider_ingestion: ProviderIngestionResponse
