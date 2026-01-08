# Filter Result Counts (Phase 2)

**Backlog**: `chip_filter_standardization.md`
**Priority**: P2
**Effort**: Medium

---

## Goal

Integrate `FilterResultService` into filter components to show result counts on chips and disable options that yield 0 results.

## Background

Phase 1 (Core Filter Chip Component) is complete. The shake animation and tooltip for disabled chips are already implemented in `FilterChipComponent`. Phase 2 adds the logic to calculate and display result counts.

## Tasks

1. **Extend `FilterResultService`**
   - Add method to compute counts for all filter combinations
   - Support "delta" counting (how many results if this filter is toggled)

2. **Update `ResourceFiltersComponent`**
   - Replace `mat-chip-listbox` with custom `FilterChipComponent`
   - Pass result counts to each chip
   - Handle disabled state for 0-result options

3. **Add Result Count Display**
   - Show "(N)" next to each chip option in dropdown
   - Gray out and show "(0)" for options yielding no results

4. **Unit Tests**
   - Test `FilterResultService.computeOptionAvailability()`
   - Test chip disabled state triggers shake on click
   - Test tooltip appears for disabled chips

## Files to Modify

| File | Action |
|------|--------|
| `shared/services/filter-result.service.ts` | Extend |
| `features/assets/components/resource-filters/resource-filters.component.ts` | Major refactor |
| `shared/components/filter-chip/filter-chip.component.ts` | Minor (verify inputs) |

## Latency Considerations

- Calculation is in-memory on filtered result set
- Expected <10ms for inventories up to 5,000 items
- Use `computed()` signals for automatic memoization

## Success Criteria

- [ ] Chips show result counts
- [ ] 0-result chips are disabled
- [ ] Shake animation triggers on disabled click
- [ ] Tooltip explains why chip is disabled
