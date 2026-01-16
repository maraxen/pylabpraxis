# State Inspection Browser Mode - Planning Summary

**Date**: 2026-01-16
**Status**: Planning Complete
**Task ID**: FE-02
**Dependency**: FE-01 (State Inspection Backend) - COMPLETE

---

## Executive Summary

This document details the implementation plan for browser mode state inspection, enabling "time travel" debugging for protocols executed via Pyodide. The architecture uses a **hybrid approach**:

1. **State Capture**: Python-side hooks in `web_bridge.py` (because PLR objects exist only in Pyodide)
2. **State Transformation**: TypeScript utilities in Angular (for type safety and debuggability)
3. **State Persistence**: Browser SQLite via existing `FunctionCallLogRepository`
4. **State Retrieval**: Enhanced `SqliteService.getRunStateHistory()` with real data

**Estimated Effort**: 12-16 hours (3-4 days at part-time pace)

---

## Architecture Decision

### Why Hybrid Approach?

The investigation identified two options:
- **Option A**: Wrapper pattern in TypeScript
- **Option B**: Modify web_bridge.py in Python

After detailed code analysis, **neither option alone is sufficient**:

| Concern | Option A (TypeScript) | Option B (Python) | Hybrid |
|---------|----------------------|-------------------|--------|
| PLR state access | Cannot access - objects in Pyodide only | Full access via `serialize_all_state()` | Full access |
| Type safety | Excellent | None | Excellent for transformation |
| Debugging | Browser DevTools | Pyodide console only | Both available |
| Message overhead | N/A | One message per function call | Minimal |
| Code complexity | Complex wrapper logic | Simple patching | Balanced |

**Decision**: Use Python for capture (where state exists) and TypeScript for transformation (where types exist).

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PYODIDE (Python)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  Protocol Function Executes                                                 │
│       ↓                                                                     │
│  patch_function_call_logging(lh)  ← NEW: Wraps LH methods                   │
│       ↓                                                                     │
│  Before method: state_before = lh.deck.serialize_all_state()               │
│       ↓                                                                     │
│  Method executes (aspirate, dispense, etc.)                                │
│       ↓                                                                     │
│  After method: state_after = lh.deck.serialize_all_state()                 │
│       ↓                                                                     │
│  postMessage({type: 'FUNCTION_CALL_LOG', payload: {...}})                  │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WEB WORKER (python.worker.ts)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  Handle FUNCTION_CALL_LOG message type                                      │
│       ↓                                                                     │
│  Forward to main thread with execution ID                                   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ANGULAR MAIN THREAD                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  PythonRuntimeService receives message                                      │
│       ↓                                                                     │
│  ExecutionService.handleFunctionCallLog(runId, payload)                     │
│       ↓                                                                     │
│  SqliteService.createFunctionCallLog({                                      │
│      state_before_json: payload.state_before,  ← Raw PLR state             │
│      state_after_json: payload.state_after,                                 │
│      ...                                                                    │
│  })                                                                         │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STATE RETRIEVAL                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  SimulationResultsService.getStateHistory(runId)                            │
│       ↓                                                                     │
│  SqliteService.getRunStateHistory(runId)                                    │
│       ↓                                                                     │
│  Query function_call_logs WHERE protocol_run_accession_id = runId           │
│       ↓                                                                     │
│  For each log: transformPlrState(state_before_json)  ← TypeScript transform│
│       ↓                                                                     │
│  Return StateHistory with OperationStateSnapshot[]                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Python State Capture Hooks (web_bridge.py)

**File**: `praxis/web-client/src/assets/python/web_bridge.py`
**Effort**: 2-3 hours

#### 1.1 Add Function Call Logging Hook

Create a new function that wraps LiquidHandler methods to emit function call logs:

