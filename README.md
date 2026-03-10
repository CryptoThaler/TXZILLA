# TXZILLA

TXZILLA is a Codex-optimized, agentic real estate intelligence scaffold for Texas property search, underwriting, environmental risk analysis, land transition modeling, and regional expansion.

## Initial region
- San Antonio
- New Braunfels
- Seguin
- San Marcos
- Kyle
- Buda
- Austin

## Core stack
- FastAPI
- PostgreSQL + PostGIS
- SQLAlchemy
- Redis + Celery
- Python 3.9 runtime
- Pytest
- YAML-based configuration
- Codex repo guidance via AGENTS.md and Skills

## Quick start
1. Copy `.env.example` to `.env`
2. Start the full stack with `docker compose up --build`
3. For local non-container development, install dependencies with `pip install -r requirements.txt`
4. Bootstrap the database with `python -m app.bootstrap`
5. Run the API with `uvicorn app.main:app --reload`
6. Run the worker with `celery -A app.worker.celery_app worker --loglevel=info`
7. Run tests with `pytest`

## GitHub release flow
1. Push the repo to GitHub.
2. The `Release Image` workflow publishes `ghcr.io/<owner>/txzilla`.
3. Deploy the published image with the manifests in [deploy/README.md](deploy/README.md) and [deploy/docker-compose.runtime.yml](deploy/docker-compose.runtime.yml).

## GitHub demo flow
1. Open the `Smoke Demo` workflow in GitHub Actions.
2. Run it manually with `workflow_dispatch`.
3. Download the `smoke-demo-artifacts` artifact to inspect:
   - `smoke-demo.json`
   - `uvicorn.log`

## Runtime endpoints
- `/live` liveness probe
- `/ready` readiness probe with database/bootstrap status
- `/health` detailed health report
- `/providers/runs` ingestion run history
- `/providers/artifacts` county/provider artifact lineage

## Codex operating order
1. Read `AGENTS.md`
2. Read `PLANS.md`
3. Read `ARCHITECTURE.md`, `MODEL_SPEC.md`, `DATA_PIPELINE_SPEC.md`
4. Implement the current milestone
5. Update `DOCUMENTATION.md`
