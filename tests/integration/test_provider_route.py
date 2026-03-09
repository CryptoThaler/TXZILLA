from fastapi.testclient import TestClient

from app.main import app
from app.repositories.provider_repository import ProviderRepository


client = TestClient(app)


def test_provider_ingest_cad_persists_raw_property_run():
    response = client.post(
        "/providers/ingest",
        json={
            "provider_name": "cad_push_demo",
            "provider_type": "cad",
            "records": [
                {
                    "source_name": "cad_bexar",
                    "source_record_id": "cad-live-001",
                    "county": "Bexar",
                    "parcel_number": "BEX-LIVE-001",
                    "address": "10 Live Oak Way",
                    "city": "San Antonio",
                    "latitude": 29.5,
                    "longitude": -98.5,
                    "property_type": "single_family",
                    "bedrooms": 3,
                    "owner_name": "Live Oak Holdings LLC",
                    "ownership_start_date": "2025-01-01",
                    "mailing_address": "10 Live Oak Way, San Antonio, TX 78259",
                    "tax_year": 2025,
                    "assessed_total_value": 340000,
                    "assessed_land_value": 90000,
                    "assessed_improvement_value": 250000,
                    "taxable_value": 325000,
                    "tax_amount_annual": 6900,
                    "source_observed_at": "2026-03-09T00:00:00Z",
                }
            ],
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["run"]["run_status"] == "completed"
    assert payload["stored_raw_properties"] == 1
    assert payload["stored_raw_listings"] == 0
    assert payload["canonical_properties_upserted"] == 1
    assert payload["assessment_records_written"] == 1
    assert payload["ownership_records_written"] == 1

    search_response = client.get("/search", params={"query": "Live Oak"})
    assert search_response.status_code == 200
    search_payload = search_response.json()
    assert search_payload["total"] >= 1
    live_oak = [
        item for item in search_payload["items"] if item["address_line1"] == "10 Live Oak Way"
    ][0]
    assert live_oak["latest_assessment"]["assessed_total_value"] == 340000.0

    analyze_response = client.get(f"/analyze/{live_oak['property_id']}")
    assert analyze_response.status_code == 200
    analyze_payload = analyze_response.json()
    assert analyze_payload["property"]["latest_assessment"]["tax_year"] == 2025
    assert analyze_payload["investment"]["acquisition_basis"] == 340000.0


def test_provider_ingest_cad_accepts_county_specific_aliases():
    response = client.post(
        "/providers/ingest",
        json={
            "provider_name": "hays_bulk_demo",
            "provider_type": "cad",
            "records": [
                {
                    "county": "Hays",
                    "source_name": "hayscad",
                    "prop_id": "hays-live-002",
                    "acct": "HAY-LIVE-002",
                    "situs_address": "44 Blanco Bend",
                    "city": "San Marcos",
                    "lat": 29.88,
                    "lon": -97.94,
                    "owner": "Hays Owner LLC",
                    "market_value": 375000,
                    "year": 2025,
                    "source_observed_at": "2026-03-09T00:00:00Z",
                }
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["canonical_properties_upserted"] == 1

    search_response = client.get("/search", params={"query": "Blanco Bend"})
    assert search_response.status_code == 200
    search_payload = search_response.json()
    assert any(item["address_line1"] == "44 Blanco Bend" for item in search_payload["items"])


def test_provider_ingest_listing_feed_returns_match_status_and_run_listing():
    response = client.post(
        "/providers/ingest",
        json={
            "provider_name": "mls_push_demo",
            "provider_type": "mls",
            "records": [
                {
                    "source_name": "demo_mls",
                    "source_record_id": "mls-live-001",
                    "county": "Bexar",
                    "parcel_number": "BEX-1001-0001",
                    "address": "123 Mission Ridge Dr",
                    "city": "San Antonio",
                    "listing_status": "active",
                    "list_price": 369000,
                    "listed_at": "2026-03-09",
                    "source_observed_at": "2026-03-09T00:00:00Z",
                }
            ],
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["stored_raw_listings"] == 1
    assert payload["canonical_properties_upserted"] == 0
    assert payload["matched_records"] == 1
    assert payload["review_records"] == 0

    runs_response = client.get("/providers/runs")
    assert runs_response.status_code == 200
    runs_payload = runs_response.json()
    assert any(run["provider_name"] == "mls_push_demo" for run in runs_payload)


def test_provider_artifact_routes_return_stored_run_artifacts():
    response = client.post(
        "/providers/ingest",
        json={
            "provider_name": "cad_artifact_demo",
            "provider_type": "cad",
            "records": [
                {
                    "county": "Travis",
                    "source_name": "tcad",
                    "acct": "TRV-ART-001",
                    "situs": "1 Artifact Way",
                    "city": "Austin",
                    "lat": 30.27,
                    "lon": -97.74,
                    "owner": "Artifact Owner LLC",
                    "market_value": 515000,
                    "year": 2025,
                    "source_observed_at": "2026-03-09T00:00:00Z",
                }
            ],
        },
    )
    assert response.status_code == 200
    run_id = response.json()["run"]["provider_run_id"]

    repository = ProviderRepository()
    repository.store_run_artifact(
        provider_run_id=run_id,
        county="Travis",
        dataset_key="travis_current_export",
        source_url="https://traviscad.org/exports/travis-roll.zip",
        local_path="/tmp/travis-roll.zip",
        checksum_sha256="artifact-checksum-001",
        media_type="application/zip",
        bytes_downloaded=1024,
    )

    artifact_response = client.get(f"/providers/runs/{run_id}/artifacts")
    assert artifact_response.status_code == 200
    artifacts = artifact_response.json()
    assert len(artifacts) == 1
    assert artifacts[0]["dataset_key"] == "travis_current_export"

    filtered_response = client.get(
        "/providers/artifacts",
        params={"county": "Travis", "dataset_key": "travis_current_export"},
    )
    assert filtered_response.status_code == 200
    filtered = filtered_response.json()
    assert any(item["provider_run_id"] == run_id for item in filtered)
