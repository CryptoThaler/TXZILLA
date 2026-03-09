from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.services.database_init_service import DatabaseInitService


def test_database_init_service_bootstraps_sqlite_runtime_metadata():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    response = DatabaseInitService(engine=engine).bootstrap()

    assert response.mode == "sqlite_metadata"
    assert response.statements_executed == 2

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert "properties" in tables
    assert "assessment_history" in tables
    assert "ownership_history" in tables
    assert "provider_runs" in tables
    assert "provider_run_artifacts" in tables
