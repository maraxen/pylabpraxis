# Agent Prompt: 34_asset_search_filter_pattern

Examine `.agents/README.md` for development context.

**Status:** ✅ Done
**Batch:** [260109](./README.md)
**Backlog:** [ux_issues_260109.md](../../backlog/ux_issues_260109.md)

---

## Task

Implement a consistent search bar + filter accordion pattern across all Asset Management tabs.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [assets.component.ts](../../../praxis/web-client/src/app/features/assets/assets.component.ts) | Main assets page |
| [machines-accordion.component.ts](../../../praxis/web-client/src/app/features/assets/components/machines-accordion/) | Machines tab |
| [resource-accordion.component.ts](../../../praxis/web-client/src/app/features/assets/components/resource-accordion/) | Resources tab |
| [definitions-list.component.ts](../../../praxis/web-client/src/app/features/assets/components/definitions-list/) | Registry tab |

---

## Current State

Each tab has different filter implementations:
- Overview: Dashboard cards (no filtering)
- Spatial View: Has filters inline
- Machines: Has filter chips but no search
- Resources: Has filter chips but no search
- Registry: Has search but different layout

---

## Required Pattern

All "list" tabs should have:

```html
<div class="tab-header">
  <!-- Search Bar -->
  <mat-form-field appearance="outline" class="search-field">
    <mat-icon matPrefix>search</mat-icon>
    <input matInput placeholder="Search {{ tabName }}..."
           [formControl]="searchControl">
    <button mat-icon-button matSuffix *ngIf="searchControl.value"
            (click)="searchControl.reset()">
      <mat-icon>close</mat-icon>
    </button>
  </mat-form-field>

  <!-- Filter Accordion -->
  <mat-expansion-panel class="filter-panel">
    <mat-expansion-panel-header>
      <mat-panel-title>
        <mat-icon>filter_list</mat-icon>
        Filters
        @if (activeFilterCount() > 0) {
          <span class="filter-badge">{{ activeFilterCount() }}</span>
        }
      </mat-panel-title>
    </mat-expansion-panel-header>

    <div class="filter-content">
      <!-- Tab-specific filter chips/selectors -->
    </div>
  </mat-expansion-panel>
</div>

<div class="tab-content">
  <!-- Filtered results -->
</div>
```

---

## Implementation Steps

### 1. Create Shared FilterHeaderComponent

```typescript
@Component({
  selector: 'app-filter-header',
  standalone: true,
  imports: [MatFormFieldModule, MatInputModule, MatExpansionModule, ...],
  template: `...`
})
export class FilterHeaderComponent {
  searchPlaceholder = input<string>('Search...');
  filterCount = input<number>(0);

  searchControl = new FormControl('');
  filterExpanded = signal(false);

  @Output() searchChange = new EventEmitter<string>();

  constructor() {
    this.searchControl.valueChanges.pipe(
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(value => this.searchChange.emit(value || ''));
  }
}
```

### 2. Update Machines Accordion

```typescript
// machines-accordion.component.ts
<app-filter-header
  searchPlaceholder="Search machines..."
  [filterCount]="activeFilters().length"
  (searchChange)="onSearch($event)">

  <ng-container filterContent>
    <!-- Category chips -->
    <!-- Status chips -->
  </ng-container>
</app-filter-header>
```

### 3. Update Resources Accordion

Same pattern as machines.

### 4. Update Registry/Definitions List

Same pattern as machines.

### 5. Styling

```scss
.tab-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--mat-sys-surface);
  padding: 16px;
  border-bottom: 1px solid var(--mat-sys-outline-variant);
}

.search-field {
  width: 100%;
  max-width: 400px;
}

.filter-panel {
  margin-top: 12px;
}

.filter-badge {
  background: var(--mat-sys-primary);
  color: var(--mat-sys-on-primary);
  border-radius: 12px;
  padding: 2px 8px;
  font-size: 12px;
  margin-left: 8px;
}
```

---

## Affected Tabs

| Tab | Search | Filters |
|-----|--------|---------|
| Overview | Skip (dashboard) | Skip |
| Spatial View | Add | Keep existing |
| Machines | Add | Wrap in accordion |
| Resources | Add | Wrap in accordion |
| Registry | Keep | Wrap in accordion |

---

## Testing

1. Search filters results in real-time (debounced)
2. Clear button resets search
3. Filter accordion expands/collapses
4. Filter badge shows active filter count
5. Pattern consistent across all tabs

---

## On Completion

- [ ] FilterHeaderComponent created
- [ ] Machines tab updated
- [ ] Resources tab updated
- [ ] Registry tab updated
- [ ] Consistent styling applied
- [ ] Update backlog status
- [ ] Mark this prompt complete in batch README

---

## References

- [ux_issues_260109.md](../../backlog/ux_issues_260109.md) - Section 2.2
- [ui_consistency.md](../../backlog/ui_consistency.md) - UI patterns
