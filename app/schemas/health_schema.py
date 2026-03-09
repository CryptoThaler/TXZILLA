from typing import Literal

from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    dialect: str
    reachable: bool
    bootstrap_verified: bool
    bootstrap_ready: bool
    required_extensions: list[str] = Field(default_factory=list)
    present_extensions: list[str] = Field(default_factory=list)
    required_schema: str
    schema_present: bool
    required_tables: list[str] = Field(default_factory=list)
    present_tables: list[str] = Field(default_factory=list)
    missing_tables: list[str] = Field(default_factory=list)
    detail: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: str
    environment: str
    version: str
    database: DatabaseHealth


class LivenessResponse(BaseModel):
    status: Literal["ok"]
    service: str
    environment: str
    version: str
