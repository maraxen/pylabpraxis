# Agent Prompt: State Inspection Enhancement Planning


**Status:** ✅ Completed
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Complex
**Dependencies:** `04_state_inspection_gap_analysis_I.md`
**Backlog Reference:** `references/state_gap_analysis.md`

---

## 1. The Task

**Objective**: Plan the implementation of real-time state inspection based on the gap analysis.
**Problem**: Users cannot see live liquid levels or tip status during execution because the backend doesn't emit this state and the frontend monitor doesn't visualize it.
**Goal**: Create an implementation plan to bridge the gap between `WorkcellRuntime` state and `ExecutionMonitor` visualization.

## 2. Technical Implementation Strategy

Refine the recommendations from `references/state_gap_analysis.md` into a concrete plan:

1. **Backend Real-Time Emission**:
    - Design a `StateEmissionService` or hook into `WorkcellRuntime.StateSyncMixin`.
    - Broadcast `well_state_update` via `ws_manager` / `websockets.py`.
    - Ensure performance (don't flood the socket, use diffs/compression).

2. **Frontend Visualization**:
    - Integrate `<app-deck-view>` into `RunDetailComponent`.
    - Map `ExecutionService` signals (`currentRun().wellState`) to `DeckView` inputs.
    - Add a "Live View" tab to the Run Detail page.

## 3. Context & References

**Relevant Skills**:

- `senior-fullstack`
- `backend-dev-guidelines`
- `frontend-design`

**Reference Documents**:

- `.agent/references/state_gap_analysis.md` (The Gap Analysis)

## 4. Constraints & Conventions

- **Do Not Implement**: PLANNING only (Type P).
- **Output**: `implementation_plan.md` for the enhancement.

## 5. Verification Plan

**Definition of Done**:

1. `implementation_plan.md` created and approved.
2. `04_state_inspection_enhancement_E.md` (Type E) queued.

---

## On Completion

- [ ] Create `04_state_inspection_enhancement_E.md`
- [ ] Mark this prompt complete in batch README
