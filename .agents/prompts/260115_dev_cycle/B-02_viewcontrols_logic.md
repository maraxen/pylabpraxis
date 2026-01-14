# Agent Prompt: ViewControls Logic Updates

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Low  
**Dependencies:** I-01  
**Input Artifact:** `viewcontrols_inspection_findings.md`

---

## 1. The Task

Implement logic improvements to ViewControls toggles and chip displays.

**Issues (from Audit Notes B.2, B.3, B.4, B.6):**

- View Type toggle shows text (want Icons only).
- Status Filter missing "Available" option.
- GroupBy shows "None" in dropdown (want Toggle if binary).
- Filter Chips are grouped poorly.

## 2. Implementation Steps

### Step 1: View Type Toggle

- Update `ViewTypeToggleComponent` to hide text labels and show only icons (Card/List/Table).

### Step 2: Binary GroupBy

- If `groupByOptions` has only 2 items (e.g. None + Type), render as a specialized Toggle button instead of a full Dropdown.

### Step 3: Filter Chips

- Update `ActiveFiltersComponent` (or equivalent) to group chips by key.
- Format: `Status: [Available]x [Error]x` instead of `[Status: Available]x [Status: Error]x`.

### Step 4: Status Enumeration

- Ensure "Available" status is correctly mapped in the `status` filter options (check `ProtocolStatus` enum vs string).

## 3. Constraints

- **Component**: `ViewControlsComponent` and children.

## 4. Verification Plan

- [ ] View Toggle is Icon-only.
- [ ] Filter chips are grouped by Category.
- [ ] "Available" appears in Status filter.

---

## On Completion

- [ ] Update this prompt status to 🟢 Completed.
