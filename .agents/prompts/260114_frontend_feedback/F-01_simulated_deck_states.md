# F-01: Simulated Deck States Implementation

**Status:** 🟢 Ready for Implementation
**Priority:** High
**Assignee:** Agent
**Type:** 🟢 Implementation (Frontend)
**Unblocked By:** F-P1 (Workcell UX Planning) - Completed 2026-01-13

## Design Reference

> [!NOTE]
> F-P1 is now complete. See the design documents for context:
>
> - **Design:** [`artifacts/workcell_ux_redesign.md`](./artifacts/workcell_ux_redesign.md)
> - **Implementation Plan:** [`artifacts/workcell_implementation_plan.md`](./artifacts/workcell_implementation_plan.md)
>
> This task (F-01) corresponds to **Phase 3: Deck State Integration** in the implementation plan.

## Objectives

1. **Connect Simulation State:**
    - Ensure `AssetService` or a new `SimulationStateService` polls or subscribes to `Machine.plr_state` updates.
    - Map the `plr_state` JSON to the `PlrDeckData` interface expected by `DeckViewComponent`.
2. **Enhance `DeckViewComponent`:**
    - Ensure it correctly interprets "Simulated" state vs "Static" definition.
    - Visualize `volume` (liquid levels) and `has_tip` (tip presence) dynamically.
    - (If planned in F-P1) Add visual indicators for "Simulating" vs "Connected".
3. **Implement Visualizer Updates:**
    - Replace the "No deck state available" fallback with a proper "Empty Deck" or "Loading State" visualization if valid but empty.
    - Implement the "Deck State Reflector" component proposed in F-P1 (if applicable).

## Implementation Details (Provisional)

- **Service Layer:**
  - Check `praxis/web-client/src/app/features/assets/services/asset.service.ts`.
  - Ensure `getMachines()` includes `plr_state` (mapped from `MachineRead`).
- **Component Layer:**
  - Modify `praxis/web-client/src/app/features/visualizer/visualizer.component.ts` (or its replacement from F-P1).
  - Pass `machine.plr_state` into `<app-deck-view [state]="...">`.

## Verification

1. **Manual Test:**
    - Start the backend simulation.
    - Navigate to Workcell view.
    - Verify that Deck Layout appears.
    - Run a protocol (simulation).
    - **Verify that liquid levels and tips change in the UI** as the protocol runs.
2. **Automated Test (e2e/unit):**
    - Mock a `Machine` with populated `plr_state`.
    - Verify `DeckViewComponent` renders the correct number of tips/liquid volume.

---

## Relevant Files in Context

- `praxis/web-client/src/app/features/visualizer/visualizer.component.ts`
- `praxis/web-client/src/app/shared/components/deck-view/deck-view.component.ts`
- `praxis/backend/models/domain/machine.py`
