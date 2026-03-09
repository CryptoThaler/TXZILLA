from app.routes import counties as county_routes
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class FakeSyncService:
    def run(self, county: str, request):
        assert county == "hays"
        assert request.dataset_key == "hays_property_export"
        return county_routes.CountySyncResponse(
            county="Hays",
            dataset_key="hays_property_export",
            manifest_source_url="https://hayscad.com/data-downloads/",
            artifact={
                "source_url": "https://hayscad.com/files/hays-property-export.zip",
                "local_path": "/tmp/txzilla-county-downloads/hays/hays_property_export/demo.zip",
                "checksum_sha256": "abc123",
                "media_type": "application/zip",
                "bytes_downloaded": 128,
            },
            provider_ingestion={
                "run": {
                    "provider_run_id": "run-demo-001",
                    "provider_name": "hays_hays_property_export",
                    "provider_type": "cad",
                    "region_key": "central_texas",
                    "fetched_at": "2026-03-09T00:00:00Z",
                    "completed_at": "2026-03-09T00:01:00Z",
                    "run_status": "completed",
                    "record_count": 1,
                    "metadata": {"dataset_key": "hays_property_export"},
                    "error_message": None,
                },
                "stored_raw_properties": 1,
                "stored_raw_listings": 0,
                "canonical_properties_upserted": 1,
                "assessment_records_written": 1,
                "ownership_records_written": 1,
                "matched_records": 0,
                "review_records": 0,
                "unmatched_records": 0,
                "notes": [],
            },
        )


def test_county_adapters_route_lists_supported_counties():
    response = client.get("/counties/adapters")
    assert response.status_code == 200

    payload = response.json()
    assert [entry["county"] for entry in payload] == ["Bexar", "Hays", "Travis", "Williamson"]


def test_bexar_adapter_route_returns_bulk_strategy():
    response = client.get("/counties/adapters/bexar")
    assert response.status_code == 200

    payload = response.json()
    assert payload["bulk_sources"][0]["label"] == "BCAD property search"
    assert len(payload["formalization_strategy"]) >= 3


def test_county_pipeline_routes_return_ready_counties_and_bexar_strategy():
    response = client.get("/counties/pipelines")
    assert response.status_code == 200

    payload = response.json()
    readiness = {entry["county"]: entry["readiness"] for entry in payload}
    assert readiness["Hays"] == "ready_now"
    assert readiness["Travis"] == "ready_now"
    assert readiness["Williamson"] == "ready_now"
    assert readiness["Bexar"] == "formalize_access"


def test_travis_pipeline_route_returns_bulk_primary_dataset():
    response = client.get("/counties/pipelines/travis")
    assert response.status_code == 200

    payload = response.json()
    assert payload["datasets"][0]["dataset_key"] == "travis_current_export"
    assert payload["datasets"][0]["parser_profile"]["parser_kind"] == "bulk_export_layout"


def test_manifest_inspect_route_classifies_hays_download_page():
    response = client.post(
        "/counties/pipelines/hays/inspect-manifest",
        json={
            "html": """
            <a href='/files/hays-property-export.zip'>2025 Property Data Export Files as of 3-6-2026</a>
            <a href='/files/hays-certified-export.zip'>2025 Certified Export Files</a>
            <a href='/files/hays-gis-shapefile.zip'>GIS Shapefile Download</a>
            """,
            "source_url": "https://hayscad.com/data-downloads/",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert [candidate["dataset_key"] for candidate in payload["dataset_candidates"]] == [
        "hays_property_export",
        "hays_certified_export",
        "hays_gis_bundle",
    ]


def test_prepare_ingestion_route_builds_travis_provider_request():
    response = client.post(
        "/counties/pipelines/travis/prepare-ingestion",
        json={
            "dataset_key": "travis_current_export",
            "source_observed_at": "2026-03-09T00:00:00Z",
            "provider_name": "tcad_current",
            "rows": [
                {
                    "acct": "TRV-001",
                    "situs": "55 Congress Ave",
                    "city": "Austin",
                    "lat": 30.26,
                    "lon": -97.74,
                    "owner": "Travis Owner LLC",
                    "market_value": 650000,
                }
            ],
        },
    )
    assert response.status_code == 200

    payload = response.json()
    prepared = payload["request"]
    assert prepared["provider_type"] == "cad"
    assert prepared["metadata"]["dataset_key"] == "travis_current_export"
    assert prepared["records"][0]["parcel_number"] == "TRV-001"


def test_run_sync_route_returns_artifact_and_provider_run(monkeypatch):
    original_sync_service = county_routes.sync_service
    county_routes.sync_service = FakeSyncService()
    try:
        response = client.post(
            "/counties/pipelines/hays/run-sync",
            json={
                "dataset_key": "hays_property_export",
                "max_records": 1,
                "source_observed_at": "2026-03-09T00:00:00Z",
            },
        )
    finally:
        county_routes.sync_service = original_sync_service

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset_key"] == "hays_property_export"
    assert payload["artifact"]["checksum_sha256"] == "abc123"
    assert payload["provider_ingestion"]["canonical_properties_upserted"] == 1


def test_run_sync_route_blocks_bexar_without_fetching():
    response = client.post("/counties/pipelines/bexar/run-sync", json={})

    assert response.status_code == 400
    assert "not automation-ready" in response.json()["detail"]
