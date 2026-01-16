# Inspection Summary: View Controls Chips

## Component Analysis

**Component**: `ViewControlsComponent`
**Location**: `praxis/web-client/src/app/shared/components/view-controls/view-controls.component.ts`

### Current Chip Rendering

- **Location**: Inline in template (lines 189-202).
- **Logic**: Iterates over `activeFilters()` computed signal.
- **Structure**:

  ```html
  <div class="active-filters-row">
    <span class="active-label">Active:</span>
    <div class="chips-scroll-container">
      @for (filter of activeFilters(); track filter.filterId) {
        <span class="filter-chip">...</span>
      }
    </div>
  </div>
  ```

- **Styling**:
  - Encapsulated in component styles.
  - Uses `var(--theme-surface-elevated)` for background.
  - Simple text + close icon.

### Issues Identified

1. **Placement**: Chips are in a separate row below the main controls, which takes up vertical space.
2. **UX**: No tooltips or icons to distinguish filter types easily.
3. **Coupling**: Rendering logic is tightly coupled to `ViewControlsComponent`.

### Refactoring Opportunities

- Extract chip rendering to `FilterChipBarComponent`.
- Implement `IconMappingService` or localized map for filter types.
- Move `activeFilters` logic to the new component or keep as input.

## Integration Points

- Used in `ProtocolLibraryComponent`, `MachineListComponent`, `ResourceAccordionComponent`, etc.
- Any change to `ViewControlsComponent` will propagate to these views automatically.
- `DeckVisualizerComponent` does *not* use this component, so this refactor is scoped to list/grid views, not the main deck visualizer (though they may share styles later).
