# State Inspection Browser Mode - Investigation Summary

**Date**: 2026-01-16
**Status**: Investigation Complete ✅
**Key Finding**: Browser mode CAN support state inspection, but requires implementation of state capture layer

---

## Executive Summary

Browser mode state inspection is **feasible** and **partially prepared**. The infrastructure exists:
- ✅ SQLite schema has `function_call_logs` table with `state_before_json` and `state_after_json` columns
- ✅ `SqliteService` has `getRunStateHistory()` method (returns mock data currently)
- ✅ `FunctionCallLogRepository` exists for persistence
- ✅ Backend transformation logic can be ported to TypeScript
- ⚠️ State capture NOT integrated into browser execution layer
- ⚠️ No mechanism to log function calls during protocol execution

**Effort Estimate**: Medium (3-5 days)
**Complexity**: Medium (requires adding execution hooks to Pyodide wrapper)

---

## Component Status

| Component | Status | Location | Gap |
|-----------|--------|----------|-----|
| **Schema** | ✅ Ready | `praxis/web-client/src/assets/db/schema.sql` | Has `function_call_logs` with state columns |
| **Repository** | ✅ Ready | `praxis/web-client/src/app/core/db/repositories.ts` | `FunctionCallLogRepository` exists |
| **SqliteService** | ⚠️ Stub | `sqlite.service.ts:1136` | Returns mock data, needs real query |
| **Execution Service** | ❌ Missing | `execution.service.ts` | No state capture during protocol run |
| **Transformation** | ⚠️ Python | `praxis/backend/core/state_transform.py` | Needs TypeScript port |
| **Pyodide Bridge** | ⚠️ Basic | `web_bridge.py` | Has `emit_well_state()` but not full state capture |

---

## Browser Execution Flow

```
execution.service.ts:startBrowserRun()
    ↓
executeBrowserProtocol()
    ↓
buildProtocolExecutionCode() → generates Python code
    ↓
pythonRuntime.execute(code) → runs in Pyodide worker
    ↓
Protocol function executes
    ↓ (Current: only well_state_update messages)
    ↓ (Missing: function call logging with before/after state)
    ↓
wellState signal updated in component
```

### Current State Emission (Partial)

**In `web_bridge.py:emit_well_state()`**:
- Emits `WELL_STATE_UPDATE` messages with plate/tip state
- Only triggers on `patch_state_emission(lh)` calls
- No automatic function call logging

**What's Missing**:
1. No `@protocol_function` decorator equivalent for browser
2. No automatic before/after state capture
3. No function call log entries created
4. State updates not persisted to `function_call_logs` table

---

## Key Questions Answered

### Q1: Does browser execution have access to workcell state?

**Answer: YES** ✅

- Browser builds PLR `Plate`, `TipRack`, `LiquidHandler` objects during parameter resolution
- `web_bridge.py:resolve_parameters()` instantiates PLR resources with dimensions
- Full workcell available during protocol execution in Pyodide
- Can call `.serialize_all_state()` on LiquidHandler deck

**Code Evidence**:
```python
# web_bridge.py:24-108
resolved[name] = res.Plate(name=r_name, size_x=sx, size_y=sy, lid=False)
resolved[name] = res.TipRack(name=r_name, size_x=sx, size_y=sy)
resolved[name] = res.Container(...)
```

### Q2: How does Pyodide serialize PLR resource state?

**Answer: Same as backend** ✅

- Pyodide runs actual PyLabRobot code
- PLR's `serialize_all_state()` works identically in browser
- Returns same format: `{resource_name: plr_resource_state}`

**Example Output**:
```json
{
  "liquid_handler": {"head_state": {"0": {"tip": {...}}, ...}},
  "source_plate": {"volume": 250.0, "pending_volume": 250.0, ...}
}
```

### Q3: What's the browser SQLite schema for function call logs?

**Answer: Complete and ready** ✅

```sql
CREATE TABLE function_call_logs (
    accession_id CHAR(32) PRIMARY KEY,
    sequence_in_run INTEGER,
    status VARCHAR(11),
    input_args_json TEXT,
    return_value_json TEXT,
    state_before_json TEXT,      ← Already here
    state_after_json TEXT,        ← Already here
    protocol_run_accession_id CHAR(32),
    function_protocol_definition_accession_id CHAR(32),
    parent_function_call_log_accession_id CHAR(32),
    ...
);
```

**Schema Generation**: Automatically generated from backend models via `scripts/generate_browser_schema.py`

### Q4: Can we reuse backend transformation logic or need TypeScript port?

**Answer: Port to TypeScript**

**Reasoning**:
- Backend transformation runs in Python (`state_transform.py`)
- Browser runs TypeScript + Pyodide Python separately
- Two options:

**Option A: Port to TypeScript** (Recommended)
```typescript
// In browser services
function extractTipState(plrState: any): {tips_loaded: boolean, tips_count: number}
function extractLiquidVolumes(plrState: any): Record<string, Record<string, number>>
function transformPlrState(plrState: any): StateSnapshot
```
- Transformation happens in Angular
- Cleaner separation
- TypeScript type safety

**Option B: Run transformation in Pyodide**
```python
# In web_bridge.py
from praxis.backend.core.state_transform import transform_plr_state
```
- Reuse existing Python code
- More overhead (Python ↔ JS boundary crossing)
- Tighter coupling with backend

**Recommendation: Option A (TypeScript)**

---

## Architecture Design: Browser State Inspection

### High-Level Flow

