# DOCUMENTATION.md

## Status
Milestone 1 and Milestone 2 scaffold extended and validated.

## Current assumptions
- initial geography is Central Texas
- expansion to DFW and Greater Houston will be config-driven
- baseline underwriting is deterministic
- geospatial context is mandatory in production scoring

## Change log
### Initial scaffold
- created root docs
- created app/runtime skeleton
- created test skeleton
- created Codex skill folders

### Bootstrap hardening
- replaced the direct global FastAPI instantiation with an app factory and lifespan bootstrap
- centralized settings loading with a cached `get_settings()` entry point
- hardened SQLAlchemy engine/session bootstrap for SQLite test runs and pooled runtime use
- added a service-backed `/health` response model that reports environment, version, and database bootstrap state

### Database bootstrap verification
- added a repository that verifies database reachability, required extensions, schema presence, and canonical table presence
- startup now records a bootstrap health snapshot without pushing persistence logic into routes
- validation now distinguishes between reachable development SQLite and verified PostgreSQL/PostGIS bootstrap

### SQL schema expansion
- extended `sql/postgis_schema.sql` from extensions-only setup to canonical `real_estate` tables
- added explicit SRID 4326 geometry columns for property, rental, market, environmental, and land/ag data
- added primary keys, foreign keys, deterministic score audit columns, freshness/provenance columns, checks, and GIST/filter indexes

### Application build-out
- added seed-backed repositories for canonical properties, listings, transactions, market context, land features, and environmental risk
- implemented search, property detail, region, valuation, risk, land transition, market intelligence, and report services
- added thin `/search`, `/properties/{property_id}`, `/regions`, and `/analyze/{property_id}` routes on top of the service layer
- built the standard orchestration chain and the core agents listed in `AGENT_ORCHESTRATION_SPEC.md`
- added CAD and MLS ingestion transforms plus deterministic entity resolution with explicit low-confidence review behavior

### Provider pipeline
- added raw provider ingestion SQL tables for `provider_runs`, `raw_properties`, `raw_listings`, and `entity_resolution_events`
- added a push-based provider ingestion service and thin `/providers/ingest` and `/providers/runs` routes
- provider input now records run metadata, persists raw payloads, stores standardized payloads, and emits deterministic resolution outcomes for listing feeds

### Public-records-first pivot
- added canonical public-record support for `assessment_history` and `ownership_history`
- added persistence-backed public record repositories and CAD upsert hooks for canonical `properties`
- property search now merges public-record-backed properties with the existing demo catalog
- CAD ingestion can now create searchable, analyzable properties even without an active listing, using assessment history as the valuation/acquisition anchor

### County adapter framework
- added county adapter registry and ingestion plans for Bexar, Hays, Travis, and Williamson
- CAD ingestion now runs county-specific alias normalization and exact parcel validation before canonical mapping
- exposed `/counties/adapters` and `/counties/adapters/{county}` so the ingestion workflow and official source priorities are inspectable
- documented Bexar as a formalized-request county: use BCAD public-information request and clerk backfill while bulk export delivery is being established

### County pipeline planning
- added executable county pipeline plans for Hays, Travis, Williamson, and Bexar
- Hays, Travis, and Williamson are marked `ready_now` with dataset manifests, parser profiles, and next execution steps
- Bexar is explicitly marked `formalize_access` so it stays separate from the self-serve bulk counties
- exposed `/counties/pipelines` and `/counties/pipelines/{county}` for implementation-ready county execution plans

### County execution procedures
- added county manifest discovery to classify official county download-page links into known dataset keys
- added county export preparation procedures that turn Hays, Travis, and Williamson bulk-export rows into canonical CAD/provider-ingestion payloads
- exposed `/counties/pipelines/{county}/inspect-manifest` and `/counties/pipelines/{county}/prepare-ingestion` for operator-side execution support

### Autonomous county sync
- added a county fetch client that retrieves official county manifest pages and bulk export artifacts directly from Hays, Travis, and Williamson sources
- added local artifact persistence with SHA-256 checksums and per-county/per-dataset storage paths so every autonomous run preserves file lineage
- added a layout-bound delimited parser that reads posted ZIP/TXT/CSV appraisal exports and rejects runs when required parcel/account bindings are missing
- added a service-backed `/counties/pipelines/{county}/run-sync` endpoint that fetches the manifest, selects an automation-safe dataset, downloads the export, parses it, pushes canonical CAD records through provider ingestion, and stores the artifact record against the resulting provider run
- autonomous sync now supports explicit `dataset_key` selection for counties with multiple bulk feeds, including Williamson historical backfill datasets
- Bexar remains blocked from autonomous sync because the county plan is still `formalize_access`; the runtime returns an error instead of falling back to an interactive or unofficial path

