# Visual Well Selection - Linked Arguments (Phase 2)

**Backlog**: `visual_well_selection.md`
**Priority**: P2
**Effort**: Medium

---

## Goal

Support linked arguments where multiple protocol parameters share the same indices (e.g., source wells ↔ destination wells, tips ↔ wells).

## Background

Phase 1 (Core Index Selector Component) is complete:

- Grid rendering based on `items_x` × `items_y`
- Click, drag, shift-click, ctrl-click selection
- Row/column header selection
- Output in array and well notation formats

## Use Cases

1. **Tips ↔ Wells**: Pick tips from positions, aspirate from same-indexed wells
2. **Source ↔ Destination**: Transfer from wells A1-A4 to wells B1-B4
3. **Multi-channel**: 8-channel pipette selecting 8 wells at once

## Tasks

1. **Linked Argument Detection**
   - Parse `linked_to` parameter from protocol decorator
   - Or infer from matching Sequence lengths
   - Example: `@protocol(tips: Sequence[TipSpot], wells: Sequence[Well], linked=["tips", "wells"])`

2. **Linked Selection UI**
   - Show both grids side-by-side
   - Selection in one mirrors to the other
   - Visual indication of linkage (connecting lines or shared highlight color)
   - Option to unlink for independent selection

3. **Index Mapping**
   - Same indices selected in both
   - Support offset mapping (source A1:A8 → dest B1:B8)

4. **Unit Tests**
   - Test linked selection synchronization
   - Test offset mapping
   - Test unlink toggle

## Files to Modify

| File | Action |
|------|--------|
| `shared/components/index-selector/index-selector.component.ts` | Add linking support |
| `features/run-protocol/components/parameter-config/` | Render side-by-side |
| Backend protocol parsing | Extract `linked_to` metadata |

## Success Criteria

- [ ] Linked grids show side-by-side
- [ ] Selection in one grid updates the other
- [ ] Offset mapping works correctly
- [ ] User can unlink for independent selection