```python
# Global sequence counter for ordering
_function_call_sequence = 0

def patch_function_call_logging(lh: Any, run_id: str):
    """
    Patches a LiquidHandler to emit function call logs with state before/after.

    Unlike patch_state_emission() which only emits well state updates,
    this captures full serialized state for time-travel debugging.
    """
    global _function_call_sequence
    _function_call_sequence = 0  # Reset for new run

    if not IS_BROWSER_MODE:
        return lh

    methods_to_log = [
        "aspirate", "dispense", "pick_up_tips", "drop_tips",
        "aspirate96", "dispense96", "pick_up_tips96", "drop_tips96",
        "move_plate", "move_lid",  # Add more as needed
    ]

    original_methods = {}

    for method_name in methods_to_log:
        if hasattr(lh, method_name):
            original_methods[method_name] = getattr(lh, method_name)

            def create_logged_method(m_name, original):
                async def logged_method(*args, **kwargs):
                    global _function_call_sequence

                    # Capture state before
                    state_before = None
                    try:
                        state_before = lh.deck.serialize_all_state()
                    except Exception as e:
                        print(f"[web_bridge] State capture failed: {e}")

                    call_id = str(uuid.uuid4())
                    start_time = time.time()
                    error_message = None

                    # Log start
                    _emit_function_call_log(
                        call_id=call_id,
                        run_id=run_id,
                        sequence=_function_call_sequence,
                        method_name=m_name,
                        args=_serialize_args(args, kwargs),
                        state_before=state_before,
                        state_after=None,
                        status="running",
                        start_time=start_time,
                    )

                    try:
                        # Execute actual method
                        result = await original(*args, **kwargs)
                        status = "completed"
                    except Exception as e:
                        error_message = str(e)
                        status = "failed"
                        raise
                    finally:
                        # Capture state after
                        state_after = None
                        try:
                            state_after = lh.deck.serialize_all_state()
                        except Exception:
                            pass

                        end_time = time.time()
                        duration_ms = (end_time - start_time) * 1000

                        # Log completion
                        _emit_function_call_log(
                            call_id=call_id,
                            run_id=run_id,
                            sequence=_function_call_sequence,
                            method_name=m_name,
                            args=_serialize_args(args, kwargs),
                            state_before=state_before,
                            state_after=state_after,
                            status=status,
                            start_time=start_time,
                            end_time=end_time,
                            duration_ms=duration_ms,
                            error_message=error_message,
                        )

                        _function_call_sequence += 1

                    return result

                return logged_method

            setattr(lh, method_name, create_logged_method(method_name, original_methods[method_name]))

    return lh


def _emit_function_call_log(
    call_id: str,
    run_id: str,
    sequence: int,
    method_name: str,
    args: dict,
    state_before: dict | None,
    state_after: dict | None,
    status: str,
    start_time: float,
    end_time: float | None = None,
    duration_ms: float | None = None,
    error_message: str | None = None,
):
    """Emit a function call log message to the browser."""
    payload = {
        "call_id": call_id,
        "run_id": run_id,
        "sequence": sequence,
        "method_name": method_name,
        "args": args,
        "state_before": state_before,
        "state_after": state_after,
        "status": status,
        "start_time": start_time,
        "end_time": end_time,
        "duration_ms": duration_ms,
        "error_message": error_message,
    }
    postMessage(json.dumps({"type": "FUNCTION_CALL_LOG", "payload": payload}))


def _serialize_args(args: tuple, kwargs: dict) -> dict:
    """Serialize function arguments for logging."""
    result = {}

    # Positional args
    for i, arg in enumerate(args):
        try:
            if hasattr(arg, 'name'):
                result[f"arg_{i}"] = f"<{type(arg).__name__}: {arg.name}>"
            elif hasattr(arg, '__dict__'):
                result[f"arg_{i}"] = f"<{type(arg).__name__}>"
            else:
                result[f"arg_{i}"] = repr(arg)[:100]
        except Exception:
            result[f"arg_{i}"] = "<unserializable>"

    # Keyword args
    for key, value in kwargs.items():
        try:
            if hasattr(value, 'name'):
                result[key] = f"<{type(value).__name__}: {value.name}>"
            elif hasattr(value, '__dict__'):
                result[key] = f"<{type(value).__name__}>"
            else:
                result[key] = repr(value)[:100]
        except Exception:
            result[key] = "<unserializable>"

    return result
```

#### 1.2 Update Protocol Execution Code Generation

Modify `execution.service.ts:buildProtocolExecutionCode()` to call the new patching function:

```python
# In generated protocol code (within buildProtocolExecutionCode)
# After resolve_parameters, before execution:

# Patch for function call logging (time-travel debugging)
from web_bridge import patch_function_call_logging
for p_value in resolved_params.values():
    try:
        from pylabrobot.liquid_handling import LiquidHandler
        if isinstance(p_value, LiquidHandler):
            patch_function_call_logging(p_value, '${runId}')
    except ImportError:
        pass
```

---

### Phase 2: Worker Message Handling (python.worker.ts)

**File**: `praxis/web-client/src/app/core/workers/python.worker.ts`
**Effort**: 30 minutes

#### 2.1 Add FUNCTION_CALL_LOG to Message Types

```typescript
interface PythonMessage {
  type: 'INIT' | 'PUSH' | 'EXEC' | 'INSTALL' | 'COMPLETE' | 'SIGNATURES'
      | 'PLR_COMMAND' | 'RAW_IO' | 'RAW_IO_RESPONSE' | 'WELL_STATE_UPDATE'
      | 'FUNCTION_CALL_LOG';  // NEW
  id?: string;
  payload?: any;
}
```

#### 2.2 Handle FUNCTION_CALL_LOG Messages

Add case in the message handler (around line 71):

```typescript
case 'FUNCTION_CALL_LOG':
    postMessage({ type: 'FUNCTION_CALL_LOG', id: currentExecutionId, payload });
    break;
```

---

### Phase 3: Execution Service Persistence (execution.service.ts)

**File**: `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts`
**Effort**: 1-2 hours

#### 3.1 Handle function_call_log Output Type

In `executeBrowserProtocol()`, add handling for the new message type (around line 203):

```typescript
} else if (output.type === 'function_call_log') {
    try {
        const logData = JSON.parse(output.content);
        this.handleFunctionCallLog(runId, logData);
    } catch (err) {
        console.error('[ExecutionService] Error parsing function call log:', err);
    }
}
```

#### 3.2 Implement handleFunctionCallLog Method

```typescript
/**
 * Persist a function call log entry to browser SQLite.
 */
private handleFunctionCallLog(runId: string, logData: {
    call_id: string;
    run_id: string;
    sequence: number;
    method_name: string;
    args: Record<string, unknown>;
    state_before: Record<string, unknown> | null;
    state_after: Record<string, unknown> | null;
    status: string;
    start_time: number;
    end_time?: number;
    duration_ms?: number;
    error_message?: string;
}): void {
    // Only persist completed entries (with state_after)
    if (logData.status !== 'running') {
        const record = {
            accession_id: logData.call_id,
            protocol_run_accession_id: runId,
            function_protocol_definition_accession_id: 'browser_execution',
            sequence_in_run: logData.sequence,
            name: logData.method_name,
            status: logData.status === 'completed' ? 'COMPLETED' : 'FAILED',
            start_time: new Date(logData.start_time * 1000).toISOString(),
            end_time: logData.end_time ? new Date(logData.end_time * 1000).toISOString() : null,
            duration_ms: logData.duration_ms ?? null,
            input_args_json: JSON.stringify(logData.args),
            state_before_json: logData.state_before ? JSON.stringify(logData.state_before) : null,
            state_after_json: logData.state_after ? JSON.stringify(logData.state_after) : null,
            error_message_text: logData.error_message ?? null,
        };

        this.sqliteService.createFunctionCallLog(record).subscribe({
            error: (err) => console.warn('[ExecutionService] Failed to persist function call log:', err)
        });
    }
}
```

#### 3.3 Add SqliteService.createFunctionCallLog Method

In `sqlite.service.ts`, add:

```typescript
/**
 * Create a function call log entry.
 */
public createFunctionCallLog(record: Partial<FunctionCallLog>): Observable<void> {
    return this.db$.pipe(
        map(db => {
            const columns = Object.keys(record);
            const values = Object.values(record);
            const placeholders = columns.map(() => '?').join(', ');

            const sql = `INSERT INTO function_call_logs (${columns.join(', ')}) VALUES (${placeholders})`;
            db.run(sql, values);
        })
    );
}
```

---

### Phase 4: TypeScript State Transformation (NEW FILE)

**File**: `praxis/web-client/src/app/core/utils/state-transform.ts`
**Effort**: 2-3 hours

Port the Python transformation logic to TypeScript with proper types:

