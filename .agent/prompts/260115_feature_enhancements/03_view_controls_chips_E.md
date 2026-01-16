# Agent Prompt: View Controls Filter Chips - Execution

**Status:** ⚪ Queued
**Priority:** P2
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Medium
**Dependencies:** `03_view_controls_chips_P.md`
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Implement the view controls refactor with unified filter chip bar, icons, and tooltips.

**Context**: Planning phase completed with component design and icon mapping.

**Goal**: Execute the implementation:

1. **Remove Inline Chips**: Delete chip rendering from dropdown section.
2. **Create Filter Chip Bar**: Unified bar component for all active filters.
3. **Icon Integration**: Add category icons to each chip.
4. **Tooltip on Hover**: Show full filter name/value on hover.
5. **Preserve Styling**: Maintain gradient and visual polish.

## 2. Technical Implementation Strategy

**Execution Steps**:

1. **Modify View Controls Template**:
   - Remove `@for` loop rendering chips below dropdown.
   - Add `<app-filter-chip-bar>` component reference.

2. **Create/Update Filter Chip Bar**:
   ```typescript
   @Component({
     selector: 'app-filter-chip-bar',
     template: `
       <div class="filter-chip-bar">
         @for (filter of activeFilters; track filter.id) {
           <div class="filter-chip" [matTooltip]="filter.label">
             <mat-icon>{{ filter.icon }}</mat-icon>
             <span class="chip-value">{{ filter.shortValue }}</span>
             <button mat-icon-button (click)="removeFilter(filter)">
               <mat-icon>close</mat-icon>
             </button>
           </div>
         }
       </div>
     `
   })
   ```

3. **Icon Mapping Service**:
   ```typescript
   getFilterIcon(type: FilterType): string {
     const iconMap = {
       'machine': 'precision_manufacturing',
       'resource': 'inventory_2',
       'status': 'flag',
       // ...
     };
     return iconMap[type] || 'filter_list';
   }
   ```

4. **Styling**: Apply gradient background, spacing, hover effects.

## 3. Context & References

**Relevant Skills**:

- `frontend-design` (Angular Material, SCSS)

**Primary Files to Modify**:

| Path | Change |
| :--- | :--- |
| `praxis/web-client/src/app/shared/components/view-controls/` | Remove inline chips |
| `praxis/web-client/src/app/shared/components/filter-chip-bar/` | Create/update component |
| Related SCSS files | Gradient and chip styling |

## 4. Constraints & Conventions

- **Execute Changes**: This is an EXECUTION task (Type E).
- **Accessibility**: Ensure tooltips are accessible.
- **Responsive**: Chip bar should wrap gracefully on narrow screens.

## 5. Verification Plan

**Definition of Done**:

1. Dropdown no longer shows chips below it.
2. Filter chip bar displays all active filters with icons.
3. Hovering shows tooltip with full filter name.
4. Gradient styling preserved.
5. Removing chip clears the filter.

**Manual Test**:
1. Apply multiple filters of different types.
2. Verify single chip per filter in chip bar.
3. Hover to see tooltips.
4. Click X to remove filters.

---

## On Completion

- [ ] Implementation committed
- [ ] Visual verification passed
- [ ] Mark this prompt complete in batch README
