# Browser Mode Bug Fixes & UX Issues (260116)

**Priority**: High
**Status**: Planned
**Created**: 2026-01-16

## Overview

Critical bugs and UX issues discovered during browser mode testing after database regeneration and filter chip refactor.

---

## 🔴 Critical Issues (Blocking Core Functionality)

### 1. Machine Creation Fails - NOT NULL constraint

**Location**: `inventory-dialog.component.ts`, `MachineRepository`
**Error**:

```
openUnifiedDialog: Error Error: NOT NULL constraint failed: machines.maintenance_enabled
    at MachineRepository.create
```

**Description**: Cannot add machines because `maintenance_enabled` column is missing from INSERT statement.

**Impact**: Users cannot create machine instances, blocking all hardware setup flows.

**Fix Required**:

- Check machine creation INSERT statement in `MachineRepository`
- Add `maintenance_enabled` and `maintenance_schedule_json` fields (use defaults from generation script)
- Update inventory dialog to pass these fields

---

### 2. Mock Protocols in Database

**Location**: `sqlite.service.ts`, `assets/browser-data/protocols.ts`
**Issue**: 3 mock protocols without real implementation files:

- Daily System Maintenance
- Cell Culture Feed (24-well)
- PCR Prep (96-well)

**Description**: `MOCK_PROTOCOLS` array seeds fake protocols into the database when runs table is empty. These should be removed - all protocols should be real Python files.

**Current State**:

- 6 real protocols in `praxis/protocol/protocols/*.py`
- 3 additional mock protocols seeded via `seedDefaultRuns()`

**Fix Required**:

- Remove `MOCK_PROTOCOLS` import and usage from `sqlite.service.ts:407`
- Remove `assets/browser-data/protocols.ts` file
- Remove mock protocol references from `execution.service.ts:167`
- If demo runs needed, link them to real protocol definitions from `generate_browser_db.py`

---

### 3. Simulated Machines in Hardware Connect Screen

**Location**: Hardware connection flow
**Issue**: Simulated machines (with `is_simulation_override=1`) appear in "Connect to Hardware" screen.

**Error Example**: "Failed to connect to Opentrons OT-2 (Simulated)"

**Description**: Browser mode machines are all simulated by definition and should never show in hardware connect screens. Only real physical machines should be connectable.

**Fix Required**:

- Filter machines WHERE `is_simulation_override IS NULL OR is_simulation_override = 0` in hardware connect queries
- Or add explicit check in component/service filtering logic

---

## 🟡 High Priority (UX Blockers)

### 4. "Not Analyzed" Still Showing on Protocol Cards

**Location**: `protocol-warning-badge.component.ts`
**Issue**: Despite setting `simulation_result_json = {"status": "ready", "simulated": true}` in generation script, badge still shows "Not analyzed"

**Diagnosis Needed**:

- Verify database actually has non-null `simulation_result_json` after regeneration
- Check if IndexedDB cache was cleared (add `?resetdb=1` to URL)
- Verify `hasSimulation` logic: checks `protocol.simulation_result || protocol.failure_modes || protocol.simulation_version`
- May need to also populate `simulation_version` field

**Test Query**:

```sql
SELECT name, simulation_result_json, simulation_version, failure_modes_json
FROM function_protocol_definitions;
```

---

### 5. No Categories for Machine Selection

**Location**: `inventory-dialog.component.ts`
**Message**: "No categories available. Please select an asset type first."

**Issue**: When trying to add a machine, no categories appear even though machine_definitions exist.

**Root Cause Hypothesis**:

- May be filtering by instantiated machines instead of machine_definitions
- Should show categories from `machine_definitions.machine_category` not `machines.machine_category`
- Need simulated backend option even with empty machines table

**Fix Required**:

- Check if component queries `getMachines()` vs `getMachineDefinitions()`
- Ensure category list comes from definitions catalog
- Always show "Simulated" as a backend option

---

### 6. GroupBy Does Not Work in Inventory

**Location**: `view-controls.component.ts` or inventory filtering logic
**Issue**: Setting groupBy to "none" (null) nothing happens in the inventory view, it remains grouped by the previous selection. there are also duplicate None fields.

**Error**: (Need to capture specific error message)

**Fix Required**:

- Add null check for `groupBy` value in filtering/grouping logic
- Ensure "None" option properly sets `groupBy: null` instead of `groupBy: "none"` string

---

### 7. Missing Deck Definitions

**Location**: `generate_browser_db.py:discover_decks_static()`
**Issue**: Only 2 deck definitions found, missing major decks:

- Hamilton STAR/Vantage decks
- Tecan decks

**Current Output**:

```
[generate_browser_db] Inserted 2 deck definitions
```

**Expected**: Should have 10+ deck definitions

**Diagnosis Needed**:

- Check if `PLRSourceParser.discover_resource_classes()` filters to `PLRClassType.DECK`
- Verify PyLabRobot actually has these as Resource classes vs other structure
- May need to discover deck classes differently

