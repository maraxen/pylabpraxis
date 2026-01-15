# Agent Prompt: State Inspection Enhancement Execution


**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Complex
**Dependencies:** `04_state_inspection_enhancement_P.md`
**Backlog Reference:** `references/state_gap_analysis.md`, `implementation_plan.md` (check artifact URI)

---

## 1. The Task

**Objective**: Implement the State Inspection enhancements defined in the plan.
**Goal**: Enable real-time state inspection in the backend and visualization in the frontend.

## 2. Technical Implementation Steps

Follow the approved `implementation_plan.md`:

1. **Backend Implementation**:
    - Modify `WorkcellRuntime.StateSyncMixin` to support state emission callbacks.
    - Update `ProtocolRunService` to inject the callback and manage state storage.
    - Update `websockets.py` to broadcast real-time state.

2. **Frontend Implementation**:
    - Update `RunDetailComponent` to include `DeckViewComponent`.
    - Connect `DeckView` to `ExecutionService` state for active runs.

## 3. Context & References

**Relevant Skills**:

- `senior-fullstack`
- `backend-dev-guidelines`
- `frontend-design`

**Reference Documents**:

- `.agent/references/state_gap_analysis.md`
- `implementation_plan.md` (Artifact from Planning Phase)

## 4. Constraints & Conventions

- **Mode**: EXECUTION (Type E).
- **Output**: Code changes.

## 5. Verification Plan

- **Manual**: Run a simulated protocol and verify deck updates in the UI.
- **Automated**: Ensure existing tests pass.

---

## On Completion

- [x] Mark this prompt complete in batch README
- [x] Create `walkthrough.md`
