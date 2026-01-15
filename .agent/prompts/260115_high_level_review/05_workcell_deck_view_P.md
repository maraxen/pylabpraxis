# Agent Prompt: Workcell Deck View Implementation (Plan)


**Status:** ✅ Completed
**Priority:** P1
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** [05_workcell_interface_I](./05_workcell_interface_I.md)
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Enable the "Deck View" for simulated machines in the Workcell Interface.
**Problem**: Simulated machines lack the `plr_definition` property required by `MachineFocusViewComponent`, resulting in a blank deck view.
**Goal**: Implement logic to synthesize `plr_definition` from `DeckCatalogService` specs on the frontend.

## 2. Technical Implementation Strategy

**Planning Phase**:

1. **DeckCatalogService Enhancement**:
    - Add `createPlrResourceFromSpec(spec: DeckDefinitionSpec): PlrResource`.
    - This method must map `rails` and `slots` to `PlrResource` children with correct coordinates.

2. **WorkcellViewService Update**:
    - Inject `DeckCatalogService`.
    - In `mapToMachineWithRuntime`:
      - If `machine.plr_definition` is missing:
        - Determine deck type via `deckCatalog.getDeckTypeForMachine(machine)`.
        - Get spec via `deckCatalog.getDeckDefinition(type)`.
        - Convert to `PlrResource` using the new method.
        - Assign to `machine.plr_definition`.

**Verification Strategy**:

- **Unit Tests**:
  - Test `createPlrResourceFromSpec` generates valid PlrResource tree.
  - Test `WorkcellViewService` populates `plr_definition` for simulated machine mock.
- **Manual Verification**:
  - Open Workcell Dashboard.
  - Select a Simulated Machine (e.g., "Simulated Star").
  - Verify Deck View renders with rails/slots.

## 3. Context & References

**Relevant Skills**:

- `senior-fullstack`
- `frontend-design`

**Primary Files**:

- `praxis/web-client/src/app/features/run-protocol/services/deck-catalog.service.ts`
- `praxis/web-client/src/app/features/workcell/services/workcell-view.service.ts`

## 4. Constraints & Conventions

- **Do Not Implement Yet**: PLANNING only (Type P).
- **Output**: `implementation_plan.md`.

## 5. Verification Plan

**Definition of Done**:

1. `implementation_plan.md` created.
2. Plan approved by User.

---

## On Completion

- [x] Create `05_workcell_deck_view_E.md` (Type E)
- [ ] Mark this prompt complete in batch README (Waiting for 01 Machine Sim completion before finalizing)
