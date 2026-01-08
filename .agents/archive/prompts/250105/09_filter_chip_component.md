# Prompt 9: Core Filter Chip Component

Create the reusable FilterChipComponent for standardized filter UI.

## Tasks

1. Create `FilterChipComponent` in shared/components/:
   - States: inactive (outlined), active (filled), disabled (grayed, dashed)
   - Input: label, options, selectedValue, disabled, resultCount
   - Output: selectionChange

2. Implement mat-menu integration for dropdown on click

3. Implement disabled state behavior:
   - Grayed out with dashed border
   - On click: subtle horizontal shake animation (~200ms CSS)
   - Show tooltip: "No results match this filter combination"

4. Show "(0 results)" next to disabled options in menu

5. Create `FilterResultService` to pre-compute option availability

6. Write unit tests for all states and interactions

## Files to Create

- `praxis/web-client/src/app/shared/components/filter-chip/filter-chip.component.ts`
- `praxis/web-client/src/app/shared/components/filter-chip/filter-chip.component.html`
- `praxis/web-client/src/app/shared/components/filter-chip/filter-chip.component.scss`
- `praxis/web-client/src/app/shared/services/filter-result.service.ts`

## Reference

- `.agents/backlog/chip_filter_standardization.md` (Phase 1, 2)
