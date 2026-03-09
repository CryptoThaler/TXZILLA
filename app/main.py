from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes.analysis import router as analysis_router
from app.routes.counties import router as counties_router
from app.routes.health import router as health_router
from app.routes.providers import router as providers_router
from app.routes.regions import router as regions_router
from app.routes.search import router as search_router
from app.routes.score import router as score_router
from app.services.health_service import get_health_report
from app.services.runtime_service import initialize_runtime
from app.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.bootstrap_execution = initialize_runtime(settings=settings)
    app.state.startup_health = (
        get_health_report() if settings.enable_startup_db_check else None
    )
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(counties_router)
    app.include_router(regions_router)
    app.include_router(search_router)
    app.include_router(analysis_router)
    app.include_router(providers_router)
    app.include_router(score_router)
    return app


app = create_app()
