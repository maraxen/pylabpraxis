# State Inspection Backend - Investigation Summary

**Date**: 2026-01-16
**Status**: Investigation Complete ✅
**Surprising Result**: 95% already implemented, only needs state transformation layer

---

## Executive Summary

The state inspection backend feature is **almost entirely complete**. The schema, execution capture, API endpoint, and frontend service all exist and are functional. The only missing piece is a **state format transformation layer** in the API endpoint to convert PyLabRobot's raw state format into the structured format expected by the frontend.

**Estimated Effort**: Small (1-2 hours)
**Risk Level**: Low (isolated change, no schema modifications needed)

---

## Component Status

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| Schema Fields | ✅ Complete | `models/domain/protocol.py:592-597` | `state_before_json`, `state_after_json` exist |
| State Capture | ✅ Complete | `decorators/protocol_decorator.py:92-97, 384-399` | Captures before/after every decorated function |
| Persistence | ✅ Complete | `services/protocols.py:469-526` | Both `log_function_call_start()` and `log_function_call_end()` |
| API Endpoint | ⚠️ Needs Transform | `api/protocols.py:192-256` | Endpoint exists but returns raw PLR state |
| Frontend Service | ✅ Complete | `simulation-results.service.ts:89-117` | Calls endpoint correctly |
| Frontend Models | ✅ Complete | `simulation.models.ts` | TypeScript interfaces defined |

---

## Critical Files

### Backend - State Capture

1. **`praxis/backend/core/decorators/protocol_decorator.py`**
   - Lines 92-97: `_log_call_start()` captures `state_before` via `context.runtime.get_state_snapshot()`
   - Lines 384-399: Wrapper finally block captures `state_after` after function execution
   - Already handles exceptions gracefully with try/catch around state capture

2. **`praxis/backend/core/workcell_runtime/state_sync.py`**
   - Lines 188-190: `get_state_snapshot()` delegates to `_main_workcell.serialize_all_state()`
   - This is the interface between execution and workcell state

3. **`praxis/backend/core/workcell.py`**
   - Lines 165-171: `serialize_all_state()` iterates all resources and calls PLR's `serialize_state()`
   - Returns: `{resource_name: resource_plr_state_dict}`

### Backend - Persistence

4. **`praxis/backend/services/protocols.py`**
   - Lines 469-494: `log_function_call_start()` creates `FunctionCallLog` with `state_before_json`
   - Lines 498-526: `log_function_call_end()` updates with `state_after_json`
   - Both handle None values gracefully (nullable fields)

### Backend - API

5. **`praxis/backend/api/protocols.py`**
   - Lines 192-256: `get_run_state_history()` endpoint
   - Lines 226-235: `wrap_state()` helper - **THIS IS WHERE TRANSFORMATION NEEDED**
   - Currently returns empty tips/liquids and stores raw state in `raw_plr_state`

### Frontend

6. **`praxis/web-client/src/app/core/services/simulation-results.service.ts`**
   - Lines 89-117: `getStateHistory()` fetches from backend endpoint
   - Lines 169-177: `getStateHistoryFromBrowserMode()` for browser mode (separate implementation)

7. **`praxis/web-client/src/app/core/models/simulation.models.ts`**
   - Lines 124-133: `StateSnapshot` interface definition
   - Lines 138-145: `TipStateSnapshot` interface
   - Lines 156-167: `StateHistory` interface

---

## State Format Analysis

### PyLabRobot Raw Format

Based on `Workcell.serialize_all_state()`, the state returned is:

```python
{
    "tip_rack_1": { /* TipRack.serialize_state() */ },
    "source_plate": { /* Plate.serialize_state() */ },
    "dest_plate": { /* Plate.serialize_state() */ },
    "liquid_handler": { /* LiquidHandler.serialize_state() */ }
}
```

