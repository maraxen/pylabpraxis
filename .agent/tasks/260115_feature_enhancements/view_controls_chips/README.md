# Task: View Controls Filter Chips Refactor

**ID**: FE-03
**Status**: ⚪ Not Started
**Priority**: P2
**Difficulty**: Medium

---

## 📋 Phase 1: Inspection (I)

**Objective**: Inspect current view controls component to understand dropdown and chip rendering.

- [ ] Read `praxis/web-client/src/app/shared/components/view-controls/` component
- [ ] Examine HTML template for dropdown and chip sections
- [ ] Check SCSS/CSS for gradient effects and chip styles
- [ ] Trace filter state management flow

**Findings**:
> - Component structure diagram
> - Current chip rendering logic location
> - Styles to preserve (gradients, colors)

---

## 📐 Phase 2: Planning (P)

**Objective**: Design unified filter chip bar with icons and tooltips.

- [ ] Plan chip component structure
- [ ] Define icon mapping for filter types
- [ ] Design tooltip implementation
- [ ] Identify template sections to remove

**Implementation Plan**:

1. Remove chips rendered directly below dropdown
2. Create/update `FilterChipBar` component
3. Each chip: icon prefix + short value + close button
4. Tooltip on hover shows full filter name
5. Preserve gradient styling from current implementation

**Icon Mapping**:
```typescript
const FILTER_ICONS = {
  'machine': 'precision_manufacturing',
  'resource': 'inventory_2',
  'status': 'flag',
  'type': 'category',
};
```

**Definition of Done**:

1. Dropdown no longer shows chips below it
2. Filter chip bar displays all active filters with icons
3. Hovering shows tooltip with full filter name
4. Gradient styling preserved
5. Removing chip clears the filter

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement unified filter chip bar.

- [ ] Modify view controls template - remove inline chip `@for` loop
- [ ] Create/update filter chip bar component:
  ```typescript
  @Component({
    selector: 'app-filter-chip-bar',
    template: `
      <div class="filter-chip-bar">
        @for (filter of activeFilters; track filter.id) {
          <div class="filter-chip" [matTooltip]="filter.label">
            <mat-icon>{{ getIcon(filter.type) }}</mat-icon>
            <span>{{ filter.shortValue }}</span>
            <button mat-icon-button (click)="remove(filter)">
              <mat-icon>close</mat-icon>
            </button>
          </div>
        }
      </div>
    `
  })
  ```
- [ ] Implement icon mapping service/method
- [ ] Apply gradient background and styling
- [ ] Wire up filter removal

**Work Log**:

- [Pending]

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify filter chip bar UX.

- [ ] Apply multiple filters of different types
- [ ] Verify single chip per filter in chip bar
- [ ] Hover to see tooltips
- [ ] Click X to remove filters
- [ ] Verify responsive behavior on narrow screens

**Results**:
> [To be captured]

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **UX Spec**: Icon with tooltip on hover (user clarification)
- **Files**:
  - `praxis/web-client/src/app/shared/components/view-controls/`
  - `praxis/web-client/src/app/shared/components/filter-chip-bar/` (new or refactored)
