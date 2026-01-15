# Agent Prompt: State Inspection Gap Analysis


**Status:** ✅ Completed
**Priority:** P3
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** None
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Perform a gap analysis of "State Inspection" and "Simulation Reporting" against user expectations.
**Problem**: User states "STATE INSPECTION and simulation reporting still lacks what i have specified".
**Goal**: Identify specifically *what* is missing from the `ExecutionMonitor` and `SimulationReport`.

## 2. Technical Implementation Strategy

**Inspection Phase**:

1. Review `ExecutionMonitorComponent` (frontend) -> What data is visualized?
2. Review `ExecutionService` (frontend) -> What data is received via WebSocket?
3. Review `WorkcellRuntime` (backend) -> What state is emitted? (Tip presence, liquid volumes, etc.)

**Output Generation**:

- Create `references/state_gap_analysis.md` comparing:
  - Available Data (from backend/websocket).
  - Visualized Data (in frontend components).
  - Missing Critical Data (e.g. Tip Status, Liquid Level).

## 3. Context & References

**Relevant Skills**:

- `senior-fullstack` (Full stack state tracing)

**Primary Files to Inspect**:

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/execution-monitor/` | Monitor UI |
| `praxis/web-client/src/app/shared/components/deck-view/` | Deck Visualizer |

## 4. Constraints & Conventions

- **Do Not Implement**: INSPECTION only (Type I).
- **Output**: `references/state_gap_analysis.md` output.

## 5. Verification Plan

**Definition of Done**:

1. Gap Analysis created in `references/`.
2. Prompt `04_state_inspection_enhancement_P.md` Queued.

---

## On Completion

- [x] Create `04_state_inspection_enhancement_P.md` (Type P)
- [x] Mark this prompt complete in batch README and set status to ✅ Completed
