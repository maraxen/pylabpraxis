# Agent Prompt: View Controls Filter Chips - Inspection

**Status:** 🔵 Ready
**Priority:** P2
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Medium
**Dependencies:** None
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Inspect the current view controls component to understand the dropdown and chip rendering logic, preparing for a UX refactor.

**Problem**: The current implementation has:
- Dropdown with chips rendered below it (redundant visual clutter)
- Grouped chips per filter category
- Chips lack clear visual distinction between filter types

**Goal**: Document:

1. **Current Component Structure**: How `view-controls` component renders dropdowns and chips.
2. **Chip Rendering Logic**: Where chips are generated, how they're grouped.
3. **Gradient Styling**: Identify any gradient/visual effects to preserve.
4. **Filter State Management**: How filter selections are tracked and applied.

## 2. Technical Implementation Strategy

**Inspection Phase**:

1. **Component Analysis**: Read `praxis/web-client/src/app/shared/components/view-controls/` (or equivalent location).
2. **Template Review**: Examine the HTML template for dropdown and chip sections.
3. **Styling Audit**: Check SCSS/CSS for gradient effects and chip styles.
4. **State Flow**: Trace how filter selections flow to parent components.

**Output Generation**:

- Create `references/view_controls_audit.md` with:
  - Component structure diagram
  - Current chip rendering logic
  - Styles to preserve (gradients, colors)
  - Proposed chip bar location

## 3. Context & References

**Relevant Skills**:

- `frontend-design` (Angular component patterns)

**Primary Files to Inspect**:

| Path | Description |
| :--- | :--- |
| `praxis/web-client/src/app/shared/components/view-controls/` | View controls component |
| `praxis/web-client/src/app/shared/components/filter-chips/` | Filter chips component (if exists) |
| Related feature components using view-controls | Usage context |

## 4. Constraints & Conventions

- **Do Not Implement**: This is an INSPECTION task (Type I).
- **Scope**: View controls and filter chip rendering.
- **Note**: Identify all places using these components.

## 5. Verification Plan

**Definition of Done**:

1. `references/view_controls_audit.md` documents current implementation.
2. Gradient/styling to preserve is identified.
3. Chip rendering logic location is documented.
4. Prompt `03_view_controls_chips_P.md` is ready to proceed.

---

## On Completion

- [ ] Create `references/view_controls_audit.md`
- [ ] Mark this prompt complete in batch README
- [ ] Proceed to `03_view_controls_chips_P.md`
