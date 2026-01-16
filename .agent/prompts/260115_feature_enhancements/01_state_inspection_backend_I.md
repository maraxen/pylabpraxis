# Agent Prompt: State Inspection Backend - Inspection

**Status:** 🔵 Ready
**Priority:** P1
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Medium
**Dependencies:** None
**Backlog Reference:** `implementation_plan.md`

---

## 1. The Task

**Objective**: Inspect the current `FunctionCallLog` model and `ExecutionMixin` to understand the gaps preventing post-run "time travel" state inspection for backend-executed protocol runs.

**Problem**: Real-time state updates work via WebSockets during execution, but after a run completes, users cannot replay the deck state at each step because `FunctionCallLog` entries don't persist state snapshots.

**Goal**: Document the current state of:

1. **FunctionCallLog Schema**: What fields exist, what's missing for `state_before_json` / `state_after_json`.
2. **ExecutionMixin Flow**: Where function calls are logged, where `workcell_runtime.get_state_snapshot()` could be captured.
3. **API Gaps**: Whether any endpoint currently returns state history (likely none for backend mode).
4. **Serialization Format**: What `get_state_snapshot()` returns vs what `DeckView` expects.

## 2. Technical Implementation Strategy

**Inspection Phase**:

1. **Schema Review**: Read `praxis/backend/models/domain/protocol.py` → `FunctionCallLog` class.
2. **Execution Flow**: Read `praxis/backend/core/orchestrator/execution.py` → trace where logs are created.
3. **State Snapshot Method**: Read `praxis/backend/core/workcell_runtime/workcell_runtime.py` → `get_state_snapshot()` implementation.
4. **Frontend Expectations**: Read `praxis/web-client/src/app/features/workcell/components/deck-view/` to understand expected data format.

**Output Generation**:

- Create `references/state_inspection_audit.md` with:
  - Current schema analysis
  - Execution flow diagram (text-based)
  - Serialization format comparison (PLR output vs frontend expectations)
  - Gap list with specific line numbers

## 3. Context & References

**Relevant Skills**:

- `backend-dev-guidelines` (SQLModel patterns)

**Primary Files to Inspect**:

| Path | Description |
| :--- | :--- |
| `praxis/backend/models/domain/protocol.py` | FunctionCallLog model |
| `praxis/backend/core/orchestrator/execution.py` | ExecutionMixin with log calls |
| `praxis/backend/core/workcell_runtime/workcell_runtime.py` | State snapshot method |
| `praxis/web-client/src/app/core/services/simulation-results.service.ts` | Frontend state history consumer |

## 4. Constraints & Conventions

- **Do Not Implement**: This is an INSPECTION task (Type I).
- **No Code Changes**: Read and document only.
- **Output**: `references/state_inspection_audit.md` artifact.

## 5. Verification Plan

**Definition of Done**:

1. `references/state_inspection_audit.md` exists with schema analysis and gap documentation.
2. Serialization format differences are identified.
3. Prompt `01_state_inspection_backend_P.md` is ready to proceed.

---

## On Completion

- [ ] Create/update `references/state_inspection_audit.md`
- [ ] Mark this prompt complete in batch README
- [ ] Proceed to `01_state_inspection_backend_P.md`
