# Browser Mode Issues & Feature Gaps

**Priority**: P1 (Critical)
**Owner**: Full Stack
**Created**: 2026-01-02
**Status**: Mostly Resolved - 1 item remaining (Execution Monitor Filters)

---

## Overview

Despite many features being marked as complete in the development matrix, manual browser mode verification has revealed significant gaps between documented status and actual functionality. This document tracks all browser-mode-specific issues that need resolution.

---

## P1 - Critical Issues (Features Not Working)

### 1. ✅ Asset Manager - Items/Groupings Now Rendering

- **Status**: Fixed (2026-01-02)
- **Root Cause**: `AssetService` always used HTTP calls, ignoring browser mode
- **Fix**: Updated `AssetService` to route to `SqliteService` repositories when `ModeService.isBrowserMode()` is true
- **Verified**: Machines tab shows machines, Resources tab shows accordions, Registry shows definitions

### 2. ✅ Resource Addition Now Working

- **Status**: Fixed (2026-01-04)
- **Root Cause**: The database schema uses Joined Table Inheritance (separate `assets` and `resources` tables), but `ResourceRepository.create()` only inserted into `resources`, missing required Asset fields.
- **Fix**:
  - Updated `AssetService.createResource()` to include `fqn` and `asset_type` fields
  - Overrode `ResourceRepository.create()` to split insertions between `assets` and `resources` tables
  - Same fix applied to `MachineRepository.create()` for consistency
  - Fixed `SqliteService.seedMockData()` to align with normalized schema
- **Files Changed**:
  - `repositories.ts` - Added multi-table insert logic for Resources and Machines
  - `asset.service.ts` - Added fqn/asset_type generation for browser mode
  - `sqlite.service.ts` - Fixed mock data seeding
- **Verified**: Production build succeeds, type errors resolved

### 3. ✅ Start Execution Not Working (FIXED)

- **Expected**: "Run" button starts protocol execution
- **Actual**: ~~Execution does not start in browser mode~~ **FIXED**
- **Solution**: Added browser mode detection to `ExecutionService.startRun()`. In browser mode, execution routes through `PythonRuntimeService` (Pyodide worker) instead of HTTP calls.
- **Files Changed**:
  - `execution.service.ts` - Added browser mode execution path
  - `sqlite.service.ts` - Added `getProtocolById()` method
- **Tests**: Unit tests pass (32/32), E2E test added (`execution-browser.spec.ts`)

### 4. API Docs Not Rendering

- **Expected**: OpenAPI/Swagger docs accessible
- **Actual**: Docs not rendering despite backlog item marked complete
- **Related Backlog**: [docs.md](./docs.md)

### 5. ✅ Schema-Defined Data Views Now Rendering

