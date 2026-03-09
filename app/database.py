from functools import lru_cache
from typing import Any, Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.settings import get_settings


def _build_engine_kwargs(database_url: str) -> dict[str, Any]:
    engine_kwargs: dict[str, Any] = {"future": True, "pool_pre_ping": True}

    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in database_url:
            engine_kwargs["poolclass"] = StaticPool

    return engine_kwargs


@lru_cache(maxsize=4)
def get_engine(database_url: Optional[str] = None) -> Engine:
    resolved_database_url = database_url or get_settings().database_url
    return create_engine(
        resolved_database_url,
        **_build_engine_kwargs(resolved_database_url),
    )


@lru_cache(maxsize=4)
def get_session_factory(
    database_url: Optional[str] = None,
) -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(database_url),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )


def get_db() -> Generator[Session, None, None]:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
