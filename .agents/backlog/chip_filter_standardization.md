# Chip-Based Filter Standardization Backlog

**Priority**: P2-P3
**Goal**: Unified filter UX across all surfaces using the `FilterChipComponent`.

---

## Active Tasks

### 1. Unique Name Parsing

**Priority**: P2
**Status**: ⏳ Todo
**Issue**: When many assets have similar names (e.g., "Hamilton Core96 Tip Rack"), the filter chips can cut off the distinguishing parts.
**Action**: Implement logic to extract and display only the unique identifying parts of asset names in the chip labels.

### 2. UI Visual Tweaks (from ui_polish.md)

**Priority**: P3
**Status**: ⏳ Todo
**Tasks**:

- [ ] **Registry Spacing**: Fix padding issues in the Asset Registry list view.
- [ ] **Machine Tab Alignment**: Correct the vertical alignment of status indicators in the Machines tab.
- [ ] **Grid Layout Consistency**: Ensure that resource cards have consistent height even with varying metadata density.

---

## Completed Items ✅

- [x] **Core Filter Chip Component**: Base component with active/inactive/disabled states.
- [x] **Resource Filter Chips**: Integrated Categories, Brands, Status into Resource Inventory.
- [x] **Machine Filter Chips**: Category, Simulated, Status, Backend filters for Machines.
- [x] **Disabled Chip UX**: Shake animation + message on disabled click.
- [x] **Chip Filter Overflow**: Flex-wrap + dropdown collapsing for >5 chips.
- [x] **Search Icon Centering**: Aligned search icons vertically across all inputs (from `ui_polish.md`).
- [x] **Capability Dropdown Theme**: Fixed light-theme-only select panels in dark mode (from `ui_polish.md`).
- [x] **Filter Result Counts**: Integrated dynamic counts and delta counting into filter chips.
- [x] **Merge UI Polish**: Consolidated `ui_polish.md` into this backlog (2026-01-07).
