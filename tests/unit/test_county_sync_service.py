import csv
import io
import zipfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool

from app.repositories.provider_repository import ProviderRepository
from app.repositories.public_record_repository import PublicRecordRepository
from app.schemas.county_sync_schema import CountySyncRequest
from app.services.county_sync_service import CountySyncService
from app.services.provider_ingestion_service import ProviderIngestionService
from app.settings import Settings


def _build_engine():
    return create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _build_zip_payload(filename: str, rows: list[list[str]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(rows)
        archive.writestr(filename, csv_buffer.getvalue())
    return buffer.getvalue()


class FakeCountyFetchClient:
    def __init__(self, manifest_html_by_url: dict[str, str], payload_by_url: dict[str, tuple[bytes, str]]) -> None:
        self.manifest_html_by_url = manifest_html_by_url
        self.payload_by_url = payload_by_url
        self.fetched_text_urls: list[str] = []
        self.downloaded_urls: list[str] = []

    def fetch_text(self, url: str) -> str:
        self.fetched_text_urls.append(url)
        return self.manifest_html_by_url[url]

    def download_bytes(self, url: str) -> tuple[bytes, str]:
        self.downloaded_urls.append(url)
        return self.payload_by_url[url]


def test_county_sync_service_runs_hays_export_and_stores_artifact(tmp_path):
    engine = _build_engine()
    provider_repository = ProviderRepository(engine=engine)
    public_record_repository = PublicRecordRepository(engine=engine)
    provider_ingestion_service = ProviderIngestionService(
        repository=provider_repository,
        public_record_repository=public_record_repository,
    )
    fetch_client = FakeCountyFetchClient(
        manifest_html_by_url={
            "https://hayscad.com/data-downloads/": """
            <a href="/files/hays-property-export.zip">2025 Property Data Export Files</a>
            <a href="/files/hays-gis-shapefile.zip">GIS Shapefile Download</a>
            """,
        },
        payload_by_url={
            "https://hayscad.com/files/hays-property-export.zip": (
                _build_zip_payload(
                    "hays_property_export.csv",
                    [
                        ["acct", "property_address", "city", "lat", "lon", "owner", "market_value", "year"],
                        ["HAY-201", "201 Stagecoach Trl", "San Marcos", "29.88", "-97.94", "Hays Owner LLC", "385000", "2025"],
                    ],
                ),
                "application/zip",
            )
        },
    )
    service = CountySyncService(
        fetch_client=fetch_client,
        provider_ingestion_service=provider_ingestion_service,
        provider_repository=provider_repository,
        settings=Settings(county_download_dir=str(tmp_path)),
    )

    response = service.run(
        "hays",
        CountySyncRequest(
            max_records=1,
            source_observed_at="2026-03-09T00:00:00Z",
        ),
    )

    assert response.county == "Hays"
    assert response.dataset_key == "hays_property_export"
    assert response.provider_ingestion.stored_raw_properties == 1
    assert response.provider_ingestion.canonical_properties_upserted == 1
    assert Path(response.artifact.local_path).exists()
    assert response.artifact.bytes_downloaded > 0
    assert fetch_client.fetched_text_urls == ["https://hayscad.com/data-downloads/"]
    assert fetch_client.downloaded_urls == ["https://hayscad.com/files/hays-property-export.zip"]

    with engine.begin() as connection:
        artifacts = connection.execute(
            select(provider_repository.provider_run_artifacts)
        ).mappings().all()
    assert len(artifacts) == 1
    assert artifacts[0]["dataset_key"] == "hays_property_export"


def test_county_sync_service_uses_requested_dataset_manifest_for_williamson(tmp_path):
    engine = _build_engine()
    provider_repository = ProviderRepository(engine=engine)
    public_record_repository = PublicRecordRepository(engine=engine)
    provider_ingestion_service = ProviderIngestionService(
        repository=provider_repository,
        public_record_repository=public_record_repository,
    )
    fetch_client = FakeCountyFetchClient(
        manifest_html_by_url={
            "https://www.wcad.org/historical-data/": """
            <a href="/files/2025-historical-certified.zip">2025 Historical Certified Export</a>
            """,
        },
        payload_by_url={
            "https://www.wcad.org/files/2025-historical-certified.zip": (
                _build_zip_payload(
                    "williamson_historical_export.csv",
                    [
                        ["acct", "property_address", "city", "lat", "lon", "owner", "market_value", "taxyear"],
                        ["WIL-301", "301 Heritage Loop", "Georgetown", "30.63", "-97.68", "Williamson Owner LLC", "425000", "2025"],
                    ],
                ),
                "application/zip",
            )
        },
    )
    service = CountySyncService(
        fetch_client=fetch_client,
        provider_ingestion_service=provider_ingestion_service,
        provider_repository=provider_repository,
        settings=Settings(county_download_dir=str(tmp_path)),
    )

    response = service.run(
        "williamson",
        CountySyncRequest(
            dataset_key="williamson_historical_export",
            source_observed_at="2026-03-09T00:00:00Z",
        ),
    )

    assert response.dataset_key == "williamson_historical_export"
    assert response.provider_ingestion.assessment_records_written == 1
    assert fetch_client.fetched_text_urls == ["https://www.wcad.org/historical-data/"]
    assert fetch_client.downloaded_urls == ["https://www.wcad.org/files/2025-historical-certified.zip"]


def test_county_sync_service_blocks_bexar_until_access_is_formalized(tmp_path):
    service = CountySyncService(
        fetch_client=FakeCountyFetchClient({}, {}),
        settings=Settings(county_download_dir=str(tmp_path)),
    )

    with pytest.raises(ValueError, match="not automation-ready"):
        service.run("bexar", CountySyncRequest())
