# CODEBASE_MAP.md

## Primary directories
- `app/` API, services, repositories, schemas, agents
- `pipelines/` ingestion and transformations
- `sql/` schema and migrations
- `tests/` unit, integration, regression
- `config/` YAML config

## Dependency direction
routes -> services -> repositories -> database
agents -> services -> repositories
pipelines -> repositories or sql
