# Agent Prompt: Execution Monitor ViewControls Adoption

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** I-03  
**Input Artifact:** `audit_notes_260114.md` (Section C)

---

## 1. The Task

Replace custom filters in `ExecutionMonitorComponent` (or `RunHistoryComponent`?) with `ViewControlsComponent`.

## 2. Implementation Steps

### Step 1: Identify Component

- Locate the page showing the list of Runs.

### Step 2: Implement ViewControls

- Replace top bar with `app-view-controls`.
- Config filters: Status (Running, Completed, Error), Machine.
- Config sort: Start Time, Duration.

## 3. Constraints

- **UX**: Ensure "Live" runs are easily accessible.

## 4. Verification Plan

- [ ] Filtering by Status works.
- [ ] Sorting by Date works.

---

## On Completion

- [ ] Update this prompt status to 🟢 Completed.
