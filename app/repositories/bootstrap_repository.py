from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_engine


REQUIRED_EXTENSIONS = ("postgis", "uuid-ossp")
REQUIRED_SCHEMA = "real_estate"
REQUIRED_TABLES = (
    "properties",
    "listings",
    "transactions",
    "rental_market",
    "environmental_risk",
    "market_features",
    "investment_scores",
    "land_ag_features",
)


@dataclass(frozen=True)
class DatabaseBootstrapInspection:
    dialect: str
    reachable: bool = False
    bootstrap_verified: bool = False
    bootstrap_ready: bool = False
    required_extensions: list[str] = field(default_factory=lambda: list(REQUIRED_EXTENSIONS))
    present_extensions: list[str] = field(default_factory=list)
    required_schema: str = REQUIRED_SCHEMA
    schema_present: bool = False
    required_tables: list[str] = field(default_factory=lambda: list(REQUIRED_TABLES))
    present_tables: list[str] = field(default_factory=list)
    missing_tables: list[str] = field(default_factory=lambda: list(REQUIRED_TABLES))
    detail: str = "Database connection has not been checked yet."


class DatabaseBootstrapRepository:
    def __init__(self, engine: Optional[Engine] = None) -> None:
        self.engine = engine or get_engine()

    def inspect_bootstrap(self) -> DatabaseBootstrapInspection:
        dialect = self.engine.dialect.name

        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

                if dialect != "postgresql":
                    return DatabaseBootstrapInspection(
                        dialect=dialect,
                        reachable=True,
                        detail=(
                            f"Connected to {dialect}; PostGIS bootstrap verification "
                            "runs only against PostgreSQL."
                        ),
                    )

                present_extensions = sorted(
                    row[0]
                    for row in connection.execute(text("SELECT extname FROM pg_extension"))
                    if row[0] in REQUIRED_EXTENSIONS
                )
                schema_present = bool(
                    connection.execute(
                        text(
                            """
                            SELECT 1
                            FROM information_schema.schemata
                            WHERE schema_name = :schema_name
                            """
                        ),
                        {"schema_name": REQUIRED_SCHEMA},
                    ).scalar()
                )
                present_tables = sorted(
                    row[0]
                    for row in connection.execute(
                        text(
                            """
                            SELECT table_name
                            FROM information_schema.tables
                            WHERE table_schema = :schema_name
                            """
                        ),
                        {"schema_name": REQUIRED_SCHEMA},
                    )
                    if row[0] in REQUIRED_TABLES
                )
                missing_tables = sorted(
                    table_name
                    for table_name in REQUIRED_TABLES
                    if table_name not in present_tables
                )
                bootstrap_ready = (
                    schema_present
                    and len(present_extensions) == len(REQUIRED_EXTENSIONS)
                    and not missing_tables
                )

                return DatabaseBootstrapInspection(
                    dialect=dialect,
                    reachable=True,
                    bootstrap_verified=True,
                    bootstrap_ready=bootstrap_ready,
                    present_extensions=present_extensions,
                    schema_present=schema_present,
                    present_tables=present_tables,
                    missing_tables=missing_tables,
                    detail=(
                        "PostGIS bootstrap verified."
                        if bootstrap_ready
                        else "Database reachable, but bootstrap is incomplete."
                    ),
                )
        except SQLAlchemyError as exc:
            return DatabaseBootstrapInspection(
                dialect=dialect,
                detail=f"Database check failed: {exc.__class__.__name__}: {exc}",
            )
