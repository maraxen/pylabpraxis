# Agent Prompt: DataViz ViewControls Adoption

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** I-03  
**Input Artifact:** `audit_notes_260114.md` (Section C)

---

## 1. The Task

Replace custom controls in `DataVisualizationComponent` with `ViewControlsComponent`.

## 2. Implementation Steps

### Step 1: Implement ViewControls

- Replace custom toolbar.
- Config:
  - Filters: Measurement Type, Plate ID.
  - GroupBy: Experiment?

## 3. Constraints

- **Complexity**: If DataViz has very specific controls (e.g. date range picker) that `ViewControls` doesn't support, keep them separate or extend `ViewControls`. Use judgement.

## 4. Verification Plan

- [x] Controls render correctly.
- [x] Data updates based on filter changes.

---

## On Completion

- [x] Update this prompt status to 🟢 Completed.
