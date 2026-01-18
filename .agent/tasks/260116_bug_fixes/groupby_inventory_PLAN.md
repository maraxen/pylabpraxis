# Plan: Fix Inventory GroupBy Issues

## Goal

Fix the issues where setting "Group By" to "None" causes:

1. Duplicate "None" options in the dropdown.
2. "Nothing happens" (or potential crash) in the Inventory/Resource views.
3. Ensure `groupBy: null` properly triggers a flat list view where applicable.

## Findings

1. **Duplicate "None" Options:**
    * `GroupBySelectComponent` (`praxis/web-client/src/app/shared/components/view-controls/group-by-select.component.ts`) automatically adds a `<mat-option [value]="null">None</mat-option>`.
    * Feature components (`DefinitionsListComponent`, `MachineListComponent`, `ResourceAccordionComponent`) *also* add explicit `{ label: 'None', value: null }` to their `groupByOptions` config.
    * **Fix:** Remove the explicit "None" option from the feature component configurations.

2. **GroupBy "None" Logic:**
    * **Machine Inventory (`MachineListComponent`):** Does not implement grouping in its template (Table/Card/List views are flat). The "Group By" control is present but ineffective for layout changes. It might be intended for sorting or future features, but current behavior is "no grouping" regardless of selection.
    * **Machine Definitions (`MachineDefinitionAccordionComponent`):** Correctly handles `groupBy: null` (via `@else` block) by showing a flat list of definitions.
    * **Resource Inventory (`ResourceAccordionComponent`):**
        * Template checks `@if (viewState().viewType === 'accordion')` and then immediately iterates over groups: `@for (group of filteredGroups(); ...`.
        * It *ignores* `viewState().groupBy`.
        * This causes "Nothing happens" when "None" is selected; it stays grouped by Category.
    * **Fix:** Update `ResourceAccordionComponent` template to check `viewState().groupBy`.
        * If `groupBy` is set, show the Accordion (grouped view).
        * If `groupBy` is `null` (None), show a flat list of resources (similar to `viewType: 'list'` but perhaps using the definition items directly).

## Proposed Changes

### 1. Remove Duplicate "None" Options

Modify the `computed` config in the following files to remove `{ label: 'None', value: null }`:

* `praxis/web-client/src/app/features/assets/components/definitions-list/definitions-list.component.ts`
* `praxis/web-client/src/app/features/assets/components/machine-list/machine-list.component.ts`
* `praxis/web-client/src/app/features/assets/components/resource-accordion/resource-accordion.component.ts`

### 2. Implementation: Logic for GroupBy None in ResourceAccordion

Modify `praxis/web-client/src/app/features/assets/components/resource-accordion/resource-accordion.component.ts`:

**Add `filteredFlatDefinitions` computed signal**:

```typescript
/**
 * Flat list of definitions when groupBy is null
 * Flattens the grouped structure while preserving all filters
 */
readonly filteredFlatDefinitions = computed(() => {
  // Get the already-filtered groups
  const groups = this.filteredGroups();
  
  // Flatten: extract items from each group and combine
  return groups
    .map(group => group.items)  // Extract items arrays
    .flat();                     // Flatten into single array
});
```

**Update Template**:

```html
@if (viewState().viewType === 'accordion') {
  @if (viewState().groupBy) {
    <!-- Grouped Accordion View -->
    <mat-accordion multi="true">
      @for (group of filteredGroups(); track group.category) {
        <mat-expansion-panel>
          <mat-expansion-panel-header>
            <mat-panel-title>{{ group.category }} ({{ group.count }})</mat-panel-title>
          </mat-expansion-panel-header>
          @for (item of group.items; track item.definition.accession_id) {
            <!-- definition-item template -->
          }
        </mat-expansion-panel>
      }
    </mat-accordion>
  } @else {
    <!-- Flat List View (groupBy: null) -->
    <div class="definition-list">
      @for (item of filteredFlatDefinitions(); track item.definition.accession_id) {
        <!-- Reuse the same definition-item template/component -->
        <app-resource-definition-item [item]="item"></app-resource-definition-item>
      }
    </div>
  }
}
```

**Note**: If the definition-item markup is currently inline, consider extracting it to a separate Angular component (`ResourceDefinitionItemComponent`) for better reusability.

### 3. Verify Defensive Checks

* Ensure `GroupBySelectComponent` handles `value: null` correctly (it does).
* Ensure `onGroupByChange` handles `null` correctly (it does).

## Verification Plan

### Automated Tests

* `npm run test -- praxis/web-client/src/app/features/assets/components/resource-accordion/resource-accordion.component.spec.ts`
* If no existing test covers `groupBy: null` behavior, add a unit test case in `resource-accordion.component.spec.ts`:
  * Set `viewState.groupBy = null`.
  * Verify that `mat-accordion` is NOT present.
  * Verify that `.definition-item` elements are present (flat list).

### Manual Verification

1. **Duplicate Check**:
    * Open "Inventory" (Resources or Machines).
    * Click "Group By" dropdown.
    * Verify only **one** "None" option exists.
2. **Functionality Check (Resources)**:
    * Go to **Inventory > Resources**.
    * Select "Group By: None".
    * Verify list transforms from Accordion (Categories) to a Flat List of resources.
    * Verify no console errors (Crash check).
3. **Functionality Check (Machine Definitions)**:
    * Go to **Add Machine** (Registry).
    * Select "Group By: None".
    * Verify flat list appears.
