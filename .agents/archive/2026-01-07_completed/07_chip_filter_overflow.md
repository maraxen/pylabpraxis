# Prompt 7: Chip Filter Overflow Fix

**Priority**: P2
**Difficulty**: Small
**Type**: Easy Win (CSS Fix)

> **IMPORTANT**: Do NOT use the browser agent. Verify with automated tests only.

---

## Context

When there are many filter chips (e.g., backends in machine filters), they overflow awkwardly instead of wrapping or collapsing into a dropdown.

---

## Tasks

### 1. Add flex-wrap to Filter Containers

Update `machine-filters.component.ts` styles:

```scss
.filters-container {
  display: flex;
  flex-wrap: wrap;  /* ADD THIS */
  align-items: flex-start;
  gap: 16px;
  /* ... rest of styles */
}

.filter-group {
  flex-shrink: 0;
  max-width: 100%;  /* ADD: Prevent overflow */
}

/* ADD: Wrap chip listbox if too many chips */
mat-chip-listbox {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-height: 120px;  /* Limit height */
  overflow-y: auto;   /* Scroll if needed */
}
```

### 2. Implement Chip Collapse for >5 Items

When there are more than 5 options, consider collapsing into a single combo chip:

```typescript
// In component
readonly CHIP_COLLAPSE_THRESHOLD = 5;

shouldCollapseBackends = computed(() => 
  this.availableBackends().length > this.CHIP_COLLAPSE_THRESHOLD
);
```

In template:

```html
@if (!shouldCollapseBackends()) {
  <mat-chip-listbox [multiple]="true" ...>
    @for (backend of availableBackends(); track backend) {
      <mat-chip-option [value]="backend">{{ backend }}</mat-chip-option>
    }
  </mat-chip-listbox>
} @else {
  <mat-form-field appearance="outline" class="chip-dropdown">
    <mat-select [multiple]="true" [(ngModel)]="selectedBackends" (selectionChange)="onFilterChange()">
      <mat-option *ngFor="let backend of availableBackends()" [value]="backend">
        {{ backend }}
      </mat-option>
    </mat-select>
  </mat-form-field>
}
```

### 3. Apply to Resource Filters Too

If `resource-filters.component.ts` exists, apply the same pattern.

---

## Verification

```bash
cd praxis/web-client && npm run build
```

---

## Success Criteria

- [x] Filter containers use `flex-wrap: wrap`
- [x] Chip listboxes have max-height with scroll
- [x] Backends with >5 options collapse to dropdown
- [x] No horizontal overflow