**Test**:

```python
from praxis.backend.utils.plr_static_analysis import PLRSourceParser, PLRClassType, find_plr_source_root
parser = PLRSourceParser(find_plr_source_root())
all_resources = parser.discover_resource_classes()
decks = [r for r in all_resources if r.class_type == PLRClassType.DECK]
print(f"Found {len(decks)} decks: {[d.name for d in decks]}")
```

---

## 🟢 Medium Priority (Polish & UX)

### 8. Dialog Spacing Issues

**Location**: `inventory-dialog.component.ts`, `add-asset-dialog`
**Issue**: Spacing is off in Add Asset and Add Machine dialogs

**Details**: (Need specific measurements/screenshots)

**Constraint**: **NO HORIZONTAL SCROLLING** should be required for the entire canvas.

- Vertical scrolling is preferred.
- Sub-components (like tables or grid rows) may scroll horizontally if strictly necessary, but the main dialog container must fit within the viewport width without scrolling.
- The UX must feel natural and contained.

---

### 9. Execution Machine Selection

**Location**: Run protocol execution flow
**Issue**: "Select execution machine" only shows one option instead of letting you pick backend for each frontend type.

**Expected Behavior**:

- User selects frontend machine type (e.g., "LiquidHandler")
- System shows available backends for that type
- User can pick specific backend implementation

**Current Behavior**: Only shows a single machine option

**Fix Required**:

- Separate frontend selection from backend selection
- Query machine_definitions filtered by frontend_fqn
- Show backend picker for selected frontend

---

### 10. Well Index Restrictions Not Enforced

**Location**: Protocol parameter inputs
**Issue**: Well indexes that should be tied and restricted are not validated

**Example**: Source wells and destination wells should have matching counts

**Note**: Acknowledged as technical debt - defer to future validation enhancement task

---

### 11. Deck State Not Updating in Guided Setup

**Location**: Guided setup component
**Issue**: When resources are added via checkboxes, the deck state doesn't show them as added immediately (requires refresh)

**Expected**: Real-time update showing resource count on related cards

**Current**: Delay before seeing resource count change (refresh required)

**Fix Required**:

- Add reactive signal or observable to deck state
- Trigger change detection when resources added
- Or: acceptable delay if state eventually syncs?

---

## 🔵 Low Priority (Technical Debt)

### 12. Tutorial Completion Error

**Location**: `tutorial.service.ts:302`
**Error**:

```
ERROR RangeError: Maximum call stack size exceeded
    at Step.destroy (shepherd.mjs:4527:3)
    at shepherd.mjs:5462:39
    at Array.forEach (<anonymous>)
    at Tour._done (shepherd.mjs:5462:18)
    at Tour.complete (shepherd.mjs:5338:10)
    at _TutorialService.onComplete (tutorial.service.ts:302:19)
```

**Issue**: Tutorial errors at completion and doesn't return full control to app

**Impact**: Non-critical, but poor first-time user experience

**Defer**: Tutorial refactor task

---

## Testing Checklist

After fixes, verify:

- [ ] Can create machines with all required fields
- [ ] Machine categories show when adding machines
- [ ] No mock protocols appear in library
- [ ] All 6 real protocols show "Ready" status (green checkmark)
- [ ] Simulated machines don't appear in hardware connect
- [ ] GroupBy "None" works in inventory without crashing
- [ ] Deck definitions include STAR, Vantage, Tecan decks
- [ ] Dialog spacing looks correct
- [ ] Backend selection works for machine instantiation
- [ ] Deck state updates reactively (or document expected delay)

---

## Files to Modify

**High Priority**:

- `praxis/web-client/src/app/core/db/repositories.ts` - MachineRepository.create()
- `praxis/web-client/src/app/core/services/sqlite.service.ts` - Remove MOCK_PROTOCOLS
- `praxis/web-client/src/assets/browser-data/protocols.ts` - DELETE FILE
- `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts` - Remove mock refs
- Hardware connect component/service - Filter simulated machines
- `scripts/generate_browser_db.py` - Fix deck discovery

**Medium Priority**:

- `praxis/web-client/src/app/shared/components/protocol-warning-badge/protocol-warning-badge.component.ts` - Debug hasSimulation
- `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts` - Category filtering
- `praxis/web-client/src/app/shared/components/view-controls/view-controls.component.ts` - GroupBy null handling
- Machine instantiation flow - Backend selection UX

---

## Related Tasks

- `260115_feature_enhancements/sim_machines_visibility/` - Machine seeding fixes (COMPLETED)
- `260115_feature_enhancements/view_controls_chips/` - Filter chip refactor (COMPLETED)
- `260115_tech_debt/frontend_type_safety/` - Type safety improvements (IN PROGRESS)

---

## Notes

- Database regeneration script now working correctly for resources/machines/backends
- Filter chip refactor complete - one chip per value with gradient styling
- Resource adding IS working (just has UI delay before count updates)