```typescript
/**
 * State transformation utilities for converting PyLabRobot state to frontend format.
 *
 * This is a TypeScript port of praxis/backend/core/state_transform.py
 * for use in browser mode where state comes directly from Pyodide.
 */

import type { StateSnapshot, TipStateSnapshot, WellVolumeMap } from '../models/simulation.models';

/**
 * Raw PyLabRobot state format from serialize_all_state()
 */
export type PlrState = Record<string, PlrResourceState>;

export interface PlrResourceState {
    // TipTracker format (LiquidHandler channels)
    head_state?: Record<string, { tip: unknown | null; tip_state: unknown; pending_tip: unknown }>;

    // VolumeTracker format (Container/Well)
    volume?: number;
    pending_volume?: number;
    thing?: string;
    max_volume?: number;

    // Other resource properties
    [key: string]: unknown;
}

/**
 * Extract tip state from PLR state.
 *
 * Searches for liquid handler state (identified by "head_state" key) and counts
 * how many channels have tips loaded.
 */
export function extractTipState(plrState: PlrState): TipStateSnapshot {
    let tipsLoaded = false;
    let tipsCount = 0;

    for (const resourceState of Object.values(plrState)) {
        if (typeof resourceState !== 'object' || resourceState === null) {
            continue;
        }

        // Check for liquid handler state (has "head_state" key)
        if ('head_state' in resourceState && resourceState.head_state) {
            const headState = resourceState.head_state;

            if (typeof headState === 'object') {
                for (const channelState of Object.values(headState)) {
                    if (
                        typeof channelState === 'object' &&
                        channelState !== null &&
                        'tip' in channelState &&
                        channelState.tip !== null
                    ) {
                        tipsCount++;
                    }
                }
            }

            tipsLoaded = tipsCount > 0;
            break; // Only one liquid handler expected
        }
    }

    return { tips_loaded: tipsLoaded, tips_count: tipsCount };
}

/**
 * Extract liquid volumes from PLR state.
 *
 * Searches for resources with VolumeTracker state (identified by "volume" key)
 * and organizes them by parent resource (plate) and well identifier.
 */
export function extractLiquidVolumes(plrState: PlrState): Record<string, WellVolumeMap> {
    const liquids: Record<string, WellVolumeMap> = {};

    for (const [resourceName, resourceState] of Object.entries(plrState)) {
        if (typeof resourceState !== 'object' || resourceState === null) {
            continue;
        }

        // Check for volume tracker state (has "volume" key)
        if ('volume' in resourceState && typeof resourceState.volume === 'number') {
            const volume = resourceState.volume;

            // Only include resources with non-zero volume
            if (volume > 0) {
                const parentName = inferParentName(resourceName);
                const wellId = inferWellId(resourceName);

                if (!liquids[parentName]) {
                    liquids[parentName] = {};
                }

                liquids[parentName][wellId] = volume;
            }
        }
    }

    return liquids;
}

/**
 * Infer parent plate name from well resource name.
 *
 * Common naming patterns:
 * - "plate_name_A1" -> "plate_name"
 * - "source_plate_well_A1" -> "source_plate"
 * - "A1" -> "unknown_plate"
 */
export function inferParentName(resourceName: string): string {
    // Pattern: anything ending in _[A-P][1-24] or _well_[A-P][1-24]
    const match = resourceName.match(/^(.+?)(?:_well)?_([A-P]\d{1,2})$/i);
    if (match) {
        return match[1];
    }

    // If no pattern match, check if it looks like a standalone well ID
    if (/^[A-P]\d{1,2}$/i.test(resourceName)) {
        return 'unknown_plate';
    }

    // Otherwise, treat the whole name as the resource identifier
    return resourceName;
}

/**
 * Infer well ID from resource name.
 */
export function inferWellId(resourceName: string): string {
    // Pattern: extract [A-P][1-24] from end of name
    const match = resourceName.match(/([A-P]\d{1,2})$/i);
    if (match) {
        return match[1].toUpperCase();
    }

    return resourceName;
}

/**
 * Get list of resource names currently on deck.
 */
export function getOnDeckResources(plrState: PlrState): string[] {
    return Object.keys(plrState);
}

/**
 * Transform PyLabRobot state to frontend StateSnapshot format.
 *
 * This is the main entry point for state transformation.
 */
export function transformPlrState(plrState: PlrState | null | undefined): StateSnapshot | null {
    if (!plrState || Object.keys(plrState).length === 0) {
        return null;
    }

    const tipState = extractTipState(plrState);
    const liquids = extractLiquidVolumes(plrState);
    const onDeck = getOnDeckResources(plrState);

    return {
        tips: tipState,
        liquids,
        on_deck: onDeck,
        raw_plr_state: plrState,
    };
}
```

