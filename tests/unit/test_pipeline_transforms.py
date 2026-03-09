from pipelines.cad_ingestion import ingest_cad
from pipelines.entity_resolution import resolve_entities
from pipelines.mls_ingestion import ingest_mls


def test_cad_ingestion_preserves_lineage_and_region():
    raw_record = {
        "source_name": "cad_bexar",
        "source_record_id": "cad-demo-001",
        "county": "Bexar",
        "parcel_number": "BEX-1001-0001",
        "address": "123 Mission Ridge Dr",
        "city": "San Antonio",
        "latitude": 29.6407,
        "longitude": -98.4822,
        "source_observed_at": "2026-03-01T00:00:00Z",
    }
    output = ingest_cad([raw_record], fetched_at="2026-03-05T00:00:00Z", region_key="central_texas")

    assert output["standardized"][0]["raw_lineage"]["payload"]["parcel_number"] == "BEX-1001-0001"
    assert output["curated"][0]["region_key"] == "central_texas"


def test_cad_ingestion_uses_county_adapter_aliases():
    raw_record = {
        "county": "Hays",
        "source_name": "hays_bulk",
        "prop_id": "hays-demo-001",
        "acct": "HAY-ALIAS-001",
        "situs_address": "100 River Chase",
        "city": "San Marcos",
        "lat": 29.9,
        "lon": -97.9,
        "owner": "Alias Owner LLC",
        "market_value": 355000,
        "year": 2025,
        "source_observed_at": "2026-03-01T00:00:00Z",
    }
    output = ingest_cad([raw_record], fetched_at="2026-03-05T00:00:00Z", region_key="central_texas")

    standardized = output["standardized"][0]
    assert standardized["parcel_number"] == "HAY-ALIAS-001"
    assert standardized["address_line1"] == "100 River Chase"
    assert standardized["assessed_total_value"] == 355000
    assert standardized["owner_name"] == "Alias Owner LLC"


def test_entity_resolution_keeps_low_confidence_address_match_in_review():
    property_record = {
        "property_id": "prop-demo-001",
        "county": "Bexar",
        "parcel_number": "BEX-0001",
        "address_line1": "123 Mission Ridge Dr",
    }
    listing_record = {
        "county": "Bexar",
        "parcel_number": None,
        "address_line1": "123 Mission Ridge Dr",
    }

    result = resolve_entities([property_record], listing_record)
    assert result["match_status"] == "review"
    assert result["confidence"] == 0.78


def test_mls_ingestion_preserves_raw_lineage():
    raw_record = {
        "source_name": "demo_mls",
        "source_record_id": "mls-demo-001",
        "county": "Bexar",
        "address": "123 Mission Ridge Dr",
        "city": "San Antonio",
        "listing_status": "active",
        "list_price": 365000,
        "listed_at": "2026-02-20",
        "source_observed_at": "2026-03-01T00:00:00Z",
    }
    output = ingest_mls([raw_record], fetched_at="2026-03-05T00:00:00Z")

    assert output["standardized"][0]["raw_lineage"]["payload"]["source_record_id"] == "mls-demo-001"
