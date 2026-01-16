# Agent Prompt: State Inspection Backend - Execution

**Status:** ⚪ Queued
**Priority:** P1
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Hard
**Dependencies:** `01_state_inspection_backend_P.md`, `implementation_plan.md`
**Backlog Reference:** `implementation_plan.md`

---

## 1. The Task

**Objective**: Implement the state inspection backend changes to enable post-run "time travel" for backend-executed protocol runs.

**Context**: Planning phase completed. `implementation_plan.md` contains the detailed steps.

**Goal**: Execute the following:

1. **Schema Update**: Add `state_before_json` and `state_after_json` fields to `FunctionCallLog` model.
2. **Alembic Migration**: Generate and apply migration.
3. **Execution Capture**: Modify `ExecutionMixin` to capture `workcell_runtime.get_state_snapshot()` before/after function calls.
4. **API Endpoint**: Implement `GET /api/v1/protocols/runs/{run_id}/state-history`.
5. **Frontend Integration**: Update `SimulationResultsService.getStateHistory()`.

## 2. Technical Implementation Strategy

**Execution Steps**:

1. **Modify Model** (`praxis/backend/models/domain/protocol.py`):
   ```python
   state_before_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
   state_after_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
   ```

2. **Generate Migration**:
   ```bash
   cd praxis/backend && alembic revision --autogenerate -m "add state snapshots to function_call_log"
   alembic upgrade head
   ```

3. **Modify ExecutionMixin** (`praxis/backend/core/orchestrator/execution.py`):
   - Before function call: `state_before = self.workcell_runtime.get_state_snapshot()`
   - After function call: `state_after = self.workcell_runtime.get_state_snapshot()`
   - Pass to log creation.

4. **Implement API Endpoint** (`praxis/backend/api/endpoints/protocol_runs.py`):
   - Query `FunctionCallLog` for run_id, ordered by sequence.
   - Map to `StateHistory` response model.

5. **Update Frontend Service** (`simulation-results.service.ts`):
   - Detect backend mode and call API instead of local simulation state.

## 3. Context & References

**Relevant Skills**:

- `backend-dev-guidelines` (Alembic, SQLModel, FastAPI)

**Primary Files to Modify**:

| Path | Change |
| :--- | :--- |
| `praxis/backend/models/domain/protocol.py` | Add JSON fields |
| `praxis/backend/core/orchestrator/execution.py` | Capture state |
| `praxis/backend/api/endpoints/protocol_runs.py` | New endpoint |
| `praxis/web-client/src/app/core/services/simulation-results.service.ts` | API integration |

## 4. Constraints & Conventions

- **Execute Changes**: This is an EXECUTION task (Type E).
- **Test Coverage**: Verify state snapshots are captured in DB after protocol run.
- **Backwards Compatible**: Existing runs without state data should return empty history gracefully.

## 5. Verification Plan

**Definition of Done**:

1. Migration applied successfully.
2. Running a protocol populates `state_before_json` / `state_after_json` in `function_call_logs` table.
3. API endpoint returns `StateHistory` with operation snapshots.
4. Frontend State Inspector tab shows timeline for backend runs.

**Test Commands**:
```bash
# Verify migration
uv run alembic current

# Run a test protocol
# Check DB: SELECT state_before_json FROM function_call_logs WHERE protocol_run_id = ?

# Test API
curl http://localhost:8000/api/v1/protocols/runs/{run_id}/state-history
```

---

## On Completion

- [ ] All code changes committed
- [ ] Migration applied and verified
- [ ] Mark this prompt complete in batch README