### Deployment bootstrap and operations
- added `DatabaseInitService` plus `python -m app.bootstrap` so deployment can apply the canonical SQL bootstrap on PostgreSQL/PostGIS and create runtime metadata tables for local SQLite development
- extended provider persistence and service APIs to expose run artifacts, making county-download lineage queryable through `/providers/runs/{provider_run_id}/artifacts` and `/providers/artifacts`
- expanded the Celery worker from a stub into executable county-sync tasks so scheduled jobs can run deterministic county ingests through the service layer instead of embedding logic in the worker module
- added `.env.example` with deployment-oriented defaults for PostgreSQL, Redis, and county artifact storage
- aligned CI and the production container to the validated Python 3.9 runtime, and disabled matrix fail-fast so future GitHub failures preserve full job signal

### Runtime packaging and probes
- added `auto_bootstrap_on_startup` runtime initialization so containerized API startup can apply the bootstrap path automatically when enabled
- added `/live` and `/ready` routes; `/ready` returns HTTP 503 when the runtime is up but the database/bootstrap state is degraded
- added Celery beat schedule configuration from settings so ready county syncs can run on a fixed interval without hand wiring schedule code in deployment
- added a production Dockerfile, `.dockerignore`, and expanded `docker-compose.yml` to include API, worker, beat, PostGIS, Redis, and a shared county-artifact volume

### GitHub release and runtime manifests
- added a `Release Image` GitHub Actions workflow that builds and publishes TXZILLA images to GHCR on `main`, tags, and manual dispatch
- added `deploy/docker-compose.runtime.yml` so runtime hosts can pull published GHCR images instead of rebuilding locally
- added `deploy/runtime.env.example` to separate runtime host configuration from developer-local `.env`
- added `deploy/README.md` with the host-side procedure for pulling the image, running bootstrap, and starting the API/worker/beat stack

### GitHub smoke demonstration
- added a `Smoke Demo` workflow that runs on `main` pushes or manual dispatch, boots a deterministic file-backed runtime in GitHub Actions, starts the API, runs a deterministic HTTP smoke flow, and uploads demo artifacts
- added `scripts/smoke_demo.py` to demonstrate runtime probes, provider ingest, DB-backed search, provider run audit, provider artifact audit, county pipeline inspection, and the intentionally blocked Bexar sync path
- hardened the smoke-demo script so non-JSON HTTP failures are reported with status and body snippets instead of a generic JSON decode traceback
- added `artifacts/` to `.gitignore` so local and GitHub demo outputs are not committed

## Deployment procedure
1. Copy `.env.example` into a real environment file or deployment secret store and set production values.
2. Provision PostgreSQL with PostGIS and Redis.
3. Run `python -m app.bootstrap` against the production `DATABASE_URL`.
4. Start the API with `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
5. Start the worker with `celery -A app.worker.celery_app worker --loglevel=info`.
6. Trigger county sync tasks through Celery or the HTTP county-sync endpoint for Hays, Travis, and Williamson.
7. Monitor `/health`, `/providers/runs`, and `/providers/artifacts` for bootstrap and ingestion status.

## GitHub runtime deployment procedure
1. Push the repo to GitHub.
2. Allow the `Release Image` workflow to publish the GHCR image.
3. Copy `deploy/runtime.env.example` to `deploy/runtime.env` on the runtime host.
4. Set `TXZILLA_IMAGE` to the published GHCR tag.
5. Run `docker compose --env-file deploy/runtime.env -f deploy/docker-compose.runtime.yml up -d`.
6. Validate `/live`, `/ready`, and `/providers/runs` on the deployed host.

### Tests
- fixed schema typing for Python 3.9-compatible test collection
- pinned `shapely` to a Python 3.9-compatible release for local bootstrap/test installs
- expanded scoring tests to cover deterministic score output and default assumption logging
- added database bootstrap, search, analysis, valuation, risk, region, and pipeline contract tests
- added county parser tests for ZIP layout parsing and required-binding failures
- added county sync service and route tests for autonomous Hays/Williamson bulk runs, artifact persistence, and the blocked Bexar path
- added database-init, worker-task, and provider-artifact audit tests for deployment-stage runtime surfaces
- added runtime-bootstrap, liveness/readiness, and Celery schedule configuration tests
