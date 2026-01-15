# Agent Prompt: QA Scope Inspection


**Status:** 🟢 Completed
**Priority:** P3
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Easy
**Dependencies:** None
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Inspect the codebase to build a complete inventory of features for the QA Checklist.
**Goal**: "Introspect" to ensure we cover *everything* in the manual checklist.
**Scope**: All user-facing features (UI, API interactions, Visual states).

## 2. Technical Implementation Strategy

**Planning Phase**:

- Breakdown features into verification steps.
- Categories:
  - **Setup**: Asset/Machine registration.
  - **Configuration**: Protocol Parameters, Deck Setup.
  - **Execution**: Run start, Monitoring, Pause/Resume.
  - **Analysis**: Results viewing, Logs.

**Output Generation**:

- Create `references/qa_interaction_checklist.md` (or `MANUAL_QA_CHECKLIST.md` in root? No, keep in refs for now).
- Format: Checkbox list with "Expected Result" for each action.

## 3. Context & References

**Relevant Skills**:

- `pylabpraxis-planning` (Understanding user value)
- `qa-best-practices` (if available, else general knowledge)

## 4. Constraints & Conventions

- **Do Not Implement**: PLANNING / ARTIFACT CREATION (Type P).
- **Output**: `references/qa_interaction_checklist.md`.

## 5. Verification Plan

**Definition of Done**:

1. `references/qa_interaction_checklist.md` created.
2. Checklist covers >= 90% of visible features.

---

## On Completion

- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed
- [ ] (Optional) Promote checklist to project root if approved.
