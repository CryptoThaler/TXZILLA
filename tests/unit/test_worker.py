from celery import Celery

from app.schemas.county_sync_schema import CountySyncResponse
from app.settings import Settings
from app.worker import configure_celery_app, run_county_sync_task, run_ready_county_syncs_task


class FakeCountyJobService:
    def run_county_sync(self, county, request):
        assert county == "hays"
        assert request.dataset_key == "hays_property_export"
        return CountySyncResponse.model_validate(
            {
                "county": "Hays",
                "dataset_key": "hays_property_export",
                "manifest_source_url": "https://hayscad.com/data-downloads/",
                "artifact": {
                    "source_url": "https://hayscad.com/files/hays-property-export.zip",
                    "local_path": "/tmp/hays.zip",
                    "checksum_sha256": "demo-checksum",
                    "media_type": "application/zip",
                    "bytes_downloaded": 128,
                },
                "provider_ingestion": {
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
            }
        )

    def run_ready_county_syncs(self):
        return [
            self.run_county_sync("hays", type("Request", (), {"dataset_key": "hays_property_export"})())
        ]


def test_run_county_sync_task_delegates_to_job_service(monkeypatch):
    monkeypatch.setattr("app.worker.CountyJobService", FakeCountyJobService)

    payload = run_county_sync_task(
        "hays",
        {"dataset_key": "hays_property_export"},
    )

    assert payload["county"] == "Hays"
    assert payload["dataset_key"] == "hays_property_export"
    assert payload["provider_ingestion"]["canonical_properties_upserted"] == 1


def test_run_ready_county_syncs_task_serializes_all_ready_runs(monkeypatch):
    monkeypatch.setattr("app.worker.CountyJobService", FakeCountyJobService)

    payload = run_ready_county_syncs_task()

    assert len(payload) == 1
    assert payload[0]["county"] == "Hays"


def test_configure_celery_app_sets_county_sync_schedule():
    celery = configure_celery_app(
        Celery("txzilla-test", broker="redis://localhost:6379/0"),
        Settings(
            county_sync_interval_hours=12,
            enable_background_jobs=True,
            county_sync_task_enabled=True,
        ),
    )

    schedule = celery.conf.beat_schedule["county-ready-syncs"]
    assert schedule["task"] == "txzilla.counties.run_ready_syncs"
    assert schedule["schedule"] == 43200
