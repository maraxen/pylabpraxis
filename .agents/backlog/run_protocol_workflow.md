# Run Protocol Workflow Enhancements

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-02
**Status**: Active

---

## Overview

Refinements to the Run Protocol workflow based on user feedback and usability testing. The main changes involve restructuring the asset configuration steps and ensuring deck display consistency.

---

## 1. Asset Configuration Step Restructure

### Current Flow

```
1. Select Protocol
2. Configure Parameters
3. Asset Selection (Resource Selection Interface + Machine Selection)
4. Deck Setup (Guided Setup Dialog)
5. Review & Run
```

### Target Flow

```
1. Select Protocol
2. Configure Parameters
3. Machine Selection (NEW - uses Resource Selection Interface pattern)
4. Asset Selection (Resources only)
5. Deck Setup (move current dialog content here as main content, not dialog)
6. Review & Run
```

### Tasks

- [x] **Add Machine Selection Step** (before Deck Setup)
  - [x] Create `MachineSelectionStepComponent`
  - [x] Use same interface pattern as current Resource Selection
  - [x] Show compatible machines based on protocol requirements
  - [x] Allow single or multi-machine selection based on protocol needs

- [x] **Refactor Deck Setup Step**
  - [x] Move current dialog content to be the main step content
  - [x] Current guided setup dialog becomes the inline experience
  - [x] Remove dialog wrapper, use step container directly

- [x] **Update Stepper Configuration**
  - [x] Add machine selection step to stepper
  - [x] Update step labels and icons
  - [x] Ensure responsive label sizing

- [x] **Restore Asset Selection Step** ~~(REGRESSION)~~ ✅ IMPLEMENTED
  - [x] Re-enabled "Asset Selection" step after Machine Selection (Lines 317-343 in run-protocol.component.ts)
  - [x] Implemented resource autofill via `<app-guided-setup>` integration
  - [x] Allow user to select specific resource candidates from inventory
  - [x] Ensure selected resources are passed to Deck Setup phase via `configuredAssets` signal

---

## 2. Deck Display Consistency

### Issue

The deck display in Run Protocol workflow does not match the standalone Deck View component. All decks appear to be the same hardcoded layout instead of dynamically rendering based on machine deck definition.

### Tasks

- [x] **Investigate Deck Display Sources**
  - [x] Compare `DeckViewComponent` used in Run Protocol vs standalone
  - [x] Identify why hardcoded layout is being used
  - [x] Trace deck definition loading in both contexts

- [x] **Dynamic Deck Rendering**
  - [x] Ensure `DeckGeneratorService` uses machine's deck definition
  - [x] Render slots vs rails based on deck type (OT2 slots, Hamilton rails)
  - [x] Apply correct dimensions from deck type definition

- [x] **Test Deck Types**
  - [x] Hamilton STAR (rails)
  - [x] Opentrons OT-2 (slots)
  - [ ] Tecan EVO (rails)
  - [x] Verify each renders correctly

---

## 3. Related Issues

### Simulation/Physical Button Selector

- [ ] Remove checkmark from button selector display
- [ ] Audit all instances of this button pattern across app
- [ ] Locations: Execution Monitor, Protocol Workflow

### Start Execution Not Working

- Tracked in: [browser_mode_issues.md](./browser_mode_issues.md)
- Impacts: Cannot complete protocol workflow in browser mode

### Workflow Blockers (2026-01-07)

- [ ] **Continue Button Issue**: Debug "Continue" button on "Select Assets" step.
- [ ] **Stepper Restriction**: Allow broader navigation within the protocol setup stepper.
- [x] **Example Protocols**: Add example protocols for no-liquid-handler and rich well selection scenarios. ✅ Added `plate_reader_assay`, `kinetic_assay`, and `selective_transfer` protocols (2026-01-09)
- [x] **Protocols Not Analyzed**: Investigate why protocols persistently show "Not Analyzed" status. Ensure analysis runs and persists correctly. ✅ FIXED

### Guided Deck Setup UI (2026-01-08 Verification)

> [!WARNING]
> User verification confirmed these issues on 2026-01-08.

- [x] **Continue/Next Button Not Visible**: After adding carriers, the Continue button is not visible
- [x] **Confirm & Continue Action Broken**: Clicking the button now advances the stepper. Verified fix on 2026-01-09.
- [x] **Container Scrolling**: Scrolling behavior fixed with independent scroll areas for item list and deck preview.
- [x] **Flex Container Fix**: Wizard uses proper flex container; footer navigation is always visible and functional.

### POST /resources/ API Error (from TECHNICAL_DEBT.md)

**Priority**: Low (workaround exists)
**Added**: 2026-01-07

**Issue:** The `POST /api/v1/resources/` endpoint returns 500 errors. Direct ORM insertion via `scripts/seed_direct.py` works.

**Workaround:** Use `scripts/seed_direct.py` for seeding resources.

**Files Affected:**

- `praxis/backend/api/resources.py`
- `praxis/backend/services/resource.py`

### Consumables & Auto-Assignment (from TECHNICAL_DEBT.md)

**Priority**: Medium
**Added**: 2026-01-07

Current auto-selection logic is naive (picks Nth item from filtered list).

**Improvements Needed:**

- [x] **(High) Fix "Buggy" Behavior**: User reported autoselection "seems buggy" (2026-01-08). Investigate failure cases.
- [x] Consider resource `status` (prefer `AVAILABLE_IN_STORAGE` over `IN_USE`)
- [ ] Check remaining capacity for consumables (partial tip racks, plates)
- [ ] Handle case where not enough unique resources exist
- [ ] UI indication when resources must be shared or duplicated
- [ ] Backend endpoint to suggest "best available" with smart ranking

**Files Affected:**

- `praxis/web-client/src/app/shared/formly-types/asset-selector.component.ts`
- `praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts`

---

## Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `run-protocol.component.ts` | Modify | Add machine selection step, restructure |
| `run-protocol.component.html` | Modify | Update stepper with new steps |
| `machine-selection-step.component.ts` | Create | New component for machine selection |
| `deck-setup-step.component.ts` | Modify | Move dialog content to main view |
| `deck-generator.service.ts` | Modify | Use dynamic deck definitions |

---

## Success Criteria

1. [x] Machine selection appears as separate step before deck setup
2. [x] Machine selection uses familiar resource selection interface
3. [x] Deck setup step shows guided setup inline (not in dialog)
4. [ ] Deck display matches standalone Deck View component
5. [ ] Different deck types (slots vs rails) render correctly
6. [ ] Simulation/Physical selector no longer shows checkmark

---

## Related Documents

- [guided_deck_setup.md](./guided_deck_setup.md) - Wizard implementation details
- [deck_view.md](./deck_view.md) - Deck visualizer backlog
- [browser_mode_issues.md](./browser_mode_issues.md) - Execution issues