---

### Phase 5: SqliteService.getRunStateHistory() Implementation

**File**: `praxis/web-client/src/app/core/services/sqlite.service.ts`
**Effort**: 2-3 hours

Replace the mock implementation with real data retrieval:

```typescript
import { transformPlrState } from '../utils/state-transform';
import type { StateHistory, OperationStateSnapshot, StateSnapshot } from '../models/simulation.models';

/**
 * Get state history for a protocol run (time travel debugging).
 *
 * Queries function_call_logs for the run and transforms PLR state
 * to frontend format.
 */
public getRunStateHistory(runId: string): Observable<StateHistory | null> {
    return this.db$.pipe(
        map(db => {
            try {
                // Get protocol run info
                const runResult = db.exec(
                    `SELECT name FROM protocol_runs WHERE accession_id = ?`,
                    [runId]
                );

                const protocolName = runResult.length > 0 && runResult[0].values.length > 0
                    ? (runResult[0].values[0][0] as string) || 'Unknown'
                    : 'Unknown';

                // Get function call logs for this run
                const logsResult = db.exec(
                    `SELECT
                        accession_id,
                        sequence_in_run,
                        name,
                        status,
                        input_args_json,
                        state_before_json,
                        state_after_json,
                        start_time,
                        end_time,
                        duration_ms,
                        error_message_text
                     FROM function_call_logs
                     WHERE protocol_run_accession_id = ?
                     ORDER BY sequence_in_run ASC`,
                    [runId]
                );

                if (logsResult.length === 0 || logsResult[0].values.length === 0) {
                    // No function call logs - fall back to mock for now
                    // In production, this means the protocol didn't use logging
                    return this.createMockStateHistory(runId, protocolName);
                }

                const operations: OperationStateSnapshot[] = [];
                let finalState: StateSnapshot | null = null;
                let totalDurationMs = 0;

                for (const row of logsResult[0].values) {
                    const [
                        accessionId,
                        sequenceInRun,
                        name,
                        status,
                        inputArgsJson,
                        stateBeforeJson,
                        stateAfterJson,
                        startTime,
                        endTime,
                        durationMs,
                        errorMessage,
                    ] = row;

                    // Parse and transform states
                    const rawStateBefore = stateBeforeJson
                        ? JSON.parse(stateBeforeJson as string)
                        : null;
                    const rawStateAfter = stateAfterJson
                        ? JSON.parse(stateAfterJson as string)
                        : null;

                    const stateBefore = transformPlrState(rawStateBefore);
                    const stateAfter = transformPlrState(rawStateAfter);

                    // Parse args
                    const args = inputArgsJson
                        ? JSON.parse(inputArgsJson as string)
                        : undefined;

                    // Map status
                    const opStatus: 'completed' | 'failed' | 'skipped' =
                        status === 'COMPLETED' ? 'completed' :
                        status === 'FAILED' ? 'failed' : 'skipped';

                    // Create operation snapshot
                    const operation: OperationStateSnapshot = {
                        operation_index: sequenceInRun as number,
                        operation_id: accessionId as string,
                        method_name: name as string,
                        args,
                        state_before: stateBefore || this.getEmptyState(),
                        state_after: stateAfter || this.getEmptyState(),
                        timestamp: startTime as string,
                        duration_ms: durationMs as number,
                        status: opStatus,
                        error_message: errorMessage as string | undefined,
                    };

                    operations.push(operation);

                    // Track final state and duration
                    if (stateAfter) {
                        finalState = stateAfter;
                    }
                    if (typeof durationMs === 'number') {
                        totalDurationMs += durationMs;
                    }
                }

                return {
                    run_id: runId,
                    protocol_name: protocolName,
                    operations,
                    final_state: finalState || this.getEmptyState(),
                    total_duration_ms: totalDurationMs,
                } as StateHistory;

            } catch (error) {
                console.warn('[SqliteService] State history retrieval failed, using mock:', error);
                return this.createMockStateHistory(runId, 'Browser Protocol');
            }
        })
    );
}

/**
 * Get an empty state snapshot for fallback.
 */
private getEmptyState(): StateSnapshot {
    return {
        tips: { tips_loaded: false, tips_count: 0 },
        liquids: {},
        on_deck: [],
    };
}
```

---

