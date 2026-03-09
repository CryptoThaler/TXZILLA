# SERVICE_BOUNDARY_SPEC.md

## Ownership
- routes: HTTP parsing and response shaping
- services: deterministic business logic
- repositories: persistence access
- pipelines: ingestion and transformation
- agents: orchestration only

## Anti-patterns
- formulas in routes
- raw adapter logic in repositories
- undocumented business logic in SQL views
