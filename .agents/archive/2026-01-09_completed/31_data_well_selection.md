# Agent Prompt: 31_data_well_selection

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260109](./README.md)
**Backlog:** [ux_issues_260109.md](../../backlog/ux_issues_260109.md)

---

## Task

Replace the wells chip display in the Data Visualization page with a button that opens the Well Selector Dialog component.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [data-visualization.component.ts](../../../praxis/web-client/src/app/features/data/data-visualization.component.ts) | **Lines 210-221** - Current chip display |
| [well-selector-dialog.component.ts](../../../praxis/web-client/src/app/shared/components/well-selector-dialog/well-selector-dialog.component.ts) | Existing dialog to reuse |
| [well-selector.component.ts](../../../praxis/web-client/src/app/shared/components/well-selector/well-selector.component.ts) | Core well selector |

---

## Current Implementation

```typescript
// data-visualization.component.ts (lines 210-221)
<mat-chip-set>
  @for (well of allWells; track well) {
    <mat-chip [class.selected]="selectedWells().includes(well)"
      (click)="toggleWell(well)">
      {{ well }}
    </mat-chip>
  }
</mat-chip-set>
```

This displays individual chips for each well, which becomes unwieldy for plates with 96 or 384 wells.

---

## Required Changes

### 1. Replace Chip Set with Selection Button

```html
<button mat-stroked-button (click)="openWellSelector()">
  <mat-icon>grid_view</mat-icon>
  {{ selectedWells().length > 0
     ? selectedWells().length + ' wells selected'
     : 'Select Wells' }}
</button>

<!-- Show selected wells as preview chips (collapsed if >5) -->
@if (selectedWells().length > 0 && selectedWells().length <= 5) {
  <mat-chip-set>
    @for (well of selectedWells(); track well) {
      <mat-chip (removed)="removeWell(well)">
        {{ well }}
        <mat-icon matChipRemove>cancel</mat-icon>
      </mat-chip>
    }
  </mat-chip-set>
}

@if (selectedWells().length > 5) {
  <span class="text-sm text-gray-500">
    {{ selectedWells().slice(0, 3).join(', ') }}... and {{ selectedWells().length - 3 }} more
  </span>
}
```

### 2. Implement openWellSelector Method

```typescript
openWellSelector(): void {
  const dialogRef = this.dialog.open(WellSelectorDialogComponent, {
    data: {
      plateType: this.currentPlateType(), // e.g., 'plate_96_wellplate'
      selectedWells: this.selectedWells(),
      title: 'Select Wells for Visualization'
    },
    width: '800px',
    maxHeight: '90vh'
  });

  dialogRef.afterClosed().subscribe(result => {
    if (result) {
      this.selectedWells.set(result);
      this.loadWellData();
    }
  });
}
```

### 3. Add removeWell Method

```typescript
removeWell(well: string): void {
  this.selectedWells.update(wells => wells.filter(w => w !== well));
  this.loadWellData();
}
```

### 4. Determine Plate Type

The dialog needs to know the plate dimensions. Options:
- Derive from the data source (run metadata)
- Use a default 96-well plate
- Allow user to specify plate type

---

## Design Guidelines

- Button should match existing filter button styling
- Preview chips should be removable individually
- Collapsed state should show count, not all wells

---

## Testing

1. Click "Select Wells" button opens dialog
2. Select wells using click/drag in dialog
3. Confirm selection updates visualization
4. Individual wells can be removed via chip X button
5. Large selections show collapsed preview

---

## On Completion

- [ ] Chip set replaced with selection button
- [ ] Well selector dialog integration complete
- [ ] Preview chips with remove functionality
- [ ] Collapsed display for large selections
- [ ] Update backlog status
- [ ] Mark this prompt complete in batch README

---

## References

- [ux_issues_260109.md](../../backlog/ux_issues_260109.md) - Section 5.1
- [dataviz_well_selection.md](../../backlog/dataviz_well_selection.md) - Related backlog
