# Technical Debt

This document tracks known issues, temporary patches, and required follow-up work for the Praxis project.

## Models & Database

- [ ] **SQLModel/PostgreSQL Verification**: Unified `PraxisBase` and Alembic metadata integration have only been verified against SQLite. Full verification against a live PostgreSQL instance is required when infrastructure is available. <!-- id: 101 -->
- [ ] **Silence SQLModel Field Shadowing Warnings**: Silence `UserWarning: Field name "..." in "..." shadows an attribute in parent "..."`. <!-- id: 102 -->
  - Reason: Field re-declarations (e.g., `deck_accession_id` in `DeckRead`) are necessary for the current architecture but trigger runtime warnings in SQLModel.
  - Priority: Medium
  - Notes: Investigate using `warnings.filterwarnings` or SQLModel configuration to suppress these specific shadowing warnings while keeping other warnings active.

## Tests

- [ ] Review REPL tests in `tests/core/test_repl_session.py` and migrate them to a frontend/integration test suite; these tests require PyLabRobot runtime and interactive imports and are skipped in backend CI.<!-- id: 201 -->
  - Reason: REPL depends on environment and GUI/interactive backends that belong to integration or frontend testing.
  - Owner: TBD
  - Priority: low
  - Notes: Consider creating a small Docker-based integration job that installs `pylabrobot` and runs these tests in an environment that can import hardware simulation backends.

## Backend Sync

- [ ] **Backend Test & File Sync**: Update backend tests and files implicated by recent schema and naming convention changes (e.g., `_json` suffix alignment and `ProtocolRunRead` field additions). <!-- id: 301 -->
  - Reason: Frontend schema alignment (SQLModel unification) has introduced discrepancies in backend expectations.
  - Priority: Medium
  - Notes: Ensure that all backend repositories, services, and tests are updated to handle the new field names and consistent JSONB suffixing.

## Frontend / Web Client

- [ ] **Audit "as any" Usage**: unexpected uses of `any` and `as any` have proliferated in the web client codebase, particularly in services interfacing with the API (e.g., `simulation-results.service.ts`). <!-- id: 401 -->
  - Reason: Urgent schema alignment required bypassing some type checks. These patches reduce type safety and need to be resolved by proper type definitions.
  - Priority: Medium
  - Notes: Search for `as any` and `: any` in `praxis/web-client/src`. Replace with proper types from `schema.ts` or dedicated interfaces.