- **Status**: Fixed (2026-01-02)
- **Root Cause**: Frontend `ProtocolDefinition` interface was missing the `data_views` field
- **Fix**: Added `DataViewMetadataModel` interface and `data_views` field to `protocol.models.ts`
- **Note**: Home screen "traces" are a separate P3 feature (#18)

### 6. ✅ Hardware Inference Button Missing

- **Status**: Fixed (2026-01-02)
- **Fix**: Created `HardwareDiscoveryButtonComponent` and integrated into Home, Assets, REPL, Run Protocol, and Command Palette.

### 7. Execution Monitor Filters Not Working

- **Expected**: Filters (status, protocol, date range) affect run list
- **Actual**: Filters exist but don't filter runs
- **UI Issue**: Filters should be in horizontally scrollable flex container

### 8. ✅ OT2 Slot Type Inference Now Rendering

- **Status**: Fixed (2026-01-03)
- **Root Cause**: `DeckCatalogService` only had Hamilton STAR specs hardcoded. OT-2 uses slot-based layout (12 numbered slots in 4x3 grid) vs Hamilton's rail/carrier model.
- **Fix**:
  - Added `DeckLayoutType` and `DeckSlotSpec` interfaces to `deck-layout.models.ts`
  - Added `getOTDeckSpec()` with 12 slot positions matching PyLabRobot's `OTDeck.slot_locations`
  - Added slot boundary rendering with labels to `DeckViewComponent`
  - Implementation is generic, not OT-2 specific (works for any slot-based deck)
- **Verified**: Unit tests pass, slot boundaries and labels render correctly

### 9. Database Sync Issue

- **Expected**: Browser mode praxis.db reflects current PLR definitions
- **Actual**: Features in browser mode (and possibly production) out of sync with DB
- **Notes**: This may be a root cause for multiple rendering issues

---

## P2 - High Priority Issues

### 10. Deck Display Inconsistency

- **Expected**: Run Protocol deck display matches standalone Deck View
- **Actual**: Different rendering between the two contexts
- **Issue**: All decks render as same hardcoded thing rather than dynamic from machine/deck definition

### 11. Machine Input Params as JSON

- **Expected**: Nice form UI for connection info and input params when adding machines
- **Actual**: Raw JSON input field instead of structured form
- **Related Backlog**: [dynamic_form_generation.md](./dynamic_form_generation.md)

### 12. ✅ Backend Config - Limited Machine Types

- **Status**: Fixed (2026-01-02)
- **Expected**: Can manually add various machine types
- **Actual**: Only "chatterbox" appears in manual add options
- **Fix**: Updated `PLRSourceParser` logic to correctly map generic machine frontends (like `LiquidHandler`) to all compatible backends (like `STAR`, `OT2`), and regenerated browser DB.
- **Notes**: Backend machine type config needs expansion

### 13. ✅ Button Selector Checkmark Display

- **Status**: Fixed (2026-01-03)
- **Fix**: Added `hideSingleSelectionIndicator` to all `mat-button-toggle-group` instances (Execution Monitor, Run Protocol, Assets, Settings) to remove redundant checkmarks and rely on background/border for selection state.
- **Verified**: Visual verification and unit tests pass.

---

## P2 - REPL Issues

### 14. ✅ REPL Light/Dark Mode

- **Status**: Fixed (2026-01-02)
- **Fix**: Updated `ReplComponent` to dynamically fetch CSS variables (`--mat-sys-surface-container-low`, `--mat-sys-on-surface`) for terminal colors, ensuring perfect match with application theme. Implemented reactive updates on theme change.
- **Verified**: Unit tests pass (`should update terminal theme when store theme changes`).

### 15. ✅ REPL Error Handling

- **Status**: Fixed (2026-01-03)
- **Root Cause**: Browser mode's `python.worker.ts` was sending `String(err)` which gave a generic JS error instead of Python traceback. Backend was using `str(e)` instead of `traceback.format_exc()`.
- **Fix**:
  - Browser mode: Updated `executePush()` in `python.worker.ts` to use `traceback.format_exc()` for full Python tracebacks
  - Backend mode: Updated `repl_session.py` to use `traceback.format_exc()` in exception handler
  - Frontend already had correct stderr styling (red via ANSI codes `\x1b[1;31m`)
- **Verified**: Python tracebacks now display with full error type, message, and line numbers

### 16. ✅ REPL Protocol Editor - Not Ready

- **Status**: Complete (2026-01-02)
- **Fix**: Disabled the Protocol Editor button in `repl.component.html` with `[disabled]="true"` and added a "Coming Soon" tooltip. Styled the disabled state for visual feedback.
- **Verified**: Unit tests pass (8/8), manual verification via browser confirms disabled state and tooltip.

### 17. ✅ REPL Easy Add Assets (FIXED)

- **Status**: Fixed (2026-01-02)
- **Expected**: Easy way to add machines/resources from inventory to REPL
- **Fix**: Added Inventory tab with "Inject Code" button that inserts machine/resource handles into REPL

---

## P3 - Graph Traces & Visualizations (COMPLETED)

### 18. ✅ Summary Card Graph Traces

- **Status**: Fixed (2026-01-03)
- **Location**: Home screen summary cards
- **Fix**: Added sparkline on Running card

### 19. ✅ Execution Monitor Graph Traces

- **Status**: Fixed (2026-01-03)
- **Location**: Run selection cards in execution monitor
- **Fix**: Added timeline with Setup→Running→Complete phases

---

## Tasks to Create

### Testing Infrastructure

- [ ] Create E2E tests for protocol execution in browser mode
- [ ] Create unit tests for SqliteService CRUD operations
- [ ] Create E2E tests for asset management add/edit/delete
- [ ] Create smoke tests for each major feature in browser mode
- [ ] Add browser mode regression test suite

### Root Cause Investigation

- [ ] Verify praxis.db contains expected PLR data (~500+ resources)
- [ ] Verify SqliteService correctly loads and queries praxis.db
- [ ] Trace execution start flow and identify failure point
- [ ] Verify API doc generation pipeline

---

## Related Backlogs

- [asset_management.md](./asset_management.md)
- [deck_view.md](./deck_view.md)
- [repl.md](./repl.md)
- [execution_monitor.md](./execution_monitor.md)
- [docs.md](./docs.md)
- [modes_and_deployment.md](./modes_and_deployment.md)

---

## Verification Checklist

After fixes, verify each feature works in:

- [ ] Browser Mode (pure client-side)
- [ ] Lite Mode (local Python server + SQLite)
- [ ] Production Mode (full backend)
