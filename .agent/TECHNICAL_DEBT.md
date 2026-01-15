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

## Agentic Infrastructure

- [ ] **Maintenance Audit Prompt**: Create a generic reusable prompt that conducts audits to see what maintenance or other reusable prompts should be used, or if the `.agent/archive` needs to be decluttered. <!-- id: 501 -->
  - Reason: Ensure the agentic workspace remains clean, efficient, and that common maintenance tasks are standardized through reusable prompts.
  - Priority: Low
  - Notes: This prompt should analyze the state of `.agent/prompts`, `.agent/archive`, and `.agent/artifacts` to suggest cleanup or improvements.
- [ ] **Structured Agentic Multi-Stage Workflow**: Implement a new skill or reusable prompt that formalizes the end-to-end development cycle. <!-- id: 502 -->
  - Reason: Improve consistency and traceability of complex feature implementations by breaking them into discrete, auditable stages.
  - Priority: Medium
  - Notes: The workflow should follow this strict process:
    1. **Clarifying Questions**: Agent asks clarifying questions to fully understand the user's goals/issues.
    2. **Specification & Inspection**: Once the issue is fully specified, use inspection prompts to generate discovery artifacts (output to `.agent/artifacts`). Update backlog and `DEVELOPMENT_MATRIX.md` as appropriate.
    3. **Planning**: Use discovery artifacts to spawn in-depth planning prompts.
    4. **Implementation**: Planning prompts spawn implementation prompts (leveraging templates like `agent_prompt.md`). It is from these prompts that issues are resolved.
    - **Action Item**: Create an artifact template (`.agent/templates/artifact.md`) as we currently lack one.
- [ ] **Project Management Separation of Concerns**: Establish single sources of truth for items at each scale (Roadmap, Matrix, Backlog, Artifacts, Prompts). <!-- id: 503 -->
  - Reason: Prevent desyncing between different levels of project tracking.
  - Priority: Low
  - Notes: Define clear boundaries:
    - `ROADMAP.md`: Strategic phases and high-level milestones.
    - `DEVELOPMENT_MATRIX.md`: Current iteration work items with priority/difficulty.
    - `backlog/`: Detailed tracking of specific issues.
    - `artifacts/`: Design documents and discovery outputs.
    - `prompts/`: actionable execution units.
    - Ensure processes (like the Multi-Stage Workflow) enforce updating the correct document type at the correct stage.

## Schema & Browser Mode

- [ ] **Data Model Alignment**: The `is_reusable` column was removed from the frontend's browser-mode database to match the current backend schema. It needs to be officially added to the backend models and then reintroduced to the frontend. <!-- id: 601 -->
  - Reason: `is_reusable` is used in the frontend UI but is missing from the backend source-of-truth. It was temporarily patched via migration but removed for strict schema compliance.
  - Priority: Medium
  - Notes:
    1. Update Backend `ResourceDefinition` model to include `is_reusable: bool`.
    2. Generate migration (Alembic).
    3. Update `schema.sql` (generated).
    4. Re-enable usage in `SqliteService` (add to `INSERT`, enable in `ResourceDefinition` interface).

## Protocols & Logic

- [ ] **Selective Transfer Heuristic Replacement**: "Selective Transfer" protocols are currently detected via string matching on name/FQN. This must be replaced by formal backend metadata capabilities. <!-- id: 701 -->
  - Reason: Heuristics are brittle. Logic needs to be explicit in `ProtocolDefinition` (e.g. `requires_linked_indices: boolean`).
  - Priority: Low
  - Notes: See `protocol_execution_ux_plan.md` for context.
