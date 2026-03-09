from app.database import get_engine
from app.repositories.bootstrap_repository import DatabaseBootstrapRepository
from app.services.health_service import get_health_report


def test_database_bootstrap_repository_reports_sqlite_as_unverified_postgis():
    repository = DatabaseBootstrapRepository(
        engine=get_engine("sqlite+pysqlite:///:memory:")
    )
    inspection = repository.inspect_bootstrap()

    assert inspection.reachable is True
    assert inspection.bootstrap_verified is False
    assert inspection.bootstrap_ready is False
    assert inspection.dialect == "sqlite"
    assert "PostGIS bootstrap verification" in inspection.detail


def test_health_report_keeps_service_ok_for_reachable_non_postgres_dev_bootstrap():
    repository = DatabaseBootstrapRepository(
        engine=get_engine("sqlite+pysqlite:///:memory:")
    )
    report = get_health_report(repository=repository)

    assert report.status == "ok"
    assert report.database.bootstrap_ready is False
    assert report.database.bootstrap_verified is False
