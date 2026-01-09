# ARIA Component Overhaul & Standardization Request

## Context

We have been refactoring `AriaSelect`, `AriaMultiselect`, and `AriaAutocomplete` to align with official Angular ARIA patterns. The `AriaMultiselectComponent` has been the primary focus recently, but fixes for one issue (blur behavior) have caused regressions (selection broken, page blocked). The user also wants consistency across all three components.

## Current State & Issues

1. **Overlay Strategy**:
    * `AriaSelect` and `AriaAutocomplete` use `usePopover: 'inline'` (Native Popover API).
    * `AriaMultiselect` was switched to `cdkConnectedOverlay` to try and fix blur issues with the sticky header.
    * **Regression**: usage of `cdkConnectedOverlayHasBackdrop="true"` is blocking page interactions (scrolling, clicking other links).
2. **Blur Behavior**:
    * Sticky headers in `AriaMultiselect` (containing "Select All"/"Clear All" buttons) were preventing standard blur detection.
    * Current "fix" attempts have been unstable.
3. **Selection Logic**:
    * Internal `Listbox` pattern integration seems fragile with the new overlay strategy; user reported clicking items doesn't toggle them.
4. **Inconsistency**:
    * The three components now have divergent implementations for positioning and overlay management.

## Objectives

Perform a deep review and execute a plan to standardize the `Aria*` components.

1. **Standardize Overlay Strategy**:
    * Decide on **ONE** robust strategy for all three components (`Select`, `Multiselect`, `Autocomplete`).
    * **Recommendation**: Revisit `usePopover: 'inline'` but solve the sticky header/blur issue correctly (e.g., using `relatedTarget` checks or properly handling focus containment), OR fully migrate all three to `cdkConnectedOverlay` with a correct non-blocking strategy (e.g., `RepositionScrollStrategy`, no phantom backdrop blocking clicks unless necessary).
    * Ensure the dropdowns stay anchored to the trigger when scrolling.

2. **Fix Multiselect Interactions**:
    * Ensure "Select All", "Clear All", AND individual item toggling works unreliable.
    * Ensure clicking outside closes the dropdown.
    * Ensure clicking inside the sticky header does *not* close the dropdown.

3. **Code Consistency**:
    * Refactor `AriaSelectComponent` and `AriaAutocompleteComponent` to match the agreed-upon best practice.
    * Ensure all use consistent styling patterns from `aria-select.scss`.

## Files to Review

- `src/app/shared/components/aria-multiselect/aria-multiselect.component.ts` (Current problem area)
* `src/app/shared/components/aria-select/aria-select.component.ts` (Reference for single select)
* `src/app/shared/components/aria-autocomplete/aria-autocomplete.component.ts`
* `src/styles/aria-select.scss`

## Development approach

- **Analyze first**: Don't just patch. Understand why `popover` failed for the sticky header and if it can be solved cleanly.
* **Verify**: Ensure build passes and behavior is consistent.