**PyLabRobot Resource State Structure** (approximate, needs verification):
- `Plate.serialize_state()`: Likely contains well tracking info, volumes
- `TipRack.serialize_state()`: Tip status per position
- `LiquidHandler.serialize_state()`: Tips loaded, current positions, etc.

**Note**: Exact PLR state structure needs runtime inspection or PLR source code review.

### Frontend Expected Format

```typescript
interface StateSnapshot {
    tips: {
        tips_loaded: boolean;    // Are tips currently picked up?
        tips_count: number;      // How many tips loaded (for multi-channel)?
        tip_usage?: Record<string, number>; // Optional: tip rack consumption
    };
    liquids: {
        [resource_name: string]: {  // e.g., "source_plate"
            [well: string]: number  // e.g., "A1": 250.0 (µL)
        }
    };
    on_deck: string[];           // List of resource names on deck
    raw_plr_state?: any;         // Fallback for custom visualization
}
```

---

## Transformation Requirements

### 1. Extract Tip State

**Source**: Liquid handler state within PLR state dict
**Challenge**: Need to identify which resource is the liquid handler
**Extraction**:
- Check if resource has "liquid_handler" in category or type
- Extract `tips_loaded` boolean from handler state
- Extract `tips_count` from handler state (default to 8 for STAR?)

### 2. Extract Liquid Volumes

**Source**: Plate resources within PLR state dict
**Challenge**: Distinguish plates from other resources
**Extraction**:
- Check if resource has "plate" or "container" in category/type
- Parse well tracking from plate state
- Map to `{well_id: volume_ul}` format

### 3. Extract On-Deck Resources

**Source**: Keys of PLR state dict
**Challenge**: None - straightforward
**Extraction**:
- Return `list(plr_state.keys())`

### 4. Handle Edge Cases

- **Empty state**: Return empty structures, not None
- **Missing liquid handler**: `tips_loaded = False`, `tips_count = 0`
- **No plates**: `liquids = {}`
- **Unknown resource types**: Include in `on_deck`, ignore for tips/liquids

---

## Implementation Strategy

### Option A: API Transformation (Recommended)

**Location**: `praxis/backend/api/protocols.py:226-235`

**Pros**:
- Isolated change
- No schema modifications
- Easier to test
- Frontend remains unchanged

**Cons**:
- Requires understanding PLR state format
- May need updates if PLR changes

**Implementation**:
```python
def wrap_state(plr_state):
    if not plr_state:
        return None

    tips = extract_tip_state(plr_state)
    liquids = extract_liquid_volumes(plr_state)
    on_deck = list(plr_state.keys())

    return StateSnapshot(
        tips=TipStateSnapshot(**tips),
        liquids=liquids,
        on_deck=on_deck,
        raw_plr_state=plr_state
    )
```

### Option B: Workcell Transformation

**Location**: Add new method to `Workcell` class

**Pros**:
- Centralized transformation logic
- Reusable by other consumers

**Cons**:
- Couples workcell to frontend format
- Broader change scope

**Not recommended** unless multiple consumers need this format.

---

## Testing Strategy

### 1. Unit Tests

Create test for `wrap_state()` transformation:
- Mock PLR state dict with sample plate/handler data
- Assert correct extraction of tips/liquids/on_deck
- Test edge cases (empty state, missing handler, etc.)

### 2. Integration Tests

Add to `tests/api/test_protocol_runs.py`:
- Run a simple protocol (e.g., pick_up_tips, aspirate, dispense)
- Call `/runs/{run_id}/state-history` endpoint
- Assert `state_before` and `state_after` have populated tips/liquids

### 3. Manual Verification

- Run test protocol through full execution
- Query DB: `SELECT state_before_json FROM function_call_logs LIMIT 1;`
- Verify state capture is working
- Call API endpoint
- Verify transformation produces expected format

### 4. Frontend Verification

- Open State Inspector in UI
- Load a completed run
- Verify timeline renders with state snapshots
- Check that tip state and liquid volumes display correctly

---

## Open Questions

