from datetime import datetime, timezone
from typing import Optional

from app.repositories.provider_repository import ProviderRepository
from app.schemas.county_sync_schema import (
    CountyRunArtifactResponse,
    CountySyncRequest,
    CountySyncResponse,
)
from app.services.provider_ingestion_service import ProviderIngestionService
from app.settings import Settings, get_settings
from pipelines.county_fetch import CountyFetchClient, write_download_artifact
from pipelines.county_manifest import build_manifest_snapshot
from pipelines.county_parser import parse_delimited_export
from pipelines.county_pipeline import build_county_pipeline_plan
from pipelines.county_procedures import build_provider_request_from_county_export


class CountySyncService:
    def __init__(
        self,
        fetch_client: Optional[CountyFetchClient] = None,
        provider_ingestion_service: Optional[ProviderIngestionService] = None,
        provider_repository: Optional[ProviderRepository] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        self.fetch_client = fetch_client or CountyFetchClient()
        self.provider_ingestion_service = provider_ingestion_service or ProviderIngestionService()
        self.provider_repository = provider_repository or ProviderRepository()
        self.settings = settings or get_settings()

    @staticmethod
    def _supports_autonomous_sync(parser_kind: str) -> bool:
        return parser_kind == "bulk_export_layout"

    def _select_target_dataset(self, county: str, request: Optional[CountySyncRequest]):
        plan = build_county_pipeline_plan(county)
        if plan is None:
            raise ValueError(f"Unsupported county pipeline: {county}")

        if request and request.dataset_key:
            for dataset in plan.datasets:
                if dataset.dataset_key == request.dataset_key:
                    if not self._supports_autonomous_sync(dataset.parser_profile.parser_kind):
                        raise ValueError(
                            f"{dataset.dataset_key} is not automation-ready for autonomous sync."
                        )
                    return plan, dataset
            raise ValueError(f"{plan.county} dataset not configured: {request.dataset_key}")

        eligible_datasets = [
            dataset
            for dataset in plan.datasets
            if self._supports_autonomous_sync(dataset.parser_profile.parser_kind)
        ]
        if not eligible_datasets:
            raise ValueError(f"{plan.county} has no automation-ready datasets configured.")

        eligible_datasets.sort(key=lambda dataset: dataset.priority)
        return plan, eligible_datasets[0]

    def run(self, county: str, request: Optional[CountySyncRequest] = None) -> CountySyncResponse:
        plan, target_dataset = self._select_target_dataset(county=county, request=request)
        if plan.readiness != "ready_now":
            raise ValueError(f"{plan.county} pipeline is not automation-ready: {plan.readiness}")

        manifest_html = self.fetch_client.fetch_text(target_dataset.url)
        snapshot = build_manifest_snapshot(
            county=county,
            html=manifest_html,
            source_url=target_dataset.url,
        )

        candidates = [
            candidate
            for candidate in snapshot.dataset_candidates
            if candidate.dataset_key == target_dataset.dataset_key
        ]
        if not candidates:
            raise ValueError(
                f"No matching dataset candidates discovered for {plan.county} "
                f"dataset {target_dataset.dataset_key}."
            )

        selected = candidates[0]
        payload, media_type = self.fetch_client.download_bytes(selected.url)
        artifact = write_download_artifact(
            county=plan.county,
            dataset_key=selected.dataset_key,
            source_url=selected.url,
            payload=payload,
            media_type=media_type,
            download_dir=self.settings.county_download_dir,
        )

        rows = parse_delimited_export(plan.county, payload, selected.url)
        if request and request.max_records:
            rows = rows[: request.max_records]

        observed_at = (
            request.source_observed_at
            if request and request.source_observed_at
            else datetime.now(timezone.utc).isoformat()
        )
        provider_request = build_provider_request_from_county_export(
            county=plan.county,
            dataset_key=selected.dataset_key,
            rows=rows,
            source_observed_at=observed_at,
            provider_name=f"{plan.county.lower()}_{selected.dataset_key}",
        )
        provider_response = self.provider_ingestion_service.ingest(provider_request)
        self.provider_repository.store_run_artifact(
            provider_run_id=provider_response.run.provider_run_id,
            county=plan.county,
            dataset_key=selected.dataset_key,
            source_url=artifact.source_url,
            local_path=artifact.local_path,
            checksum_sha256=artifact.checksum_sha256,
            media_type=artifact.media_type,
            bytes_downloaded=artifact.bytes_downloaded,
        )

        return CountySyncResponse(
            county=plan.county,
            dataset_key=selected.dataset_key,
            manifest_source_url=snapshot.source_url,
            artifact=CountyRunArtifactResponse(
                source_url=artifact.source_url,
                local_path=artifact.local_path,
                checksum_sha256=artifact.checksum_sha256,
                media_type=artifact.media_type,
                bytes_downloaded=artifact.bytes_downloaded,
            ),
            provider_ingestion=provider_response,
        )
