# Task: Visual Index Selection for Itemized Resources (P2)

## Context

Protocol arguments that define indices for itemized resources (wells, tip spots, tube positions) currently use basic form inputs. Users should be able to interactively select indices via click/drag on a visual grid.

Key insight: Itemized resources have `items_x` and `items_y` properties that define their grid dimensions. These should drive the visual selector.

## Backlog Reference

See: `.agents/backlog/visual_well_selection.md`

## Scope

### Phase 1: Core IndexSelectorComponent

Create a reusable Angular component that:
- Renders a grid based on `items_x` (columns) × `items_y` (rows)
- Supports click to select single index
- Supports click + drag for rectangular selection
- Supports Shift+click to extend selection
- Supports Ctrl/Cmd+click to toggle selection
- Outputs array of selected indices

### Phase 2: Linked Arguments

Support linked arguments where multiple parameters share the same indices:
- Tips ↔ Wells (pick tips from positions, aspirate from same-indexed wells)
- Source ↔ Destination wells
- Visual indication of linkage between grids

### Phase 3: Type Inference Integration

- Detect when a protocol argument is an "always-child" type (Well, TipSpot)
- Detect Sequence[Well], Sequence[TipSpot], list[Well], etc.
- Auto-generate IndexSelectorComponent for these arguments
- Get parent resource's `items_x`/`items_y` for grid dimensions

### Phase 4: Backend Integration

- Extend protocol decorator parsing to include `field_type: "index_selector"`
- Pass parent resource info to frontend
- Support linked argument declarations

## Files to Create/Modify

**Create:**
- `praxis/web-client/src/app/shared/components/index-selector/index-selector.component.ts`
- `praxis/web-client/src/app/shared/components/index-selector/index-selector.component.html`
- `praxis/web-client/src/app/shared/components/index-selector/index-selector.component.scss`

**Modify:**
- `praxis/backend/utils/plr_static_analysis/parser.py` - Add itemized resource detection
- `praxis/web-client/src/app/features/run-protocol/` - Integrate selector into protocol forms

## Technical Notes

```typescript
// Grid rendering interface
interface ItemizedResourceSpec {
  items_x: number;  // columns (e.g., 12 for 96-well)
  items_y: number;  // rows (e.g., 8 for 96-well)
}

// Index conversion
const flatIndex = row * items_x + col;
const row = Math.floor(flatIndex / items_x);
const col = flatIndex % items_x;
```

## Expected Outcome

- Users can visually select wells/tips by clicking and dragging
- Linked arguments stay synchronized
- Protocol execution receives correct index arrays
