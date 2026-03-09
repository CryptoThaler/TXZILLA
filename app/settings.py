from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TXZILLA API"
    app_version: str = "0.2.0"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "sqlite+pysqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/0"
    app_timezone: str = "America/Chicago"
    county_download_dir: str = "/tmp/txzilla-county-downloads"
    enable_background_jobs: bool = True
    county_sync_task_enabled: bool = True
    county_sync_interval_hours: int = 24
    enable_demo_data: bool = True
    enable_geospatial_features: bool = True
    enable_startup_db_check: bool = True
    auto_bootstrap_on_startup: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
