from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import desc, select, update
from sqlalchemy.engine import Engine

from app.database import get_engine
from app.models.provider_models import get_provider_tables


class ProviderRepository:
    def __init__(self, engine: Optional[Engine] = None) -> None:
        self.engine = engine or get_engine()
        schema_name = None if self.engine.dialect.name == "sqlite" else "real_estate"
        tables = get_provider_tables(schema_name)
        self.metadata = tables["metadata"]
        self.provider_runs = tables["provider_runs"]
        self.raw_properties = tables["raw_properties"]
        self.raw_listings = tables["raw_listings"]
        self.entity_resolution_events = tables["entity_resolution_events"]
        self.provider_run_artifacts = tables["provider_run_artifacts"]

    def ensure_storage(self) -> None:
        self.metadata.create_all(self.engine)

    def create_provider_run(
        self,
        provider_name: str,
        provider_type: str,
        region_key: Optional[str],
        fetched_at: datetime,
        record_count: int,
        metadata: dict,
    ) -> dict:
        self.ensure_storage()
        run_id = str(uuid4())
        now = datetime.now(timezone.utc)

        payload = {
            "provider_run_id": run_id,
            "provider_name": provider_name,
            "provider_type": provider_type,
            "region_key": region_key,
            "requested_at": now,
            "fetched_at": fetched_at,
            "completed_at": None,
            "run_status": "running",
            "record_count": record_count,
            "metadata": metadata,
            "error_message": None,
            "created_at": now,
        }
        with self.engine.begin() as connection:
            connection.execute(self.provider_runs.insert().values(**payload))

        return payload

    def complete_provider_run(self, provider_run_id: str) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                update(self.provider_runs)
                .where(self.provider_runs.c.provider_run_id == provider_run_id)
                .values(
                    run_status="completed",
                    completed_at=datetime.now(timezone.utc),
                )
            )

    def fail_provider_run(self, provider_run_id: str, error_message: str) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                update(self.provider_runs)
                .where(self.provider_runs.c.provider_run_id == provider_run_id)
                .values(
                    run_status="failed",
                    completed_at=datetime.now(timezone.utc),
                    error_message=error_message,
                )
            )

    def store_raw_properties(
        self,
        provider_run_id: str,
        provider_name: str,
        provider_type: str,
        fetched_at: datetime,
        records: list[dict],
    ) -> int:
        if not records:
            return 0

        now = datetime.now(timezone.utc)
        payloads = [
            {
                "raw_property_id": str(uuid4()),
                "provider_run_id": provider_run_id,
                "provider_name": provider_name,
                "provider_type": provider_type,
                "source_record_id": record["source_record_id"],
                "county": record.get("county"),
                "region_key": record.get("region_key"),
                "fetched_at": fetched_at,
                "payload": record["raw_lineage"]["payload"],
                "standardized_payload": record,
                "created_at": now,
            }
            for record in records
        ]
        with self.engine.begin() as connection:
            connection.execute(self.raw_properties.insert(), payloads)
        return len(payloads)

    def store_raw_listings(
        self,
        provider_run_id: str,
        provider_name: str,
        provider_type: str,
        fetched_at: datetime,
        records: list[dict],
    ) -> int:
        if not records:
            return 0

        now = datetime.now(timezone.utc)
        payloads = [
            {
                "raw_listing_id": str(uuid4()),
                "provider_run_id": provider_run_id,
                "provider_name": provider_name,
                "provider_type": provider_type,
                "source_record_id": record["source_record_id"],
                "county": record.get("county"),
                "region_key": record.get("region_key"),
                "fetched_at": fetched_at,
                "payload": record["raw_lineage"]["payload"],
                "standardized_payload": record,
                "created_at": now,
            }
            for record in records
        ]
        with self.engine.begin() as connection:
            connection.execute(self.raw_listings.insert(), payloads)
        return len(payloads)

    def store_resolution_events(
        self,
        provider_run_id: str,
        provider_name: str,
        events: list[dict],
    ) -> int:
        if not events:
            return 0

        now = datetime.now(timezone.utc)
        payloads = [
            {
                "entity_resolution_event_id": str(uuid4()),
                "provider_run_id": provider_run_id,
                "provider_name": provider_name,
                "source_record_id": event["source_record_id"],
                "canonical_entity_type": event["canonical_entity_type"],
                "canonical_entity_id": event.get("canonical_entity_id"),
                "match_status": event["match_status"],
                "confidence": event["confidence"],
                "resolution_reason": event["resolution_reason"],
                "event_payload": event,
                "created_at": now,
            }
            for event in events
        ]
        with self.engine.begin() as connection:
            connection.execute(self.entity_resolution_events.insert(), payloads)
        return len(payloads)

    def list_provider_runs(self, limit: int = 20) -> list[dict]:
        self.ensure_storage()
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(self.provider_runs)
                .order_by(desc(self.provider_runs.c.fetched_at))
                .limit(limit)
            ).mappings()
            return [dict(row) for row in rows]

    def store_run_artifact(
        self,
        provider_run_id: str,
        county: str,
        dataset_key: str,
        source_url: str,
        local_path: str,
        checksum_sha256: str,
        media_type: Optional[str],
        bytes_downloaded: int,
    ) -> dict:
        self.ensure_storage()
        payload = {
            "provider_run_artifact_id": str(uuid4()),
            "provider_run_id": provider_run_id,
            "county": county,
            "dataset_key": dataset_key,
            "source_url": source_url,
            "local_path": local_path,
            "checksum_sha256": checksum_sha256,
            "media_type": media_type,
            "bytes_downloaded": bytes_downloaded,
            "created_at": datetime.now(timezone.utc),
        }
        with self.engine.begin() as connection:
            connection.execute(self.provider_run_artifacts.insert().values(**payload))
        return payload

    def list_run_artifacts(self, provider_run_id: str) -> list[dict]:
        self.ensure_storage()
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(self.provider_run_artifacts)
                .where(self.provider_run_artifacts.c.provider_run_id == provider_run_id)
                .order_by(desc(self.provider_run_artifacts.c.created_at))
            ).mappings()
            return [dict(row) for row in rows]

    def list_artifacts(
        self,
        limit: int = 20,
        county: Optional[str] = None,
        dataset_key: Optional[str] = None,
    ) -> list[dict]:
        self.ensure_storage()
        query = select(self.provider_run_artifacts)
        if county is not None:
            query = query.where(self.provider_run_artifacts.c.county == county)
        if dataset_key is not None:
            query = query.where(self.provider_run_artifacts.c.dataset_key == dataset_key)

        with self.engine.begin() as connection:
            rows = connection.execute(
                query.order_by(desc(self.provider_run_artifacts.c.created_at)).limit(limit)
            ).mappings()
            return [dict(row) for row in rows]
