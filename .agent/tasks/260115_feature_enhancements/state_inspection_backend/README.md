# Task: State Inspection Backend

**ID**: FE-01
**Status**: ⚪ Not Started
**Priority**: P1
**Difficulty**: Hard

---

## 📋 Phase 1: Inspection (I)

**Objective**: Inspect current `FunctionCallLog` model and `ExecutionMixin` to understand gaps preventing post-run "time travel" state inspection.

- [ ] Review `praxis/backend/models/domain/protocol.py` → `FunctionCallLog` class
- [ ] Trace execution flow in `praxis/backend/core/orchestrator/execution.py`
- [ ] Read `praxis/backend/core/workcell_runtime/workcell_runtime.py` → `get_state_snapshot()`
- [ ] Check frontend expectations in `praxis/web-client/src/app/features/workcell/components/deck-view/`

**Findings**:
> - Current schema gaps (state_before_json, state_after_json missing)
> - Serialization format differences (PLR output vs frontend expectations)
> - API gaps for state history retrieval

---

## 📐 Phase 2: Planning (P)

**Objective**: Plan schema updates, execution flow modifications, and API endpoint.

- [ ] Design Alembic migration for new JSON columns
- [ ] Plan ExecutionMixin capture points
- [ ] Design `GET /api/v1/protocols/runs/{run_id}/state-history` response model
- [ ] Plan frontend service integration

**Implementation Plan**:

1. Add `state_before_json` and `state_after_json` to `FunctionCallLog` model
2. Generate Alembic migration with nullable defaults
3. Modify `ExecutionMixin` to capture `get_state_snapshot()` before/after calls
4. Implement API endpoint returning `StateHistory` / `OperationStateSnapshot`
5. Update `SimulationResultsService.getStateHistory()` for backend mode

**Definition of Done**:

1. Migration applied successfully
2. Running a protocol populates state snapshots in DB
3. API endpoint returns state history
4. Frontend State Inspector shows timeline for backend runs

**Risk Mitigations**:
- Performance: Large JSON snapshots may cause DB bloat (future: delta compression)
- Serialization: May need transformation layer for PLR → frontend format

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement state capture and history endpoint.

- [ ] Modify `praxis/backend/models/domain/protocol.py`:
  ```python
  state_before_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
  state_after_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
  ```
- [ ] Generate migration: `alembic revision --autogenerate -m "add state snapshots"`
- [ ] Apply migration: `alembic upgrade head`
- [ ] Modify `ExecutionMixin` to capture state before/after function calls
- [ ] Implement API endpoint in `praxis/backend/api/endpoints/protocol_runs.py`
- [ ] Update `simulation-results.service.ts` to call backend API

**Work Log**:

- [Pending]

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify state inspection works end-to-end.

- [ ] Verify migration: `uv run alembic current`
- [ ] Run test protocol, check DB: `SELECT state_before_json FROM function_call_logs`
- [ ] Test API: `curl http://localhost:8000/api/v1/protocols/runs/{run_id}/state-history`
- [ ] Manual UI verification: State Inspector tab shows timeline

**Results**:
> [To be captured]

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Technical Debt**: TD-801, TD-802, TD-803
- **Files**:
  - `praxis/backend/models/domain/protocol.py`
  - `praxis/backend/core/orchestrator/execution.py`
  - `praxis/backend/core/workcell_runtime/workcell_runtime.py`
  - `praxis/backend/api/endpoints/protocol_runs.py`
  - `praxis/web-client/src/app/core/services/simulation-results.service.ts`
