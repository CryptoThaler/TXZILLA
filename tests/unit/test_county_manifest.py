from pipelines.county_manifest import build_manifest_snapshot
from pipelines.county_procedures import build_provider_request_from_county_export


def test_hays_manifest_discovers_primary_datasets():
    html = """
    <html><body>
      <a href="/files/hays-property-export.zip">2025 Property Data Export Files as of 3-6-2026</a>
      <a href="/files/hays-certified-export.zip">2025 Certified Export Files</a>
      <a href="/files/hays-gis-shapefile.zip">GIS Shapefile Download</a>
    </body></html>
    """
    snapshot = build_manifest_snapshot("hays", html, "https://hayscad.com/data-downloads/")

    dataset_keys = [candidate.dataset_key for candidate in snapshot.dataset_candidates]
    assert dataset_keys == [
        "hays_property_export",
        "hays_certified_export",
        "hays_gis_bundle",
    ]


def test_travis_manifest_discovers_current_certified_and_supplemental():
    html = """
    <html><body>
      <a href="/exports/travis-roll.zip">2025 Appraisal Roll Export</a>
      <a href="/exports/travis-certified.zip">2025 Certified Export</a>
      <a href="/exports/travis-supplemental.zip">2025 Supplemental Export</a>
    </body></html>
    """
    snapshot = build_manifest_snapshot("travis", html, "https://traviscad.org/publicinformation/")

    dataset_keys = [candidate.dataset_key for candidate in snapshot.dataset_candidates]
    assert dataset_keys == [
        "travis_current_export",
        "travis_certified_export",
        "travis_supplemental_export",
    ]


def test_williamson_prepare_request_normalizes_export_rows():
    request = build_provider_request_from_county_export(
        county="williamson",
        dataset_key="williamson_current_export",
        rows=[
            {
                "acct": "WIL-001",
                "property_address": "100 County Line Rd",
                "city": "Round Rock",
                "lat": 30.5,
                "lon": -97.6,
                "owner": "Williamson Owner LLC",
                "market_value": 410000,
            }
        ],
        source_observed_at="2026-03-09T00:00:00Z",
        provider_name="wcad_current",
    )

    assert request.region_key == "central_texas"
    assert request.metadata["dataset_key"] == "williamson_current_export"
    assert request.records[0]["parcel_number"] == "WIL-001"
    assert request.records[0]["address"] == "100 County Line Rd"
    assert request.records[0]["assessed_total_value"] == 410000