```
Protocol Execution
├─ Function Call Start
│  ├─ Capture state_before = lh.serialize_all_state()
│  └─ Log function_call_start() to SQLite
├─ Function executes
└─ Function Call End
   ├─ Capture state_after = lh.serialize_all_state()
   ├─ Log function_call_end() with state
   └─ Store to function_call_logs table

State Retrieval
├─ getRunStateHistory(runId)
├─ Query function_call_logs for run
├─ Transform each state via transformPlrState()
└─ Return StateHistory with operations[]
```

### Implementation Strategy

**Option A: Wrapper/Decorator Pattern** (Recommended)

Create a function wrapper that auto-logs calls:

```typescript
// In execution.service.ts
function createLoggingWrapper(protocolFunction, runId, sqliteService) {
    return async (...args) => {
        // 1. Log start
        const callId = uuid();
        const stateBefore = ...get state from args...
        await sqliteService.functionCallLogs.insert({
            accession_id: callId,
            state_before_json: stateBefore,
            ...
        });

        // 2. Execute
        const result = await protocolFunction(...args);

        // 3. Log end
        const stateAfter = ...get state from args...
        await sqliteService.functionCallLogs.update(callId, {
            state_after_json: stateAfter,
            ...
        });

        return result;
    };
}
```

**Option B: Modify web_bridge.py**

Add function call hooks:

```python
# In web_bridge.py
def log_function_call_start(func_name, state_before):
    # Send to browser via postMessage
    postMessage({
        'type': 'FUNCTION_CALL_START',
        'function': func_name,
        'state_before': state_before
    })

def log_function_call_end(func_name, state_after):
    postMessage({
        'type': 'FUNCTION_CALL_END',
        'function': func_name,
        'state_after': state_after
    })
```

**Recommendation: Option A**
- Keeps logic in Angular
- Simpler to debug
- No Pyodide overhead
- Clear separation of concerns

---

## Implementation Gaps

### Gap 1: No Automatic State Capture

**Current**:
- Only `well_state_update` messages during execution
- No function-level state snapshots
- No persistent logging to SQLite

**Required**:
- Before each function call: capture state_before
- After each function call: capture state_after
- Log to `function_call_logs` table

### Gap 2: SqliteService.getRunStateHistory() Returns Mock Data

**Current** (line 1136-1157):
```typescript
public getRunStateHistory(runId: string): Observable<any | null> {
    // Returns this.createMockStateHistory(runId, protocolName)
    // if state_history_json is null
}
```

**Required**:
```typescript
public getRunStateHistory(runId: string): Observable<StateHistory | null> {
    // 1. Query function_call_logs for runId
    // 2. Transform each record via transformPlrState()
    // 3. Build StateHistory with operations[]
    // 4. Return structured data
}
```

### Gap 3: No TypeScript State Transformation

**Current**: Python-only (`praxis/backend/core/state_transform.py`)

**Required**: TypeScript equivalent
```typescript
// new file: praxis/web-client/src/app/core/utils/state-transform.ts
export function extractTipState(plrState: any): TipStateSnapshot { ... }
export function extractLiquidVolumes(plrState: any): LiquidVolumes { ... }
export function transformPlrState(plrState: any): StateSnapshot { ... }
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `praxis/web-client/src/app/core/utils/state-transform.ts` | CREATE | TypeScript transformation functions |
| `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts` | MODIFY | Add state capture during execution |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | MODIFY | Implement `getRunStateHistory()` properly |
| `praxis/web-client/src/app/core/workers/python.worker.ts` | MODIFY | Handle FUNCTION_CALL messages |
| `praxis/web-client/src/assets/python/web_bridge.py` | MODIFY | Add function logging hooks |

---

## Current vs. Proposed

### Current (Mock Data)

```
Protocol Execute
    ↓ (no logging)
Well State Updates
    ↓ (UI updates only)
State Inspector → Shows Mock Data
```

### Proposed (Real Data)

```
Protocol Execute
    ↓
Function Start → Log to SQLite
    ↓
Function Call with State Before
    ↓
Function Executes
    ↓
Function Call with State After → Log to SQLite
    ↓
getRunStateHistory() → Real Data from Logs
    ↓
Transform via TypeScript functions
    ↓
State Inspector → Shows Real Timeline
```

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **Performance**: Frequent state serialization | Medium | Only capture on function boundaries, not every instruction |
| **Storage**: Large JSON snapshots in SQLite | Medium | Browser SQLite has size limits; may need delta compression later |
| **Sync Issues**: State drift between Python/TS | Low | Transform same format both sides; add validation |
| **Debugging**: Errors in Pyodide capture logic | Medium | Add comprehensive error handling; test with simple protocols first |

---

## Dependencies

- ✅ No new external libraries needed
- ✅ Existing PLR code handles serialization
- ✅ TypeScript interfaces already defined (`StateSnapshot`, `StateHistory`)
- ✅ Repository pattern already in place

---

## Conclusion

**Browser mode state inspection is achievable** with medium-level effort:

1. **Schema & DB**: ✅ Already ready
2. **Repositories**: ✅ Already implemented
3. **Execution**: ⚠️ Needs function logging hooks
4. **Transformation**: ❌ Needs TypeScript port
5. **Retrieval**: ⚠️ Needs real implementation instead of mock

**Next Phase**: Planning (P) - Design the exact implementation approach and function logging strategy.

**Estimated Effort**:
- Port transformation logic: 2-3 hours
- Add execution hooks: 4-6 hours
- Implement getRunStateHistory(): 2-3 hours
- Testing & debugging: 3-4 hours
- **Total: 3-5 days**

**Priority**: P2 (nice-to-have; backend mode (FE-01) is more critical)
