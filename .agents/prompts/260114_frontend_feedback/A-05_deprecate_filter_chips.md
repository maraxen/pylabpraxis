# Agent Prompt: Deprecate FilterChip in Favor of Praxis Select/Multiselect

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** 🟡 Intricate
**Type:** 🟢 Implementation
**Dependencies:** A-01 (Shared View Controls Component)
**Backlog Reference:** Group A - View Controls Standardization, Group B Issue #4 (Category dropdown vs chips)

---

## 1. The Task

Replace the `FilterChipComponent` with `PraxisSelectComponent` and `PraxisMultiselectComponent` for all filter and group-by controls across the application. The chip-based filter pattern should be deprecated in favor of standardized dropdown components.

### User Feedback

> "add resource screen have the category also be a dropdown instead of chips"

### Problem Statement

The current `FilterChipComponent` (310 lines) provides a chip-based menu for single/multi-select filtering. While visually compact, this pattern has several issues:

1. **Inconsistency**: Chips render differently for single vs multi-select modes, causing visual misalignment
2. **Discoverability**: Dropdown menus are a more familiar interaction pattern for filtering
3. **Maintainability**: We already have mature `PraxisSelectComponent` and `PraxisMultiselectComponent` components that implement `ControlValueAccessor` and support proper form integration
4. **Z-index issues**: Chip filtering has reported z-axis alignment problems

### Goals

1. Update `ViewControlsComponent` to use `PraxisSelectComponent` and `PraxisMultiselectComponent` instead of `FilterChipComponent`
2. Remove the `'chips'` filter type from `FilterConfig` (deprecate, keep backward-compatible)
3. Mark `FilterChipComponent` as deprecated
4. Update any direct usages of `FilterChipComponent` elsewhere in the codebase

## 2. Technical Implementation Strategy

### Phase 1: Update ViewControlsComponent

The primary change is in `view-controls.component.ts`:

**Current Implementation (Lines 84-96):**

```typescript
<!-- Filters -->
<div class="filters-chips">
  @for (filterConfig of config.filters; track filterConfig.key) {
    <app-filter-chip
      [label]="filterConfig.label"
      [options]="filterConfig.options || []"
      [selectedValue]="state.filters[filterConfig.key]"
      [multiple]="filterConfig.type === 'multiselect'"
      [isToggle]="filterConfig.type === 'toggle'"
      (selectionChange)="onFilterChange(filterConfig.key, $event)"
    ></app-filter-chip>
  }
</div>
```

**Target Implementation:**

```typescript
<!-- Filters -->
<div class="filters-row">
  @for (filterConfig of config.filters; track filterConfig.key) {
    @switch (filterConfig.type) {
      @case ('multiselect') {
        <app-praxis-multiselect
          [label]="filterConfig.label"
          [options]="filterConfig.options || []"
          [value]="state.filters[filterConfig.key]"
          (valueChange)="onFilterChange(filterConfig.key, $event)"
        ></app-praxis-multiselect>
      }
      @case ('select') {
        <app-praxis-select
          [placeholder]="filterConfig.label"
          [options]="filterConfig.options || []"
          [value]="state.filters[filterConfig.key]?.[0]"
          (valueChange)="onFilterChange(filterConfig.key, [$event])"
        ></app-praxis-select>
      }
      @case ('toggle') {
        <!-- Keep toggle as a button or checkbox -->
        <button 
          mat-stroked-button
          [class.active]="state.filters[filterConfig.key]"
          (click)="onFilterChange(filterConfig.key, !state.filters[filterConfig.key])">
          <mat-icon>{{ state.filters[filterConfig.key] ? 'check_box' : 'check_box_outline_blank' }}</mat-icon>
          {{ filterConfig.label }}
        </button>
      }
    }
  }
</div>
```

### Phase 2: Update Type Definitions

In `view-controls.types.ts`, update the `FilterConfig` type:

**Current (Line 16):**

```typescript
type: 'multiselect' | 'select' | 'chips' | 'toggle';
```

**Target:**

```typescript
/**
 * Filter type.
 * Note: 'chips' is deprecated and will be mapped to 'multiselect'
 */
type: 'multiselect' | 'select' | 'toggle' | 'chips';
```

Add a runtime mapping in `ViewControlsComponent` that treats `'chips'` as `'multiselect'`:

