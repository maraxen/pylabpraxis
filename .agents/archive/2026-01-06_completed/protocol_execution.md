# Protocol Execution Wizard

**Priority**: High (MVP → Full Implementation)
**Owner**: Frontend
**Created**: 2026-01-01
**Status**: Planning

---

## Overview

Improve the user experience of the protocol execution wizard by persisting the state of the form across refreshes. This ensures that users don't lose their progress if they accidentally reload the page or navigate away and back.

### Current State

1. User starts protocol execution.
2. User fills out parameters, selects a machine, and configures the deck.
3. User refreshes the page.
4. **Result**: All input is lost, and the wizard resets to the first step.

### Target State

1. User starts protocol execution.
2. User fills out parameters, selects a machine, and configures the deck.
3. User refreshes the page.
4. **Result**: The wizard initializes with the previously entered values and returns the user to the specific step they were on.

---

## Implementation Details

### Persistence Strategy

- **Storage**: `LocalStorage` (sufficient for form data) or `SessionStorage` (if we want it to clear on tab close). Given "continuing where you left off", `LocalStorage` is preferred.
- **Keying**: `praxis_wizard_state_{protocolId}`. This allows multiple protocol setups to be "in progress" simultaneously (though unusual, it's safer).
- **Structure**:

  ```json
  {
    "stepIndex": 2,
    "formData": {
      "parameters": { ... },
      "machineId": "...",
      "deckMapping": [ ... ]
    },
    "timestamp": 1672564800000
  }
  ```

### Frontend Tasks

#### 1. Wizard State Service

- Create `WizardStateService` to handle CRUD operations for persistence.
- Methods: `saveState(protocolId, state)`, `getState(protocolId)`, `clearState(protocolId)`.

#### 2. RunProtocolComponent Integration

- **Hydration**: In `ngOnInit`, check for existing state.
- **Form Patching**: Patch the `FormGroup` with saved values if a state exists.
- **Stepper Control**: Set `selectedStepIndex` on the `mat-stepper` based on saved state.
- **Auto-save**: Subscribe to `valueChanges` on the main `FormGroup` (debounced) to sync to `LocalStorage`.

#### 3. State Invalidation

- Clear state when:
  - Protocol is successfully submitted to the scheduler.
  - User explicitly clicks "Cancel" or "Start Over".
  - State is older than a certain TTL (e.g., 24 hours).

---

## Implementation Phases

### Phase 1: Basic Persistence (2-3 hours)

- [ ] Create `WizardStateService`.
- [ ] Implement manual "Save Draft" or auto-save on value changes.
- [ ] Verify state is stored in `LocalStorage`.

### Phase 2: Hydration & Navigation (2-3 hours)

- [ ] Hydrate `RunProtocolComponent` forms on init.
- [ ] Restore stepper position.
- [ ] Handle edge cases (e.g., protocol definition changed since last save).

### Phase 3: Polish & Error Handling (1-2 hours)

- [ ] Add "Clear Progress" button.
- [ ] Handle schema mismatches (if protocol is updated while state exists).
- [ ] UX indicator: "Restored from draft".

---

## Success Metrics

1. **User Retention**: Progress is maintained after page refresh.
2. **Robustness**: Form does not crash if `LocalStorage` data is malformed or outdated.
3. **Transparency**: Clear way for user to reset progress.

---

## Completed Tasks ✅

### Step Rendering & Visibility (2026-01-01)

- [x] **Blank Screen Fix**: Inactive steps were NOT being collapsed correctly, pushing active content off-screen.
- [x] Targeted `.mat-horizontal-stepper-content-current` to force height visibility and `:not(...)` to collapse inactive steps.
- [x] Verified in browser that downstream steps (Machine Select, Deck Setup) render correctly.

### Stepper UX Improvements (2026-01-01)

- [x] **Label Responsiveness**: Enabled text wrapping for stepper labels (`white-space: normal`) and set `height: auto` on headers.
- [x] **Compact Layout**: Reduced header padding and font size for better fit on small screens.
- [x] **Dark Mode Contrast**: Fixed number icon text color for better readability.
- [x] **Double Text Cleanup**: Removed overlapping overlay text in the deck visualizer.

---

## Related Backlogs

- [ui-ux.md](./ui-ux.md) - General wizard improvements
- [execution_monitor.md](./execution_monitor.md) - Re-running from history (similar hydration logic)
