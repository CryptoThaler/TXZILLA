# AGENTS.md

## Mission
Build and maintain TXZILLA as a deterministic, geospatially aware, agentic real estate intelligence platform for Texas.

## Read first
1. `PLANS.md`
2. `ARCHITECTURE.md`
3. `MODEL_SPEC.md`
4. `DATA_PIPELINE_SPEC.md`
5. `CODEBASE_MAP.md`
6. `SERVICE_BOUNDARY_SPEC.md`
7. `DATA_SCHEMA_REFERENCE.md`
8. `AGENT_ORCHESTRATION_SPEC.md`
9. `IMPLEMENT.md`
10. `DOCUMENTATION.md`

## Global priorities
1. correctness
2. reproducibility
3. geospatial integrity
4. risk-aware underwriting
5. maintainability
6. test coverage
7. documentation completeness

## Global rules
- business logic belongs in services
- route handlers stay thin
- repositories own persistence access
- pipelines preserve lineage and freshness
- deterministic formulas must be auditable
- DeFAI scenarios are overlays only, not baseline underwriting
- update docs when architecture or formulas change
- add tests for any deterministic behavior change

## Directory guidance
More specific `AGENTS.md` files in subdirectories override this file locally while this policy remains in force.
