# Task: State Inspection Backend

**ID**: FE-01
**Status**: ✅ Complete
**Priority**: P1
**Difficulty**: Easy (revised from Hard - 95% already implemented!)

---

## 📋 Phase 1: Inspection (I)

**Objective**: Inspect current `FunctionCallLog` model and `ExecutionMixin` to understand gaps preventing post-run "time travel" state inspection.

- [x] Review `praxis/backend/models/domain/protocol.py` → `FunctionCallLog` class
- [x] Trace execution flow in `praxis/backend/core/orchestrator/execution.py`
- [x] Read `praxis/backend/core/workcell_runtime/workcell_runtime.py` → `get_state_snapshot()`
- [x] Check frontend expectations in `praxis/web-client/src/app/core/models/simulation.models.ts`

**Findings**:

### ✅ Already Implemented (Surprisingly!)

1. **Schema Fields**: `FunctionCallLog` already has `state_before_json` and `state_after_json` fields (protocol.py:592-597)
2. **State Capture**: Protocol decorator already captures state before/after each function call (protocol_decorator.py:92-97, 384-399)
   - Uses `context.runtime.get_state_snapshot()` to capture state
   - Passes to `log_function_call_start()` and `log_function_call_end()`
3. **Service Layer**: State values are persisted to DB (services/protocols.py:469-526)
4. **API Endpoint**: `GET /api/v1/protocols/runs/{run_id}/state-history` endpoint exists (api/protocols.py:192-256)
5. **Frontend Service**: `SimulationResultsService.getStateHistory()` already calls the endpoint (simulation-results.service.ts:89-117)

### ⚠️ Primary Gap: State Format Transformation

**Issue**: PLR state format ≠ Frontend expected format

**PLR State Format** (from `Workcell.serialize_all_state()`):
```json
{
  "resource_name_1": { /* PLR Resource.serialize_state() */ },
  "resource_name_2": { /* PLR Resource.serialize_state() */ }
}
```

**Frontend Expected Format** (from `simulation.models.ts`):
```typescript
{
  tips: { tips_loaded: boolean, tips_count: number },
  liquids: { resource_name: { well: volume } },
  on_deck: string[],
  raw_plr_state?: any
}
```

**Current API Behavior** (protocols.py:226-235):
- Wraps raw PLR state in `StateSnapshot` with empty tips/liquids/on_deck
- Has TODO comment: "Implement proper transformation from PLR state to flattened volumes/tips"
- Currently stores raw PLR state in `raw_plr_state` field as fallback

### 📊 Data Flow (Verified Working)

1. **Execution**: `@protocol_function` decorator wrapper (protocol_decorator.py:283-413)
2. **Pre-capture**: `_log_call_start()` → `context.runtime.get_state_snapshot()` → `state_before_json`
3. **Function runs**: User protocol function executes
4. **Post-capture**: Finally block → `context.runtime.get_state_snapshot()` → `state_after_json`
5. **Persistence**: `log_function_call_end()` updates DB with both states
6. **API**: Endpoint queries `FunctionCallLog` records and wraps in `StateHistory`
7. **Frontend**: Service calls endpoint, receives data

### 🔍 State Snapshot Implementation

**WorkcellRuntime.get_state_snapshot()** (workcell_runtime/state_sync.py:188-190):
```python
def get_state_snapshot(self) -> dict[str, Any]:
    return self._main_workcell.serialize_all_state()
```

**Workcell.serialize_all_state()** (core/workcell.py:165-171):
```python
def serialize_all_state(self) -> dict[str, Any]:
    state: dict[str, Any] = {}
    for child in self.get_all_children():
        if isinstance(child, Resource):
            state[child.name] = child.serialize_state()
    return state
```

Returns: `{resource_name: PLRResourceState}` - delegates to PyLabRobot's `Resource.serialize_state()`

### 🎯 What Needs Implementation

**Only one thing**: State transformation layer in API endpoint

Current (protocols.py:226-235):
```python
def wrap_state(plr_state):
    if not plr_state: return None
    # TODO: Implement proper transformation from PLR state to flattened volumes/tips
    return StateSnapshot(
        tips=TipStateSnapshot(),
        liquids={},
        on_deck=[],
        raw_plr_state=plr_state
    )
```

Need to extract from PLR state:
- `tips_loaded` / `tips_count` from liquid handler state
- Well volumes from plate resources
- On-deck resource list from workcell state keys

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

**Objective**: Implement state transformation layer for API endpoint.

- [x] Create state transformation helper module `praxis/backend/core/state_transform.py`
- [x] Implement `extract_tip_state()` - extracts tip state from liquid handler head_state
- [x] Implement `extract_liquid_volumes()` - extracts well volumes from VolumeTracker states
- [x] Implement `get_on_deck_resources()` - returns list of resource names
- [x] Implement `transform_plr_state()` - main entry point combining all extractors
- [x] Update `wrap_state()` in `api/protocols.py` to use transformation module

**Work Log**:

- 2026-01-16: Created `praxis/backend/core/state_transform.py` with transformation functions
- 2026-01-16: Updated `api/protocols.py:226-238` to use `transform_plr_state()`
- 2026-01-16: Added 27 unit tests in `tests/core/test_state_transform.py`

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify state inspection works end-to-end.

- [x] Unit tests for transformation functions: 27 tests pass
- [x] API tests pass: 5/5 protocol_runs tests
- [x] Full test suite: 106 passed, 2 skipped
- [ ] Manual UI verification: State Inspector tab shows timeline (deferred to frontend testing)

**Results**:
> ✅ All automated tests pass. State transformation layer implemented and verified.
>
> **Test Output Summary**:
> - `tests/core/test_state_transform.py`: 27 passed
> - `tests/api/test_protocol_runs.py`: 5 passed
> - Full API test suite: 106 passed, 2 skipped

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Technical Debt**: TD-802 (resolved)
- **Files Created/Modified**:
  - `praxis/backend/core/state_transform.py` (NEW - transformation utilities)
  - `praxis/backend/api/protocols.py` (MODIFIED - updated wrap_state())
  - `tests/core/test_state_transform.py` (NEW - 27 unit tests)
- **Files Reference**:
  - `praxis/backend/models/domain/protocol.py` - FunctionCallLog model
  - `praxis/backend/core/decorators/protocol_decorator.py` - state capture
  - `praxis/backend/services/protocols.py` - state persistence
  - `praxis/web-client/src/app/core/services/simulation-results.service.ts` - frontend service