1. **PLR State Format**: What is the exact structure returned by PyLabRobot's `serialize_state()` for different resource types?
   - **Resolution**: Need to inspect runtime state or review PLR source code
   - **Impact**: Medium - affects transformation logic accuracy

2. **Multi-Channel Tips**: How to determine tip count for different liquid handler models?
   - **Resolution**: Check handler definition or use default (8 for STAR)
   - **Impact**: Low - defaults acceptable for MVP

3. **Well Volume Tracking**: Does PLR track volumes, or is this Praxis-managed?
   - **Resolution**: Check if plates in state dict have volume info
   - **Impact**: High - may need alternative source if not in PLR state

4. **Resource Type Detection**: How to reliably identify plates vs. tip racks vs. other resources?
   - **Resolution**: Check `category` field or class name in state dict
   - **Impact**: Medium - affects correct categorization

---

## Performance Considerations

### Current State

- State capture happens on **every decorated function call**
- For a protocol with 100 operations, creates 100 `FunctionCallLog` entries
- Each entry stores full state snapshot (before + after)
- Typical state size: ~10-50 KB JSON per snapshot (estimated)
- Storage per run: ~1-5 MB for typical protocols

### Optimization Opportunities (Future)

1. **Delta Compression**: Only store changes between states
   - Reduces storage by ~80-90%
   - Complicates retrieval (need to reconstruct state)

2. **Selective Capture**: Flag for "capture state" vs. "skip capture"
   - User chooses whether to enable detailed tracking
   - Reduces overhead for production runs

3. **Aggregation**: Only capture state at top-level function boundaries
   - Reduces granularity but improves performance
   - May miss intermediate state changes

**Current Status**: No optimization needed for MVP, storage acceptable for typical use

---

## Browser Mode Considerations

**Note**: Browser mode has separate implementation via `SqliteService`

- Frontend: `simulation-results.service.ts:169-177` - `getStateHistoryFromBrowserMode()`
- Current: Delegates to `SqliteService.getRunStateHistory()`
- Gap: SqliteService likely doesn't have this method yet
- Separate task needed for browser mode state history

---

## Migration Analysis

**Question**: Do we need a database migration?

**Answer**: No migration needed!

**Reason**:
- Schema fields already exist in `FunctionCallLog` model
- Fields are nullable (`| None`)
- Existing records without state will have `NULL` values
- New executions will populate these fields automatically

**Verification**:
```bash
uv run alembic current
# Should show latest revision already includes state_before_json/state_after_json
```

---

## Related Technical Debt

From `.agent/TECHNICAL_DEBT.md`:

- **TD-801**: State History Storage Optimization
  - Current implementation stores full snapshots
  - Future: implement delta compression
  - Priority: Medium (optimization, not blocker)

- **TD-802**: PLR to UI State Transformation
  - This is the PRIMARY GAP identified in this investigation
  - Needs transformation layer (exactly what we found)
  - Priority: Medium → High (required for feature completion)

- **TD-803**: Interactive Timeline Updates
  - WebSocket real-time state updates during execution
  - Currently: state only available post-run
  - Priority: Low (enhancement, not MVP requirement)

---

## Conclusion

**Task Difficulty Re-assessment**: Hard → **Easy**

The "Hard" difficulty was assigned assuming significant implementation work. However, investigation reveals:
- ✅ Schema complete
- ✅ Capture logic complete
- ✅ API endpoint complete
- ✅ Frontend service complete
- ⚠️ Only needs state transformation helper function (~50 lines of code)

**Recommendation**: Proceed to planning phase with focus on:
1. Understand exact PLR state format (inspect at runtime or read PLR docs)
2. Design `extract_tip_state()` and `extract_liquid_volumes()` helpers
3. Implement transformation in API endpoint
4. Add unit tests for transformation logic
5. Run integration test with simple protocol
6. Verify in UI

**Estimated Implementation Time**: 1-2 hours (down from original "Hard" estimate of days)
