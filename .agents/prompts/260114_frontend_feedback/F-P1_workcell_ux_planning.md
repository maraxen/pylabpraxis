# F-P1: Workcell UX Planning

**Status:** ✅ COMPLETED
**Priority:** High (Blocker for F-01)
**Assignee:** Agent
**Completed:** 2026-01-13

## 📦 Artifacts Generated

1. **Design Document:** [`artifacts/workcell_ux_redesign.md`](./artifacts/workcell_ux_redesign.md)
   - Problem Statement & Current State Analysis
   - Proposed Solution with Hierarchical Navigation
   - UI Mockups (ASCII wireframes)
   - Data Requirements & Component Architecture
   - User Flows & Design System Compliance

2. **Implementation Plan:** [`artifacts/workcell_implementation_plan.md`](./artifacts/workcell_implementation_plan.md)
   - 4-Phase breakdown (11 discrete tasks)
   - Prompt generation checklist
   - Gantt chart timeline
   - Success metrics & risk mitigation

---
**Type:** 🔵 Planning (UX/UI Design)

## Context

The current "Workcell" view in the Web Client is a basic list of machines (using `VisualizerComponent` and `VisualizerService`) that allows toggling visibility of deck views. The user feedback indicates this needs a significant overhaul: "also the workcell column and just generally the workcell menu needs a lot of improvement. this will be a task of first planning out what the best UX here would be and going from there."

This task is PURELY PLANNING and UX DESIGN. No code implementation is expected yet. The output will be a design document detailed enough to generate subsequent implementation prompts.

## Objectives

1. **Audit Current UX:** Analyze `VisualizerComponent` (`features/visualizer/visualizer.component.ts`) and its usage of `DeckViewComponent`. Identify simple list-based navigation limitations vs. desired rich machine status and hierarchy.
2. **Design "Workcell" Experience:**
    - **Navigation:** Move away from a simple sidebar list. Consider a card-based inventory, a visual lab layout, or a hierarchical tree view (Workcell -> Machine -> Deck).
    - **Information Display:** What needs to be seen at a glance? (Status, Active Protocol, Next Intervention, Errors).
    - **Interaction:** How does a user Select a machine > Inspect its Deck > Interact with Resources?
3. **Simulation Integration Planning:**
    - Define how `Machine.plr_state` (JSONB) should map to visual states (liquid levels, tip presence).
    - Define how "simulated deck states" (F-01) will be visualized.
4. **Produce Design Artifacts:**
    - **User Flows:** Diagram how a user navigates to a machine and checks its running state.
    - **Wireframes/Mockups:** ASCII or Mermaid mockups of the new Layout (Sidebar, Dashboard, Details).
    - **Component Architecture:** Propose new components (e.g., `WorkcellDashboard`, `MachineCard`, `DeckStateReflector`).

## Constraints & Requirements

- **Backend Alignment:** Must use existing `Machine` and `Workcell` models in `praxis/backend/models/domain`.
- **Deck Visualization:** Must leverage (and potentially extend) the existing robust `DeckViewComponent` (`shared/components/deck-view/`).
- **Aesthetics:** Must follow the "Premium Design" guidelines (Rich Aesthetics, Dynamic Design).
- **Responsive:** The design must handle multiple machines (1-10+) gracefully.

## Expected Output

1. **`design/workcell_ux_redesign.md`**: A comprehensive design document.
    - **Problem Statement**: What is wrong with the current `visualizer.component.ts`.
    - **Proposed Solution**: New navigation structure and layout.
    - **UI Mockups**: Wireframes for the Dashboard and Machine Details view.
    - **Data Requirements**: What new fields (if any) are needed from the backend (though `plr_state` should cover most).
2. **`implementation_plan.md`**: A high-level breakdown of the implementation phases (to be used for generating F-02, F-03, etc.).
3. **Updates to `task.md`** reflecting the breakdown.

## Validation

- **Design Review:** The user must explicitly approve the `workcell_ux_redesign.md` before any code is written (F-01 implementation depends on this).

---

## Relevant Files in Context

- `praxis/web-client/src/app/features/visualizer/visualizer.component.ts` (Current "Workcell" view)
- `praxis/web-client/src/app/shared/components/deck-view/deck-view.component.ts` (Core visualization component)
- `praxis/backend/models/domain/machine.py` (Backend data model)
- `praxis/backend/models/domain/asset.py` (Contains `plr_state`)
