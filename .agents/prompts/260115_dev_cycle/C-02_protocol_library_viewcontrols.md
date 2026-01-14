# Agent Prompt: Protocol Library ViewControls Adoption

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** I-03  
**Input Artifact:** `audit_notes_260114.md` (Section C)

---

## 1. The Task

Replace the custom search/filter implementation in `ProtocolLibraryComponent` with the shared `ViewControlsComponent`.

## 2. Implementation Steps

### Step 1: Remove Old Controls

- Remove `mat-form-field` search inputs and custom filter dropdowns from `protocol-library.component.html`.

### Step 2: Implement ViewControls

- Add `<app-view-controls [config]="viewConfig" (stateChange)="onStateChange($event)"></app-view-controls>`.
- Define `viewConfig` in TS:
  - Filters: Status, Tag?
  - Sort: Name, Date.
  - ViewTypes: Card, List.
- Connect `onStateChange` to the `ProtocolService` query params or local filtering logic.

## 3. Constraints

- **Consistency**: Must behave exactly like `DefinitionsListComponent`.

## 4. Verification Plan

- [x] Page renders with generic ViewControls.
- [x] Filtering works.
- [x] Sorting works.
- [x] View switching works.

---

## On Completion

- [x] Update this prompt status to 🟢 Completed.
