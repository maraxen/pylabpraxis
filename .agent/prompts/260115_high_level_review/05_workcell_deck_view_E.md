# Agent Prompt: Workcell Deck View Implementation (Execution)


**Status:** 🟡 Not Started
**Priority:** P1
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** [05_workcell_deck_view_P](./05_workcell_deck_view_P.md), [01_machine_sim_E](./01_machine_simulation_architecture_E.md)
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Implement the approved plan to enable the "Deck View" for simulated machines by synthesizing `plr_definition` on the frontend.

**Problem Summary**:

1. Simulated machines lack `plr_definition` in backend asset data.
2. `MachineFocusViewComponent` shows an empty state ("No deck definition available").
3. `DeckCatalogService` has specs but no conversion to `PlrResource` structure.

**Goal**: Implement `DeckCatalogService.createPlrResourceFromSpec` and update `WorkcellViewService` to inject this data for simulated machines.

## 2. Technical Implementation Strategy

**Execution Phase**:

1. **DeckCatalogService**:
    - Implement `createPlrResourceFromSpec(spec: DeckDefinitionSpec): PlrResource`.
    - Map `railPositions` to `children` (for Hamilton STAR) or `slots` to `children` (for OT-2).
    - Ensure dimensions and locations match PLR coordinate system.

2. **WorkcellViewService**:
    - Inject `DeckCatalogService`.
    - Update `mapToMachineWithRuntime`:
        - If `machine.plr_definition` is missing:
            - Get spec via `deckCatalog.getDeckTypeForMachine` -> `getDeckDefinition`.
            - Generate resource via `createPlrResourceFromSpec`.
            - Assign to `machine.plr_definition`.

**Verification Strategy**:

- **Automated**: Run `deck-catalog.service.spec.ts` (add new tests for `createPlrResourceFromSpec`).
- **Manual/Browser**:
  - Launch Workcell Dashboard.
  - Select "Simulated Star" or "Simulated OT-2".
  - **Verify Deck View renders rails/slots.**

## 3. Context & References

**Relevant Skills**:

- `senior-fullstack`
- `frontend-design`

**Primary Files**:

- `praxis/web-client/src/app/features/run-protocol/services/deck-catalog.service.ts`
- `praxis/web-client/src/app/features/workcell/services/workcell-view.service.ts`
- `praxis/web-client/src/app/features/workcell/machine-focus-view/machine-focus-view.component.ts`

## 4. Constraints & Conventions

- **Implementation**: Follow `implementation_plan.md` from the Planning phase.
- **Output**: Code changes and `walkthrough.md`.

## 5. Verification Plan

**Definition of Done**:

1. Deck View visible for simulated machines.
2. `deck-catalog.service.spec.ts` passes with new coverage.
3. `walkthrough.md` created.

---

## On Completion

- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed
