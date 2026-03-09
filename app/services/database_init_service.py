from pathlib import Path
from typing import Optional

from sqlalchemy.engine import Engine

from app.database import get_engine
from app.models.provider_models import get_provider_tables
from app.models.public_record_models import get_public_record_tables
from app.schemas.bootstrap_schema import BootstrapExecutionResponse


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "sql" / "postgis_schema.sql"


def _split_sql_statements(sql_text: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
    trailing = "\n".join(current).strip()
    if trailing:
        statements.append(trailing)
    return statements


class DatabaseInitService:
    def __init__(self, engine: Optional[Engine] = None) -> None:
        self.engine = engine or get_engine()

    def bootstrap(self) -> BootstrapExecutionResponse:
        schema_path = _schema_path()
        if self.engine.dialect.name == "sqlite":
            self._bootstrap_sqlite_metadata()
            return BootstrapExecutionResponse(
                mode="sqlite_metadata",
                schema_path=str(schema_path),
                statements_executed=2,
                detail="SQLite bootstrap created runtime metadata tables for local development and tests.",
            )

        statements = _split_sql_statements(schema_path.read_text(encoding="utf-8"))
        with self.engine.begin() as connection:
            for statement in statements:
                connection.exec_driver_sql(statement)
        return BootstrapExecutionResponse(
            mode="postgres_sql_script",
            schema_path=str(schema_path),
            statements_executed=len(statements),
            detail="Applied PostgreSQL/PostGIS bootstrap SQL script.",
        )

    def _bootstrap_sqlite_metadata(self) -> None:
        public_tables = get_public_record_tables(None)
        provider_tables = get_provider_tables(None)
        public_tables["metadata"].create_all(self.engine)
        provider_tables["metadata"].create_all(self.engine)
