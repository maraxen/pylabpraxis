# Chip-Based Filter Standardization Backlog

**Priority**: P2-P3
**Goal**: Unified filter UX across all surfaces using the `FilterChipComponent`.

---

## Active Tasks

### 2. UI Visual Tweaks (from ui_polish.md)

**Priority**: P3
**Status**: ✅ Complete (2026-01-08)
**Tasks**:

- [x] **Registry Spacing**: Fix padding issues in the Asset Registry list view.
- [x] **Machine Tab Alignment**: Correct the vertical alignment of status indicators in the Machines tab.
- [x] **Grid Layout Consistency**: Ensure that resource cards have consistent height even with varying metadata density.
- [x] **Themed Gradients**: Implemented subtle themed gradients and borders across asset cards and list items.

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
- [x] **Unique Name Parsing**: Implemented word-based logic in `name-parser.ts` to extract distinguishing name parts. Integrated with `FilterChipComponent` for full-name tooltips.
