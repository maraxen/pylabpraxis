# Task: Resource Inventory Filters (P3)

## Context

The Resources tab in Asset Management has category dropdowns but lacks the filter chips/toggles that the Machines tab has. Should have parity with machine filtering UX.

## Backlog Reference

See: `.agents/backlog/ui_visual_tweaks.md` - Item #2

## Scope

### Create ResourceFiltersComponent

Match the pattern from machine filters:
- Horizontal scrollable container for filter chips
- Filter by resource type (Plate, TipRack, Trough, Carrier, etc.)
- Filter by category
- Filter by status (available, in-use, maintenance)
- Filter by parent machine/workcell
- Search by name

### Integration

- Add to Resources tab in Asset Management
- Wire up to `AssetService.getResources()` query
- Persist filter state in URL params (optional)

## Files to Reference (for pattern)

Look at how Machine filters are implemented:
- `praxis/web-client/src/app/features/assets/components/` (machine filters)
- `praxis/web-client/src/app/features/execution-monitor/components/run-filters.component.ts`

## Files to Create/Modify

**Create:**
- `praxis/web-client/src/app/features/assets/components/resource-filters/resource-filters.component.ts`

**Modify:**
- `praxis/web-client/src/app/features/assets/assets.component.ts` - Add filter component to Resources tab

## Expected Outcome

- Resources tab has filter chips matching Machines tab pattern
- Filters actually filter the resource list
- Consistent UX across Asset Management tabs