### Phase 6: Update Protocol Execution Code Generation

**File**: `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts`
**Effort**: 30 minutes

Update `buildProtocolExecutionCode()` to inject the run ID and enable function call logging:

```typescript
private buildProtocolExecutionCode(
    protocol: any,
    parameters?: Record<string, unknown>,
    assetSpecs?: Record<string, any>,
    runId?: string  // NEW PARAMETER
): string {
    // ... existing code ...

    return `
# Browser mode protocol execution
import json
import time  # NEW
from web_bridge import resolve_parameters, patch_state_emission, patch_function_call_logging  # MODIFIED

print("[Browser] Setting up simulation environment...")

# ... existing import and setup code ...

# Resolve parameters (instantiate PLR objects for plates/etc)
print("[Browser] Resolving parameters...")
resolved_params = resolve_parameters(params, metadata, asset_reqs, asset_specs)

# Patch for function call logging AND real-time state emission
for p_value in resolved_params.values():
    try:
        from pylabrobot.liquid_handling import LiquidHandler
        if isinstance(p_value, LiquidHandler):
            patch_state_emission(p_value)
            patch_function_call_logging(p_value, '${runId}')  # NEW
    except ImportError:
        pass

# Execute the protocol
print("[Browser] Executing protocol...")
result = ${functionName}(**resolved_params) if resolved_params else ${functionName}()
print(f"[Browser] Protocol finished with result: {result}")
`;
}
```

Also update the call site in `executeBrowserProtocol()`:

```typescript
// Build Python code to execute the protocol
const code = this.buildProtocolExecutionCode(protocol, parameters, assetSpecs, runId);  // ADD runId
```

---

## Testing Strategy

### Phase 7: Testing (Effort: 2-3 hours)

#### 7.1 Unit Tests for TypeScript Transformation

Create `praxis/web-client/src/app/core/utils/state-transform.spec.ts`:

```typescript
import {
    extractTipState,
    extractLiquidVolumes,
    inferParentName,
    inferWellId,
    transformPlrState
} from './state-transform';

describe('State Transform', () => {
    describe('extractTipState', () => {
        it('should return no tips for empty state', () => {
            const result = extractTipState({});
            expect(result.tips_loaded).toBe(false);
            expect(result.tips_count).toBe(0);
        });

        it('should count loaded tips from liquid handler head_state', () => {
            const plrState = {
                liquid_handler: {
                    head_state: {
                        '0': { tip: { name: 'tip_0' }, tip_state: {}, pending_tip: null },
                        '1': { tip: null, tip_state: null, pending_tip: null },
                        '2': { tip: { name: 'tip_2' }, tip_state: {}, pending_tip: null },
                    }
                }
            };

            const result = extractTipState(plrState);
            expect(result.tips_loaded).toBe(true);
            expect(result.tips_count).toBe(2);
        });
    });

    describe('extractLiquidVolumes', () => {
        it('should extract volumes grouped by plate', () => {
            const plrState = {
                source_plate_A1: { volume: 250.0, pending_volume: 250.0, thing: 'source_plate_A1', max_volume: 350.0 },
                source_plate_A2: { volume: 100.0, pending_volume: 100.0, thing: 'source_plate_A2', max_volume: 350.0 },
                dest_plate_A1: { volume: 50.0, pending_volume: 50.0, thing: 'dest_plate_A1', max_volume: 350.0 },
            };

            const result = extractLiquidVolumes(plrState);
            expect(result['source_plate']).toEqual({ A1: 250.0, A2: 100.0 });
            expect(result['dest_plate']).toEqual({ A1: 50.0 });
        });

        it('should exclude zero volumes', () => {
            const plrState = {
                plate_A1: { volume: 0, pending_volume: 0, thing: 'plate_A1', max_volume: 350.0 },
                plate_A2: { volume: 100.0, pending_volume: 100.0, thing: 'plate_A2', max_volume: 350.0 },
            };

            const result = extractLiquidVolumes(plrState);
            expect(result['plate']).toEqual({ A2: 100.0 });
        });
    });

    describe('inferParentName', () => {
        it('should extract plate name from well resource name', () => {
            expect(inferParentName('source_plate_A1')).toBe('source_plate');
            expect(inferParentName('dest_plate_B12')).toBe('dest_plate');
            expect(inferParentName('my_plate_well_H8')).toBe('my_plate');
        });

        it('should return unknown_plate for standalone well IDs', () => {
            expect(inferParentName('A1')).toBe('unknown_plate');
        });
    });

    describe('transformPlrState', () => {
        it('should return null for null/undefined input', () => {
            expect(transformPlrState(null)).toBeNull();
            expect(transformPlrState(undefined)).toBeNull();
        });

        it('should transform complete PLR state', () => {
            const plrState = {
                liquid_handler: {
                    head_state: {
                        '0': { tip: { name: 'tip_0' }, tip_state: {}, pending_tip: null }
                    }
                },
                source_plate_A1: { volume: 250.0, pending_volume: 250.0, thing: 'source_plate_A1', max_volume: 350.0 },
            };

            const result = transformPlrState(plrState);

            expect(result).not.toBeNull();
            expect(result!.tips.tips_loaded).toBe(true);
            expect(result!.tips.tips_count).toBe(1);
            expect(result!.liquids['source_plate']).toEqual({ A1: 250.0 });
            expect(result!.on_deck).toContain('liquid_handler');
            expect(result!.on_deck).toContain('source_plate_A1');
            expect(result!.raw_plr_state).toBe(plrState);
        });
    });
});
```

