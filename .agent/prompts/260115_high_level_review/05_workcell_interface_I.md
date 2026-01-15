# Agent Prompt: Workcell & Deck View Inspection


**Status:** ✅ Completed
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** [01_machine_sim_I](./01_machine_simulation_architecture_I.md) (Logic overlap, but UI is separate)
**Note:** Awaiting completion of [01 Machine Simulation Architecture](./01_machine_simulation_architecture_I.md). Planning and Execution prompts have been generated but may need to be regenerated after the new inspection is complete.
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Inspect the Workcell Interface and specifically the integration of the "Deck View" for simulated machines.
**Problem**: User reports "the workcell interface, and lack of deck view even for simulated machines". The Deck View should be visible and functional for inspection.
**Goal**: Identify why the Deck View is missing or disconnected in the Workcell UI.

## 2. Technical Implementation Strategy

**Inspection Phase**:

1. Review `praxis/web-client/src/app/features/workcell/` components.
2. Check how `WorkcellComponent` decides to show/hide the `DeckViewComponent`.
3. Investigate if "Simulated" machines are missing necessary properties (like `deck_setup`) to trigger the view.

**Output Generation**:

- Create `references/workcell_ui_audit.md` detailing:
  - Component hierarchy for Workcell View.
  - Logic conditions preventing Deck View rendering.
  - Proposed UI structure for "Deck View" within the Workcell Dashboard.

## 3. Context & References

**Relevant Skills**:

- `senior-fullstack` (Angular Component Composition)
- `frontend-design` (UI Layout inspection)

**Primary Files to Inspect**:

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/workcell/` | Workcell Feature |
| `praxis/web-client/src/app/shared/components/deck-view/` | Deck View Component |

## 4. Constraints & Conventions

- **Do Not Implement**: INSPECTION only (Type I).
- **Output**: `references/workcell_ui_audit.md`.

## 5. Verification Plan

**Definition of Done**:

1. `references/workcell_ui_audit.md` created.
2. Prompt `05_workcell_deck_view_P.md` Queued.

---

## On Completion

- [x] Create `05_workcell_deck_view_P.md` (Type P)
- [x] Mark this prompt complete in batch README and set status to ✅ Completed
