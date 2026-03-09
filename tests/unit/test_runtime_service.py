from app.schemas.bootstrap_schema import BootstrapExecutionResponse
from app.services.runtime_service import initialize_runtime
from app.settings import Settings


class FakeDatabaseInitService:
    def bootstrap(self) -> BootstrapExecutionResponse:
        return BootstrapExecutionResponse(
            mode="sqlite_metadata",
            schema_path="/tmp/schema.sql",
            statements_executed=2,
            detail="bootstrapped",
        )


def test_initialize_runtime_skips_bootstrap_when_disabled():
    result = initialize_runtime(
        settings=Settings(auto_bootstrap_on_startup=False),
        init_service=FakeDatabaseInitService(),
    )

    assert result is None


def test_initialize_runtime_runs_bootstrap_when_enabled():
    result = initialize_runtime(
        settings=Settings(auto_bootstrap_on_startup=True),
        init_service=FakeDatabaseInitService(),
    )

    assert result is not None
    assert result.detail == "bootstrapped"