#### 7.2 Integration Test

Manual test procedure:
1. Start the browser mode application
2. Run a simple protocol with aspirate/dispense operations
3. After completion, open State Inspector tab
4. Verify timeline shows real operations (not mock data)
5. Verify state snapshots show correct tip counts and volumes

#### 7.3 Comparison Test

Run the same protocol in backend mode and browser mode, compare state history output for consistency.

---

## File Summary

| File | Action | Purpose |
|------|--------|---------|
| `praxis/web-client/src/assets/python/web_bridge.py` | MODIFY | Add `patch_function_call_logging()` and helpers |
| `praxis/web-client/src/app/core/workers/python.worker.ts` | MODIFY | Handle `FUNCTION_CALL_LOG` message type |
| `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts` | MODIFY | Persist function call logs, pass runId to code gen |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | MODIFY | Add `createFunctionCallLog()`, update `getRunStateHistory()` |
| `praxis/web-client/src/app/core/utils/state-transform.ts` | CREATE | TypeScript state transformation utilities |
| `praxis/web-client/src/app/core/utils/state-transform.spec.ts` | CREATE | Unit tests for transformation |

---

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Performance**: State serialization overhead | Medium | Only serialize on function boundaries, not every instruction |
| **Storage**: Large JSON in SQLite | Medium | Monitor size; can add delta compression in future |
| **Pyodide errors**: Serialization failures | Medium | Wrap in try/catch, log warnings, continue execution |
| **Type mismatches**: PLR state format changes | Low | Use `raw_plr_state` fallback; add validation |

---

## Success Criteria

1. **Function call logs are persisted**: After browser protocol execution, `function_call_logs` table contains entries with state data
2. **State Inspector shows real data**: Timeline displays actual operations from protocol execution, not mock data
3. **State transformation is accurate**: Tip counts and liquid volumes match actual protocol behavior
4. **No regression**: Existing browser mode functionality continues to work

---

## Appendix: Message Type Reference

### New Message: FUNCTION_CALL_LOG

**Direction**: Pyodide Python -> Worker -> Main Thread

**Payload**:
```typescript
{
    call_id: string;           // UUID for the function call
    run_id: string;            // Protocol run ID
    sequence: number;          // Order in execution (0, 1, 2, ...)
    method_name: string;       // e.g., "aspirate", "dispense"
    args: Record<string, unknown>;  // Serialized arguments
    state_before: Record<string, unknown> | null;  // Raw PLR state
    state_after: Record<string, unknown> | null;   // Raw PLR state
    status: "running" | "completed" | "failed";
    start_time: number;        // Unix timestamp (seconds)
    end_time?: number;         // Unix timestamp (seconds)
    duration_ms?: number;      // Elapsed time
    error_message?: string;    // If failed
}
```

---

## Next Steps

1. **Review this plan** - User approval required before execution
2. **Create feature branch** - `feature/FE-02-browser-state-inspection`
3. **Implement Phase 1-6** - Follow implementation order
4. **Test Phase 7** - Unit tests, integration, comparison
5. **Update task README** - Mark phases complete

**Awaiting approval to proceed with implementation.**
