# Agent Prompt: 35_workcell_machine_filter

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260109](./README.md)
**Backlog:** [ux_issues_260109.md](../../backlog/ux_issues_260109.md)

---

## Task

Filter the Workcell/Spatial View to show only relevant machines (liquid handlers) by default, with option to show all.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [spatial-view.component.ts](../../../praxis/web-client/src/app/features/assets/components/spatial-view/spatial-view.component.ts) | Spatial/deck view |
| [assets.component.ts](../../../praxis/web-client/src/app/features/assets/assets.component.ts) | Parent component |

---

## Current Behavior

```typescript
// spatial-view.component.ts (line 180)
allAssets = computed(() => {
  return [...this.machines(), ...this.resources()];
});
```

Shows ALL machines and resources without filtering by category.

---

## Required Changes

### 1. Add Machine Category Filter

```typescript
// Add to spatial-view.component.ts

machineCategories = signal<string[]>(['LiquidHandler']); // Default to LH only
showAllCategories = signal(false);

filteredMachines = computed(() => {
  if (this.showAllCategories()) {
    return this.machines();
  }
  return this.machines().filter(m =>
    this.machineCategories().includes(m.machine_category || '')
  );
});

allAssets = computed(() => {
  return [...this.filteredMachines(), ...this.resources()];
});
```

### 2. Add Category Toggle UI

```html
<div class="filter-row">
  <mat-button-toggle-group
    [value]="showAllCategories() ? 'all' : 'filtered'"
    (change)="onCategoryToggle($event)">
    <mat-button-toggle value="filtered">
      <mat-icon>science</mat-icon>
      Liquid Handlers
    </mat-button-toggle>
    <mat-button-toggle value="all">
      <mat-icon>devices</mat-icon>
      All Machines
    </mat-button-toggle>
  </mat-button-toggle-group>
</div>
```

### 3. Handle Toggle Change

```typescript
onCategoryToggle(event: MatButtonToggleChange): void {
  this.showAllCategories.set(event.value === 'all');
}
```

### 4. Add Deck View Toggle

If spatial view should show deck visualization:

```typescript
viewMode = signal<'grid' | 'deck'>('grid');

// Add deck view component when machine is selected
selectedMachine = signal<Machine | null>(null);
```

```html
@if (viewMode() === 'deck' && selectedMachine()) {
  <app-deck-view [machine]="selectedMachine()!"></app-deck-view>
} @else {
  <!-- Grid view of assets -->
}
```

---

## Design Considerations

1. **Default State**: Show only LiquidHandler machines (relevant for deck view)
2. **Toggle**: Easy switch to see all machines when needed
3. **Visual Feedback**: Clear indication of which filter is active
4. **Deck View**: Consider adding inline deck visualization when machine selected

---

## Testing

1. Default view shows only LiquidHandler machines
2. Toggle to "All Machines" shows everything
3. Resources always shown
4. No "Demo" machines visible (per prompt 30)
5. Deck view renders for selected machine (if implemented)

---

## On Completion

- [ ] Machine category filter implemented
- [ ] Default to LiquidHandler only
- [ ] Toggle UI added
- [ ] Resources unaffected by machine filter
- [ ] Update backlog status
- [ ] Mark this prompt complete in batch README

---

## References

- [ux_issues_260109.md](../../backlog/ux_issues_260109.md) - Section 4
