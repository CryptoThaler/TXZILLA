from datetime import datetime, timezone
from typing import Optional

from app.repositories.public_record_repository import PublicRecordRepository
from app.repositories.property_repository import PropertyRepository
from app.repositories.provider_repository import ProviderRepository
from app.schemas.provider_schema import (
    ProviderArtifactSummary,
    ProviderIngestionRequest,
    ProviderIngestionResponse,
    ProviderRunSummary,
)
from app.services.region_service import resolve_region_for_county
from pipelines.cad_ingestion import ingest_cad
from pipelines.entity_resolution import resolve_entities
from pipelines.mls_ingestion import ingest_mls


class ProviderIngestionService:
    def __init__(
        self,
        repository: Optional[ProviderRepository] = None,
        property_repository: Optional[PropertyRepository] = None,
        public_record_repository: Optional[PublicRecordRepository] = None,
    ) -> None:
        self.repository = repository or ProviderRepository()
        self.public_record_repository = public_record_repository or PublicRecordRepository()
        self.property_repository = property_repository or PropertyRepository()

    def ingest(self, request: ProviderIngestionRequest) -> ProviderIngestionResponse:
        fetched_at = request.fetched_at or datetime.now(timezone.utc)
        run = self.repository.create_provider_run(
            provider_name=request.provider_name,
            provider_type=request.provider_type,
            region_key=request.region_key,
            fetched_at=fetched_at,
            record_count=len(request.records),
            metadata=request.metadata,
        )

        try:
            if request.provider_type == "cad":
                output = self._ingest_cad(request, fetched_at, run["provider_run_id"])
            else:
                output = self._ingest_listings(request, fetched_at, run["provider_run_id"])

            self.repository.complete_provider_run(run["provider_run_id"])
            run["run_status"] = "completed"
            run["completed_at"] = datetime.now(timezone.utc)

            return ProviderIngestionResponse(
                run=ProviderRunSummary(**run),
                stored_raw_properties=output["stored_raw_properties"],
                stored_raw_listings=output["stored_raw_listings"],
                canonical_properties_upserted=output["canonical_properties_upserted"],
                assessment_records_written=output["assessment_records_written"],
                ownership_records_written=output["ownership_records_written"],
                matched_records=output["matched_records"],
                review_records=output["review_records"],
                unmatched_records=output["unmatched_records"],
                notes=output["notes"],
            )
        except Exception as exc:
            self.repository.fail_provider_run(run["provider_run_id"], str(exc))
            raise

    def list_runs(self, limit: int = 20) -> list[ProviderRunSummary]:
        return [
            ProviderRunSummary(**record)
            for record in self.repository.list_provider_runs(limit=limit)
        ]

    def list_run_artifacts(self, provider_run_id: str) -> list[ProviderArtifactSummary]:
        return [
            ProviderArtifactSummary(**record)
            for record in self.repository.list_run_artifacts(provider_run_id=provider_run_id)
        ]

    def list_artifacts(
        self,
        limit: int = 20,
        county: Optional[str] = None,
        dataset_key: Optional[str] = None,
    ) -> list[ProviderArtifactSummary]:
        return [
            ProviderArtifactSummary(**record)
            for record in self.repository.list_artifacts(
                limit=limit,
                county=county,
                dataset_key=dataset_key,
            )
        ]

    def _ingest_cad(
        self,
        request: ProviderIngestionRequest,
        fetched_at: datetime,
        provider_run_id: str,
    ) -> dict:
        notes: list[str] = []
        curated_records: list[dict] = []
        assessment_records: list[dict] = []
        ownership_records: list[dict] = []

        for record in request.records:
            region_key = request.region_key or resolve_region_for_county(record["county"])
            if region_key is None:
                notes.append(
                    f"region_missing_for_county:{record['county']}"
                )
                region_key = "unassigned"

            output = ingest_cad(
                [record],
                fetched_at=fetched_at.isoformat(),
                region_key=region_key,
            )
            curated_records.extend(output["curated"])
            for curated_record in output["curated"]:
                if curated_record.get("tax_year") and curated_record.get("assessed_total_value") is not None:
                    assessment_records.append(
                        {
                            "property_id": curated_record["property_id"],
                            "tax_year": int(curated_record["tax_year"]),
                            "assessed_total_value": curated_record["assessed_total_value"],
                            "assessed_land_value": curated_record.get("assessed_land_value"),
                            "assessed_improvement_value": curated_record.get("assessed_improvement_value"),
                            "taxable_value": curated_record.get("taxable_value"),
                            "tax_amount_annual": curated_record.get("tax_amount_annual"),
                            "source_name": curated_record["source_name"],
                            "source_record_id": curated_record["source_record_id"],
                            "source_observed_at": curated_record["source_observed_at"],
                        }
                    )
                if curated_record.get("owner_name"):
                    ownership_records.append(
                        {
                            "property_id": curated_record["property_id"],
                            "owner_name": curated_record["owner_name"],
                            "ownership_start_date": curated_record.get("ownership_start_date"),
                            "ownership_end_date": None,
                            "mailing_address": curated_record.get("mailing_address"),
                            "source_name": curated_record["source_name"],
                            "source_record_id": curated_record["source_record_id"],
                            "source_observed_at": curated_record["source_observed_at"],
                        }
                    )

        stored_raw_properties = self.repository.store_raw_properties(
            provider_run_id=provider_run_id,
            provider_name=request.provider_name,
            provider_type=request.provider_type,
            fetched_at=fetched_at,
            records=curated_records,
        )
        canonical_properties_upserted = self.public_record_repository.upsert_properties(
            curated_records
        )
        assessment_records_written = self.public_record_repository.insert_assessment_history(
            assessment_records
        )
        ownership_records_written = self.public_record_repository.insert_ownership_history(
            ownership_records
        )

        return {
            "stored_raw_properties": stored_raw_properties,
            "stored_raw_listings": 0,
            "canonical_properties_upserted": canonical_properties_upserted,
            "assessment_records_written": assessment_records_written,
            "ownership_records_written": ownership_records_written,
            "matched_records": 0,
            "review_records": 0,
            "unmatched_records": 0,
            "notes": notes,
        }

    def _ingest_listings(
        self,
        request: ProviderIngestionRequest,
        fetched_at: datetime,
        provider_run_id: str,
    ) -> dict:
        notes: list[str] = []
        output = ingest_mls(request.records, fetched_at=fetched_at.isoformat())
        standardized_records = output["standardized"]

        property_catalog = self.property_repository.list_property_catalog()
        resolution_events: list[dict] = []
        matched_records = 0
        review_records = 0
        unmatched_records = 0

        for record in standardized_records:
            region_key = request.region_key or resolve_region_for_county(record["county"])
            record["region_key"] = region_key
            resolution = resolve_entities(property_catalog, record)
            if resolution["match_status"] == "matched":
                matched_records += 1
            elif resolution["match_status"] == "review":
                review_records += 1
                notes.append(f"review_required:{record['source_record_id']}")
            else:
                unmatched_records += 1

            resolution_events.append(
                {
                    "source_record_id": record["source_record_id"],
                    "canonical_entity_type": "property",
                    "canonical_entity_id": resolution.get("property_id"),
                    "match_status": resolution["match_status"],
                    "confidence": resolution["confidence"],
                    "resolution_reason": resolution["reason"],
                }
            )

        stored_raw_listings = self.repository.store_raw_listings(
            provider_run_id=provider_run_id,
            provider_name=request.provider_name,
            provider_type=request.provider_type,
            fetched_at=fetched_at,
            records=standardized_records,
        )
        self.repository.store_resolution_events(
            provider_run_id=provider_run_id,
            provider_name=request.provider_name,
            events=resolution_events,
        )

        return {
            "stored_raw_properties": 0,
            "stored_raw_listings": stored_raw_listings,
            "canonical_properties_upserted": 0,
            "assessment_records_written": 0,
            "ownership_records_written": 0,
            "matched_records": matched_records,
            "review_records": review_records,
            "unmatched_records": unmatched_records,
            "notes": notes,
        }
