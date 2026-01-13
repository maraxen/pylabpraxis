# Agent Prompt: Monitor State & Parameter Display

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260114_frontend_feedback](../README.md)
**Difficulty:** Medium
**Dependencies:** None
**Backlog Reference:** Group D

---

## 1. The Task

Improve the Protocol Execution Monitor's state inspection and parameter display. Users report that state inspection misses some events (e.g., dispense volume moving from tip to well) and that input parameters are hard to read (raw JSON).

**Objectives:**

1. **Fix State Inspection:** Ensure dispense operations correctly show volume leaving the tip and entering the well in the "State Inspector" diff view.
2. **Improve Parameter Display:** Replace the raw JSON dump of input parameters in the Run Detail view with a user-friendly, formatted display.

---

## 2. Technical Implementation Strategy

### Part A: State Inspection (Dispense Tracking)

**Diagnosis:**
The `StateInspectorComponent` calculates diffs in `computeStateDiff`. It currently checks:

- `tips.tips_loaded` (boolean)
- `tips.tips_count` (number)
- `liquids` (volume in wells)

It likely **misses** tracking liquid volume *inside* the tips themselves, or the backend isn't emitting that state change.

**Steps:**

1. **Verify Backend Data:**
    - detailed check of `StateSnapshot` in `praxis/backend/core/models/simulation.models.ts` (and Python equivalent).
    - Does `TipStateSnapshot` include volume information per tip? If not, investigate if PLR provides this and if `ProtocolSimulator` captures it.
    - *Hypothesis:* PLR tracks liquid in tips, but our `TipStateSnapshot` might only track `tips_loaded` boolean.

2. **Update Frontend Diff Logic:**
    - detailed check of `praxis/web-client/src/app/features/execution-monitor/components/state-inspector/state-inspector.component.ts`.
    - Modify `computeStateDiff` to include tip volume changes if available in the snapshot.
    - If tip volume is not available, at least ensure the *destination* well volume increase is clearly highlighted (it should already be covered by the `liquids` loop, so verify why it might be missed—maybe the resource name key is mismatched?).

### Part B: Parameter Display

**Design:**
Create a polished display for `input_parameters_json`.

**Frontend Components:**

1. **Create `ParameterViewerComponent`:**
    - Path: `src/app/features/execution-monitor/components/parameter-viewer/`
    - Logic: Recursive rendering for nested objects, clean key-value formatting, handling of units if present.
    - Style: Use Angular Material (e.g., `mat-list` or styled divs), distinct colors for keys/values.

2. **Update `RunDetailComponent`:**
    - Path: `src/app/features/execution-monitor/components/run-detail.component.ts`
    - Replace the `<pre>` block with `<app-parameter-viewer [parameters]="run()!.input_parameters_json" />`.

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/execution-monitor/components/state-inspector/state-inspector.component.ts` | Logic for computing state diffs. |
| `praxis/web-client/src/app/features/execution-monitor/components/run-detail.component.ts` | Parent component for run details (parameter display). |
| `praxis/web-client/src/app/features/execution-monitor/components/parameter-viewer/parameter-viewer.component.ts` | **NEW** Component for formatting parameters. |
| `praxis/backend/core/simulation.py` | (If needed) Backend simulation logic to ensure tip state is captured. |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/models/simulation.models.ts` | Frontend data models. |
| `praxis/backend/services/simulation_service.py` | Service handling simulation execution. |

---

## 4. Constraints & Conventions

- **State Management:** Use Signals.
- **Styling:** Use design tokens from `styles/themes/`, Angular Material.
- **No external libs:** Do not add `ngx-json-viewer` or similar; build a lightweight viewer.
- **Type Safety:** Ensure strict typing for parameter objects.

---

## 5. Verification Plan

**Definition of Done:**

1. **State Inspection:**
    - Open a finished run with a dispense operation.
    - Go to the State Inspector tab.
    - Verify that navigating to the dispense operation shows a diff:
        - "Volume in Well X: 0 -> 50µL" (Increase)
        - (Optional but desired) "Volume in Tip: 50 -> 0µL" (Decrease)
2. **Parameter Display:**
    - Open a run with complex input parameters.
    - Verify parameters are shown in a clean, readable list/grid, not raw JSON.
    - Verify nested objects are handled gracefully.

**Manual Verification:**

1. Run `npm run start:browser` in `praxis/web-client`.
2. Navigate to `/app/monitor`.
3. Click on a "Completed" run (if none, run a simulation first).
4. Check the "Overview" tab for Parameters.
5. Check the "State Inspector" tab for Diff accuracy.
