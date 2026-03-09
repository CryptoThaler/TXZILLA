from pathlib import Path


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "sql" / "postgis_schema.sql"


def test_postgis_schema_defines_canonical_tables():
    schema_sql = SCHEMA_PATH.read_text()

    required_tables = (
        "properties",
        "assessment_history",
        "ownership_history",
        "listings",
        "transactions",
        "rental_market",
        "environmental_risk",
        "market_features",
        "investment_scores",
        "land_ag_features",
        "provider_runs",
        "provider_run_artifacts",
        "raw_properties",
        "raw_listings",
        "entity_resolution_events",
    )

    for table_name in required_tables:
        assert f"CREATE TABLE IF NOT EXISTS real_estate.{table_name}" in schema_sql


def test_postgis_schema_uses_explicit_srid_and_spatial_indexes():
    schema_sql = SCHEMA_PATH.read_text()

    assert "GEOMETRY(Point, 4326)" in schema_sql
    assert "GEOMETRY(MultiPolygon, 4326)" in schema_sql
    assert "USING GIST" in schema_sql
