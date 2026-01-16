# Agent Prompt: State Inspection Backend - Planning

**Status:** ⚪ Queued
**Priority:** P1
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Medium
**Dependencies:** `01_state_inspection_backend_I.md`, `references/state_inspection_audit.md`
**Backlog Reference:** `implementation_plan.md`

---

## 1. The Task

**Objective**: Plan the schema updates, execution flow modifications, and API endpoint to enable post-run state history retrieval.

**Context**: The inspection phase documented the gaps in `FunctionCallLog` and identified where state snapshots should be captured during execution.

**Goal**: Create a detailed implementation plan covering:

1. **Schema Migration**: Add `state_before_json` and `state_after_json` to `FunctionCallLog`.
2. **Execution Capture**: Modify `ExecutionMixin` to call `get_state_snapshot()` before/after each function call.
3. **API Endpoint**: Design `GET /api/v1/protocols/runs/{run_id}/state-history`.
4. **Frontend Integration**: Update `SimulationResultsService.getStateHistory()` to call backend when not in browser mode.
5. **Serialization Layer**: Plan any transformations needed between PLR format and frontend `DeckView` expectations.

## 2. Technical Implementation Strategy

**Planning Deliverables**:

1. **Alembic Migration Script**: Column additions with nullable defaults.
2. **ExecutionMixin Changes**: Pseudo-code for capture points.
3. **API Response Model**: Pydantic schema for `StateHistory` / `OperationStateSnapshot`.
4. **Risk Mitigations**: Performance (large JSON), data consistency, rollback strategy.

**Output Generation**:

- Update `implementation_plan.md` with detailed step-by-step execution plan.

## 3. Context & References

**Relevant Skills**:

- `backend-dev-guidelines` (Alembic migrations, Pydantic models)

**Primary Files to Modify** (planning only):

| Path | Planned Change |
| :--- | :--- |
| `praxis/backend/models/domain/protocol.py` | Add state JSON fields |
| `praxis/backend/core/orchestrator/execution.py` | Capture state snapshots |
| `praxis/backend/api/endpoints/protocol_runs.py` | New state-history endpoint |
| `praxis/web-client/src/app/core/services/simulation-results.service.ts` | Backend API call |

## 4. Constraints & Conventions

- **Do Not Execute**: This is a PLANNING task (Type P).
- **Scope**: Backend schema + API + Frontend service wiring.
- **Output**: Updated `implementation_plan.md`.

## 5. Verification Plan

**Definition of Done**:

1. `implementation_plan.md` contains step-by-step execution instructions.
2. Migration strategy is documented.
3. API response schema is defined.
4. Prompt `01_state_inspection_backend_E.md` is ready for execution.

---

## On Completion

- [ ] Update `implementation_plan.md` with execution steps
- [ ] Mark this prompt complete in batch README
- [ ] Proceed to `01_state_inspection_backend_E.md`
