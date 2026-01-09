# Agent Prompt: 32_inventory_dialog_redesign

Examine `.agents/README.md` for development context.

**Status:** 🟢 COMPLETE
**Batch:** [260109](./README.md)
**Backlog:** [ux_issues_260109.md](../../backlog/ux_issues_260109.md)

---

## Task

Redesign the Playground Inventory Dialog to use a tabbed interface with improved UX patterns.

---

## Context Files

| File | Purpose |
| :--- | :------ |
| [inventory-dialog.component.ts](../../../praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts) | **PRIMARY TARGET** - Current dialog |
| [playground.component.ts](../../../praxis/web-client/src/app/features/playground/playground.component.ts) | Parent component |
| [aria-autocomplete.component.ts](../../../praxis/web-client/src/app/shared/components/aria-autocomplete/aria-autocomplete.component.ts) | Autocomplete for quick add |

---

## Current Implementation Issues

1. Two-column layout (stepper + sidebar) is confusing
2. No clear "Add Items" vs "Current Items" separation
3. Stepper lacks visual polish (completion indicators, icons)
4. Search is filter-on-change, not dropdown autocomplete
5. No "Quick Add" option for power users

---

## Required Changes

### 1. Replace Two-Column with Tabbed Layout

```html
<mat-tab-group>
  <mat-tab label="Quick Add">
    <!-- Autocomplete search with filters -->
  </mat-tab>
  <mat-tab label="Browse & Add">
    <!-- Existing stepper workflow -->
  </mat-tab>
  <mat-tab label="Current Items">
    <!-- List of added items with edit/remove -->
  </mat-tab>
</mat-tab-group>
```

### 2. Quick Add Tab

Features:

- Full-width autocomplete search
- Expandable "Filters" accordion with:
  - Asset Type (Machine/Resource)
  - Category filter
  - Status filter
- Results list below search
- Quick "Add" button per result
- Shows recently added items

```html
<div class="quick-add-container">
  <app-aria-autocomplete
    [options]="allAssets()"
    [displayFn]="displayAsset"
    placeholder="Search machines and resources..."
    (selectionChange)="onQuickSelect($event)">
  </app-aria-autocomplete>

  <mat-expansion-panel>
    <mat-expansion-panel-header>
      <mat-panel-title>Filters</mat-panel-title>
    </mat-expansion-panel-header>
    <!-- Filter content -->
  </mat-expansion-panel>

  <!-- Search results list -->
</div>
```

### 3. Browse & Add Tab (Existing Stepper)

Keep existing 4-step flow but add:

- Step icons (user, folder, grid_view, settings)
- Completion checkmarks on finished steps
- Smooth transitions between steps
- Current step highlight styling

```scss
.mat-step-header {
  .mat-step-icon {
    background: var(--mat-sys-primary);
  }
  .mat-step-icon-state-done {
    background: var(--mat-sys-tertiary);
  }
}
```

### 4. Current Items Tab

Replace sidebar with dedicated tab:

- List all added items with:
  - Asset name and type icon
  - Variable name (editable)
  - Category badge
  - Remove button
- "Clear All" button
- Item count badge on tab

### 5. Category Display Fix

Ensure categories are properly displayed:

- Machines: Show `machine_category` (LiquidHandler, PlateReader, etc.)
- Resources: Show `plr_category` or `asset_type`

---

## Design Guidelines

- Tab labels: "Quick Add", "Browse", "Current (N)"
- Quick Add tab should be default for frequent users
- Filter accordion collapsed by default
- Autocomplete shows up to 10 results
- Current items shows count badge when >0

---

## Testing

1. Quick Add tab allows searching and adding in one step
2. Browse tab stepper flows smoothly with visual feedback
3. Current Items shows all added assets with edit/remove
4. Filters work correctly across tabs
5. Categories display correctly for both machines and resources

---

## On Completion

- [x] Tabbed layout implemented
- [x] Quick Add tab with autocomplete + filters
- [x] Stepper visually polished
- [x] Current Items tab functional
- [x] Category display corrected
- [x] Update backlog status
- [x] Mark this prompt complete in batch README

---

## References

- [ux_issues_260109.md](../../backlog/ux_issues_260109.md) - Section 7.3
- [repl_enhancements.md](../../backlog/repl_enhancements.md) - Phase 6
