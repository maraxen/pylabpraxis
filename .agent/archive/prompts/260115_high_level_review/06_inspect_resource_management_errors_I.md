# Agent Prompt: Resource Management Error Inspection


**Status:** 🟢 Completed
**Priority:** P1
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** None
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Inspect the "Resource Management" and "Add Asset/Machine/Resource" flows to identify the root cause of reported failures.
**Problem**: User reports "Add asset, add machine, add resource" functionalities are completely broken.
**Goal**: pinpoint the exact errors (console logs, logic failures, or missing handlers) preventing these actions.

## 2. Technical Implementation Strategy

**Inspection Phase**:

1. Inspect `praxis/web-client/src/app/features/assets/` components (e.g., `AssetManagerComponent`, `AddAssetDialog`).
2. Inspect `praxis/web-client/src/app/features/resources/` (if separate).
3. Check browser console logs (via mental model or manual verification if possible) for common errors like `NullInjectorError` or 500s.

**Output Generation**:

- Create `references/resource_error_log.md` detailing:
  - The specific error messages or behavior differences observed.
  - file/line numbers of suspected culprits (e.g., missing signal updates, broken API calls).
  - Fix recommendations for the subsequent Execution prompt.

## 3. Context & References

**Relevant Skills**:

- `systematic-debugging` (Isolate the break)
- `senior-fullstack` (Angular Forms/Dialogs)

**Primary Files to Inspect**:

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/` | Asset UI |
| `praxis/web-client/src/app/core/services/resource.service.ts` | Resource Logic |

## 4. Constraints & Conventions

- **Do Not Implement**: INSPECTION only (Type I).
- **Output**: `references/resource_error_log.md`.

## 5. Verification Plan

**Definition of Done**:

1. `references/resource_error_log.md` created.
2. Prompt `06_fix_resource_management_E.md` Queued (or P if complex).

---

## On Completion

- [x] Create `06_fix_resource_management_P.md` (Type P)
- [x] Mark this prompt complete in batch README and set status to 🟢 Completed
