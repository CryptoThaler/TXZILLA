from functools import lru_cache
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Integer, MetaData, Numeric, String, Table, Text


@lru_cache(maxsize=4)
def get_provider_tables(schema_name: Optional[str]) -> dict[str, Table]:
    metadata = MetaData(schema=schema_name)

    provider_runs = Table(
        "provider_runs",
        metadata,
        Column("provider_run_id", String(36), primary_key=True),
        Column("provider_name", Text, nullable=False),
        Column("provider_type", Text, nullable=False),
        Column("region_key", Text, nullable=True),
        Column("requested_at", DateTime(timezone=True), nullable=False),
        Column("fetched_at", DateTime(timezone=True), nullable=False),
        Column("completed_at", DateTime(timezone=True), nullable=True),
        Column("run_status", Text, nullable=False),
        Column("record_count", Integer, nullable=False),
        Column("metadata", JSON, nullable=False),
        Column("error_message", Text, nullable=True),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )

    raw_properties = Table(
        "raw_properties",
        metadata,
        Column("raw_property_id", String(36), primary_key=True),
        Column("provider_run_id", String(36), nullable=False),
        Column("provider_name", Text, nullable=False),
        Column("provider_type", Text, nullable=False),
        Column("source_record_id", Text, nullable=False),
        Column("county", Text, nullable=True),
        Column("region_key", Text, nullable=True),
        Column("fetched_at", DateTime(timezone=True), nullable=False),
        Column("payload", JSON, nullable=False),
        Column("standardized_payload", JSON, nullable=True),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )

    raw_listings = Table(
        "raw_listings",
        metadata,
        Column("raw_listing_id", String(36), primary_key=True),
        Column("provider_run_id", String(36), nullable=False),
        Column("provider_name", Text, nullable=False),
        Column("provider_type", Text, nullable=False),
        Column("source_record_id", Text, nullable=False),
        Column("county", Text, nullable=True),
        Column("region_key", Text, nullable=True),
        Column("fetched_at", DateTime(timezone=True), nullable=False),
        Column("payload", JSON, nullable=False),
        Column("standardized_payload", JSON, nullable=True),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )

    entity_resolution_events = Table(
        "entity_resolution_events",
        metadata,
        Column("entity_resolution_event_id", String(36), primary_key=True),
        Column("provider_run_id", String(36), nullable=False),
        Column("provider_name", Text, nullable=False),
        Column("source_record_id", Text, nullable=False),
        Column("canonical_entity_type", Text, nullable=False),
        Column("canonical_entity_id", String(36), nullable=True),
        Column("match_status", Text, nullable=False),
        Column("confidence", Numeric(4, 3), nullable=False),
        Column("resolution_reason", Text, nullable=False),
        Column("event_payload", JSON, nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )

    provider_run_artifacts = Table(
        "provider_run_artifacts",
        metadata,
        Column("provider_run_artifact_id", String(36), primary_key=True),
        Column("provider_run_id", String(36), nullable=False),
        Column("county", Text, nullable=True),
        Column("dataset_key", Text, nullable=False),
        Column("source_url", Text, nullable=False),
        Column("local_path", Text, nullable=False),
        Column("checksum_sha256", Text, nullable=False),
        Column("media_type", Text, nullable=True),
        Column("bytes_downloaded", Integer, nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )

    return {
        "metadata": metadata,
        "provider_runs": provider_runs,
        "raw_properties": raw_properties,
        "raw_listings": raw_listings,
        "entity_resolution_events": entity_resolution_events,
        "provider_run_artifacts": provider_run_artifacts,
    }