```typescript
private normalizeFilterType(type: FilterConfig['type']): 'multiselect' | 'select' | 'toggle' {
  if (type === 'chips') {
    console.warn('[ViewControlsComponent] Filter type "chips" is deprecated, use "multiselect" instead');
    return 'multiselect';
  }
  return type;
}
```

### Phase 3: Mark FilterChipComponent as Deprecated

Add deprecation notice to `filter-chip.component.ts`:

```typescript
/**
 * @deprecated Use PraxisSelectComponent or PraxisMultiselectComponent instead.
 * This component will be removed in a future release.
 */
@Component({
  selector: 'app-filter-chip',
  // ...
})
export class FilterChipComponent { ... }
```

### Phase 4: Update Imports

In `view-controls.component.ts`, replace:

```typescript
import { FilterChipComponent } from '../filter-chip/filter-chip.component';
```

With:

```typescript
import { PraxisSelectComponent } from '../praxis-select/praxis-select.component';
import { PraxisMultiselectComponent } from '../praxis-multiselect/praxis-multiselect.component';
```

And update the imports array accordingly.

### Phase 5: Styling Adjustments

The `.filters-chips` class should be renamed to `.filters-row` and updated to accommodate the dropdown styling. Ensure horizontal layout, appropriate gaps, and consistent heights with the rest of the ViewControls.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/view-controls/view-controls.component.ts` | Replace FilterChip with Praxis Select/Multiselect (441 lines) |
| `praxis/web-client/src/app/shared/components/view-controls/view-controls.types.ts` | Update/deprecate 'chips' type (52 lines) |
| `praxis/web-client/src/app/shared/components/filter-chip/filter-chip.component.ts` | Add deprecation notice (310 lines) |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/praxis-select/praxis-select.component.ts` | Target component for single-select (152 lines) |
| `praxis/web-client/src/app/shared/components/praxis-multiselect/praxis-multiselect.component.ts` | Target component for multi-select (198 lines) |
| `praxis/web-client/src/app/shared/components/view-controls/group-by-select.component.ts` | Example of select usage in view controls |

**Related Prompts:**

| Prompt | Relationship |
|:-------|:-------------|
| `A-01_shared_view_controls.md` | Creates the ViewControlsComponent being modified |
| `A-04_adopt_shared_controls.md` | Uses ViewControlsComponent across tabs (should use updated version) |
| `GROUP_B_ui_consistency_init.md` | Contains the original user feedback about dropdown vs chips |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks.
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use existing design tokens from `styles/themes/` and `praxis-select.scss`
- **State**: Prefer Signals for new Angular components.
- **Backward Compatibility**: Existing usages of `type: 'chips'` in filter configs should still work (mapped to multiselect)
- **Testing**: Update any affected unit tests

## 5. Verification Plan

**Definition of Done:**

1. `ViewControlsComponent` uses `PraxisSelectComponent` and `PraxisMultiselectComponent` for filters
2. No direct usage of `FilterChipComponent` in ViewControls template
3. `FilterChipComponent` has a `@deprecated` JSDoc notice
4. Existing filter configs with `type: 'chips'` still work (backward compatible)
5. All filter dropdowns are visually consistent and aligned

**Test Commands:**

```bash
cd praxis/web-client
npx tsc --noEmit
npm run build
npm run test -- --include='**/view-controls/**'
```

**Manual Verification:**

1. Navigate to any tab using ViewControls (Spatial, Machines, Resources)
2. Verify filter dropdowns appear instead of chips
3. Verify single-select and multiselect filters work correctly
4. Verify filter selections are persisted correctly
5. Verify "Clear Filters" still works
6. Verify visual alignment of all filter controls

---

## On Completion

- [x] Commit changes with descriptive message: `refactor(view-controls): replace FilterChip with Praxis Select/Multiselect`
- [x] Update `A-01_shared_view_controls.md` to remove 'chips' from the type definition (no longer recommended)
- [x] Update `A-04_adopt_shared_controls.md` to change examples from `type: 'chips'` to `type: 'multiselect'`
- [x] Mark this prompt complete in batch README and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `GROUP_A_view_controls_init.md` - Parent initiative
- `GROUP_B_ui_consistency_init.md` - Contains user feedback on dropdown vs chips
- `.agents/codestyles/typescript.md` - TypeScript conventions
