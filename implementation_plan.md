# Implementation Plan - State Inspection & Reporting Enhancement

**Objective:** Enable real-time state inspection and post-run "time travel" for backend-executed protocol runs.

## 1. Backend Schema Updates

### 1.1. Update `FunctionCallLog` Model
Modify `praxis/backend/models/domain/protocol.py` to include state snapshots.

```python
class FunctionCallLog(FunctionCallLogBase, table=True):
    # ... existing fields ...
    state_before_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
    state_after_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
```

### 1.2. Update `ExecutionMixin`
Modify `praxis/backend/core/orchestrator/execution.py` in `_execute_protocol_main_logic` (or the wrapper).
- Capture `workcell_runtime.get_state_snapshot()` before calling the function.
- Capture `workcell_runtime.get_state_snapshot()` after calling the function.
- Pass these to `log_function_call_start` and `log_function_call_end` (or update log entry).

## 2. Backend API Implementation

### 2.1. New Endpoint: Get State History
Create `GET /api/v1/protocols/runs/{run_id}/state-history` in `praxis/backend/api/endpoints/protocol_runs.py`.
- **Response Model:** `StateHistory` (from `praxis/backend/models/domain/simulation.py` - need to verify/create if missing, or use Pydantic model matching frontend `StateHistory`).
- **Logic:**
    - Fetch `ProtocolRun` by ID.
    - Fetch associated `FunctionCallLog` entries, ordered by sequence.
    - Map logs to `OperationStateSnapshot`.
    - Return `StateHistory` object.

## 3. Frontend Integration

### 3.1. Update `SimulationResultsService`
Modify `praxis/web-client/src/app/core/services/simulation-results.service.ts`.
- Update `getStateHistory` to call the new backend API endpoint when not in browser mode.

## 4. Verification

1.  **Execute a Protocol** (in backend mode).
2.  **Verify DB:** Check `function_call_logs` table has populated JSON in `state_before/after` columns.
3.  **Verify UI:** Go to "State Inspector" tab in Run Details. Timeline should populate. Clicking steps should show deck state.

## 5. Risk Mitigation

-   **Performance:** Full state snapshots can be large.
    -   *Mitigation:* For now, accept the overhead (sqlite/postgres can handle it for typical run sizes). Future optimization: delta compression.
-   **Data Consistency:** Ensure `get_state_snapshot()` returns the exact format expected by frontend `DeckView`.
    -   *Mitigation:* Check PLR serialization. `DeckView` handles `volumes` (list) or `liquid_mask`. If PLR returns `liquids` (tuple list), we might need a transformation layer in `WorkcellRuntime.get_state_snapshot` or `ExecutionMixin`.

## 6. Execution Steps (Batch E)

1.  Modify Backend Models (`protocol.py`).
2.  Generate Alembic Migration (`alembic revision --autogenerate`).
3.  Apply Migration (`alembic upgrade head`).
4.  Modify `ExecutionMixin` to capture state.
5.  Implement API Endpoint.
6.  Update Frontend Service.
