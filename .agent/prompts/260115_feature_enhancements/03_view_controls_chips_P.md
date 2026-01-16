# Agent Prompt: View Controls Filter Chips - Planning

**Status:** ⚪ Queued
**Priority:** P2
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Medium
**Dependencies:** `03_view_controls_chips_I.md`, `references/view_controls_audit.md`
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Plan the refactor of view controls to remove redundant chips below dropdown and consolidate into a unified filter chip bar.

**Context**: Inspection phase documented the current component structure and chip rendering logic.

**Goal**: Design the new UX:

1. **Remove Dropdown Chips**: Eliminate chips rendered directly below dropdown.
2. **Unified Filter Chip Bar**: All active filters shown in a single horizontal bar.
3. **Single Chip Per Filter**: One chip per active filter (not grouped by category).
4. **Icon + Tooltip**: Each chip has a category icon; tooltip shows full filter name on hover.
5. **Optional Group Wrapper**: Consider a subtle visual grouping if multiple filters of same type.
6. **Preserve Gradient**: Keep existing gradient/visual styling.

## 2. Technical Implementation Strategy

**Design Decisions**:

1. **Chip Component**: Reuse or create `FilterChipComponent` with icon slot.
2. **Icon Mapping**: Map filter types to icons (machine icon, resource icon, etc.).
3. **Tooltip Implementation**: Use Angular Material tooltip or custom.
4. **Chip Bar Placement**: Likely below controls, above content.
5. **Remove Logic**: Identify template sections to remove.

**Output Generation**:

- Document design decisions in task plan.
- Create mockup description or reference existing design.

## 3. Context & References

**Relevant Skills**:

- `frontend-design` (Angular Material, component design)

**Primary Files to Plan Changes**:

| Path | Planned Change |
| :--- | :--- |
| `praxis/web-client/src/app/shared/components/view-controls/` | Remove inline chips |
| `praxis/web-client/src/app/shared/components/filter-chip-bar/` | New or refactored component |

## 4. Constraints & Conventions

- **Do Not Execute**: This is a PLANNING task (Type P).
- **UX Spec**: Icon with tooltip on hover (per user clarification).
- **Single Chip**: One chip per filter value, not grouped chips.

## 5. Verification Plan

**Definition of Done**:

1. Component structure is planned.
2. Icon mapping is defined.
3. Template changes are documented.
4. Prompt `03_view_controls_chips_E.md` is ready for execution.

---

## On Completion

- [ ] Document design plan
- [ ] Define icon mapping
- [ ] Mark this prompt complete in batch README
- [ ] Proceed to `03_view_controls_chips_E.md`
