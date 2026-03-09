from typing import Optional

from app.schemas.bootstrap_schema import BootstrapExecutionResponse
from app.services.database_init_service import DatabaseInitService
from app.settings import Settings, get_settings


def initialize_runtime(
    settings: Optional[Settings] = None,
    init_service: Optional[DatabaseInitService] = None,
) -> Optional[BootstrapExecutionResponse]:
    resolved_settings = settings or get_settings()
    if not resolved_settings.auto_bootstrap_on_startup:
        return None
    return (init_service or DatabaseInitService()).bootstrap()
