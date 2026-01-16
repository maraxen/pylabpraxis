# Task: State Inspection Browser Mode

**ID**: FE-02
**Status**: 📐 Planning Complete
**Priority**: P2
**Difficulty**: Medium
**Depends On**: FE-01 (State Inspection Backend) ✅

---

## 📋 Phase 1: Inspection (I)

**Objective**: Understand browser mode execution architecture and identify integration points for state capture.

- [x] Review browser execution layer in `praxis/web-client/src/app/core/services/`
- [x] Trace Pyodide execution flow - how protocols run in browser
- [x] Understand `SqliteService` schema and capabilities
- [x] Check if state capture hooks exist in browser execution
- [x] Review `simulation-results.service.ts:169-177` - `getStateHistoryFromBrowserMode()`

**Key Questions - ANSWERED**:

1. **Does browser execution have access to workcell state?** ✅ YES
   - Browser builds PLR `Plate`, `TipRack`, `LiquidHandler` objects during parameter resolution
   - Full workcell available during protocol execution in Pyodide
   - Can call `.serialize_all_state()` on LiquidHandler deck

2. **How does Pyodide serialize PLR resource state?** ✅ IDENTICALLY TO BACKEND
   - Pyodide runs actual PyLabRobot code
   - Returns same format: `{resource_name: plr_resource_state}`

3. **What's the browser SQLite schema for function call logs?** ✅ COMPLETE & READY
   - Schema auto-generated from backend models
   - `function_call_logs` table has `state_before_json` and `state_after_json` columns
   - Repository pattern already implemented

4. **Can we reuse backend transformation logic or need TypeScript port?** ⚠️ PORT TO TYPESCRIPT
   - Recommended: TypeScript implementation (`Option A`)
   - Cleaner separation, better type safety, less overhead

**Findings Summary**:
- ✅ Schema, repositories, and DB layer ready
- ✅ Browser has full PLR state access
- ⚠️ State capture NOT integrated into execution
- ⚠️ `getRunStateHistory()` returns mock data
- ❌ No function call logging during execution

**Detailed Findings**: See [INVESTIGATION_SUMMARY.md](./INVESTIGATION_SUMMARY.md)

---

## 📐 Phase 2: Planning (P)

**Objective**: Design browser mode state capture and retrieval architecture.

- [x] Map browser execution to state capture points
- [x] Design SqliteService.getRunStateHistory() interface
- [x] Plan state persistence in browser SQLite
- [x] Decide: TypeScript transformation vs. store pre-transformed state
- [x] Plan integration with existing `getStateHistoryFromBrowserMode()`

**Decision**: Hybrid Approach (Capture in Python, Transform in TypeScript)

After detailed analysis, the optimal architecture is:
1. **State Capture**: Python-side hooks in `web_bridge.py` (PLR objects exist only in Pyodide)
2. **State Persistence**: Store raw PLR state in `function_call_logs` table
3. **State Transformation**: TypeScript port of backend transform logic
4. **State Retrieval**: Real `getRunStateHistory()` implementation querying logs

**Detailed Plan**: See [PLANNING_SUMMARY.md](./PLANNING_SUMMARY.md)

**Implementation Phases**:
1. Python state capture hooks (`web_bridge.py`)
2. Worker message handling (`python.worker.ts`)
3. Execution service persistence (`execution.service.ts`)
4. TypeScript transformation module (new `state-transform.ts`)
5. SQLite service retrieval (`sqlite.service.ts`)
6. Testing

**Effort Estimate**: 12-16 hours (3-4 days at part-time pace)

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement browser mode state capture and retrieval.

**Phase 3.1: Python State Capture (web_bridge.py)**
- [ ] Add `patch_function_call_logging(lh, run_id)` function
- [ ] Add `_emit_function_call_log()` helper
- [ ] Add `_serialize_args()` helper
- [ ] Import `time` module for timestamps

**Phase 3.2: Worker Message Handling (python.worker.ts)**
- [ ] Add `FUNCTION_CALL_LOG` to `PythonMessage` interface
- [ ] Add case handler to forward FUNCTION_CALL_LOG messages

**Phase 3.3: Execution Service Persistence (execution.service.ts)**
- [ ] Handle `function_call_log` output type in `executeBrowserProtocol()`
- [ ] Implement `handleFunctionCallLog()` method
- [ ] Pass `runId` to `buildProtocolExecutionCode()`
- [ ] Update generated Python code to call `patch_function_call_logging()`

**Phase 3.4: SQLite Service (sqlite.service.ts)**
- [ ] Add `createFunctionCallLog()` method
- [ ] Rewrite `getRunStateHistory()` to query `function_call_logs`
- [ ] Import `transformPlrState` from new utils module

**Phase 3.5: TypeScript Transformation (NEW: state-transform.ts)**
- [ ] Create `praxis/web-client/src/app/core/utils/state-transform.ts`
- [ ] Implement `extractTipState()`
- [ ] Implement `extractLiquidVolumes()`
- [ ] Implement `inferParentName()` and `inferWellId()`
- [ ] Implement `getOnDeckResources()`
- [ ] Implement `transformPlrState()`

**Work Log**:

- [Pending - Awaiting approval]

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify browser mode state inspection works end-to-end.

- [ ] Unit tests for TypeScript transformation functions
- [ ] Integration test: run protocol in browser mode, verify state captured
- [ ] E2E test: State Inspector shows real data in browser mode
- [ ] Compare browser mode and backend mode state output for consistency

**Results**:
> [To be captured]

---

## 📚 Tracking & Context

- **Parent Task**: FE-01 (State Inspection Backend) - COMPLETE
- **Related Technical Debt**: TD-802 (resolved for backend, open for browser)
- **Files**:
  - `praxis/web-client/src/app/core/services/sqlite.service.ts`
  - `praxis/web-client/src/app/core/services/simulation-results.service.ts`
  - `praxis/web-client/src/app/core/services/pyodide.service.ts`
  - `scripts/generate_browser_schema.py`

---

## 🔗 Reference: Backend Implementation

The backend implementation (FE-01) provides a reference for what needs to be achieved:

**Backend Transformation** (`praxis/backend/core/state_transform.py`):
```python
def transform_plr_state(plr_state: dict) -> dict:
    return {
        "tips": extract_tip_state(plr_state),      # {tips_loaded, tips_count}
        "liquids": extract_liquid_volumes(plr_state),  # {plate: {well: volume}}
        "on_deck": list(plr_state.keys()),
        "raw_plr_state": plr_state
    }
```

**PLR State Format** (from `serialize_all_state()`):
```json
{
  "liquid_handler": {"head_state": {"0": {"tip": {...}}, ...}},
  "source_plate_A1": {"volume": 250.0, "pending_volume": 250.0, ...}
}
```

**Frontend Expected Format** (`StateSnapshot`):
```typescript
{
  tips: { tips_loaded: boolean, tips_count: number },
  liquids: { [resource: string]: { [well: string]: number } },
  on_deck: string[],
  raw_plr_state?: any
}
```
