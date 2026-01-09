# Angular ARIA Migration

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-08 (new backlog from technical debt)
**Status**: 🟡 In Progress (Phase 1 & 3 complete)

---

## Goal

Replace custom chip, dropdown, and grid components with standardized Angular ARIA primitives (`@angular/aria`) for improved accessibility, consistent UX, and reduced maintenance.

---

## Background

The Angular ARIA package (`@angular/aria`) provides headless, accessible UI primitives:

- `@angular/aria/combobox` - Combobox with popup (multiselect dropdowns)
- `@angular/aria/listbox` - Listbox with options (multiselect values)
- `@angular/aria/grid` - Accessible grid pattern (well selector, plate view)

These replace custom implementations with browser-native accessibility patterns.

---

## Phase 1: Multiselect Components

Replace custom filter chips and dropdowns with ARIA Combobox + Listbox:

- [x] **Machine Asset Management**: Category/Status multiselect chips
- [x] **Backend Filters**: Sort/filter dropdowns
- [x] **Spatial View**: Category dropdowns
- [x] Create shared `AriaMultiselectComponent` wrapper
- [x] Create shared `AriaSelectComponent` wrapper

Files affected:

- `src/app/features/assets/` - Filter chips
- `src/app/shared/components/filter-chip/` - Base component
- `src/app/features/spatial/` - Spatial view filters

## Phase 2: Well Selector Grid

Replace current well selector with ARIA Grid:

- [ ] Implement `@angular/aria/grid` for microplate well selector
- [ ] Support individual clicking
- [ ] Support click-and-drag selection
- [ ] Add "Clear Selection" and "Invert Selection" buttons
- [ ] Implement selection animation rendering

Files affected:

- `src/app/shared/components/well-selector/`
- `src/app/features/run-protocol/components/`

## Phase 3: Theme Integration

- [x] Style ARIA components with Material Design 3 tokens
- [x] Ensure dark/light mode compatibility
- [x] Match existing design system gradients and borders

---

## Technical Notes

### Installation

```bash
npm install @angular/aria
```

### Example: Multiselect Combobox

```typescript
import {Combobox, ComboboxInput, ComboboxPopup, ComboboxPopupContainer} from '@angular/aria/combobox';
import {Listbox, Option} from '@angular/aria/listbox';
```

### Example: Grid

```typescript
import {Grid, GridRow, GridCell, GridCellWidget} from '@angular/aria/grid';
```

---

## References

- [Angular ARIA Documentation](https://material.angular.dev/) (when available)
- [ui_consistency.md](./ui_consistency.md) - Related UI polish
- [chip_filter_standardization.md](./chip_filter_standardization.md) - Current filter implementation
