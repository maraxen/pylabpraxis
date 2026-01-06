# Visual Index Selection for Itemized Resources

**Priority**: P2 (High)
**Owner**: Frontend + Backend
**Created**: 2026-01-04
**Updated**: 2026-01-04
**Status**: In Progress - Phase 1-4 Complete

---

## Overview

When a protocol argument defines indices for an itemized resource (wells, tip spots, tube positions, etc.), the current form-based input is insufficient. Itemized resources have `items_x` and `items_y` properties that define their grid dimensions. Users should be able to interactively select indices by clicking and dragging, shift-clicking for ranges, etc.

**This applies to any itemized resource with grid children:**

- Wells in plates (96-well, 384-well, etc.)
- TipSpots in tip racks
- Tube positions in tube racks
- Any resource with `items_x` × `items_y` grid

---

## Goals

1. **Interactive Index Selection**: Replace text input with visual click/drag selection grid
2. **Dynamic Grid Rendering**: Use `items_x` and `items_y` from resource to render correct grid size
3. **Linked Arguments**: Support shared indices across multiple arguments (e.g., tips and wells use same selection)
4. **Type Inference**: Auto-detect arguments that should use visual selection
5. **Backend Integration**: Improve Formly/form field parsing from protocol decorator

---

## Phase 1: Core Index Selector Component ✅

### Tasks (Completed 2026-01-04)

- [x] **Create `IndexSelectorComponent`**
  - Grid layout based on `items_x` (columns) × `items_y` (rows)
  - Click to select single index
  - Click + drag to select rectangular region
  - Visual feedback for selected indices (highlight/fill)
  - Configurable for any grid dimensions

- [x] **Selection Interaction**
  - [x] Single click: select one index
  - [x] Click + drag: select rectangular region
  - [x] Shift + click: extend selection from last selected
  - [x] Ctrl/Cmd + click: toggle selection
  - [x] Click on row/column header: select entire row/column

- [x] **Output Formats**
  - [x] Array of indices: `[0, 1, 2, 3]` (flattened)
  - [x] Well notation: `["A1", "A2", "B1", "B2"]`

- [x] **Grid Rendering from Resource**

  ```typescript
  interface ItemizedResourceSpec {
    itemsX: number;  // columns
    itemsY: number;  // rows
    label?: string;  // optional label
    linkId?: string; // for linked selectors
  }
  ```

---

## Phase 2: Linked Arguments Support

When multiple protocol arguments share the same indices (e.g., source wells and destination wells, or tips and wells), they should be linked so selecting in one updates the other.

### Use Cases

1. **Tips ↔ Wells**: Pick tips from positions, aspirate from same-indexed wells
2. **Source ↔ Destination**: Transfer from wells A1-A4 to wells B1-B4
3. **Multi-channel operations**: 8-channel pipette selecting 8 wells at once

### Tasks

- [ ] **Linked Argument Detection**
  - Protocol decorator can specify `linked_to` parameter
  - Or infer from matching Sequence lengths
  - Example: `@protocol(tips: Sequence[TipSpot], wells: Sequence[Well], linked=["tips", "wells"])`

- [ ] **Linked Selection UI**
  - Show both grids side-by-side
  - Selection in one mirrors to the other
  - Visual indication of linkage (connecting lines or shared highlight color)
  - Option to unlink for independent selection

- [ ] **Index Mapping**
  - Same indices selected in both
  - Or offset mapping (source A1:A8 → dest B1:B8)

---

## Phase 3: Type Inference & Form Integration

### Always-Child Types

These types should always trigger visual index selection:

- `Well` - single index from a plate
- `TipSpot` - single index from a tip rack
- `list[Well]` / `Sequence[Well]` - multiple indices
- `list[TipSpot]` / `Sequence[TipSpot]` - multiple indices
- Any type annotated with itemized resource parent

### Protocol Decorator Parsing

- [ ] **Identify Itemized Resource Arguments**
  - Parse type annotations from protocol decorator
  - Check if type is a known "always-child" type
  - Check if type is a Sequence of an always-child type

- [ ] **Parent Resource Association**
  - Determine which parent resource the argument refers to
  - Get `items_x` and `items_y` from parent resource definition
  - If argument has a `parent` hint in decorator, use it

- [ ] **Form Field Generation**
  - When itemized resource arg detected, generate `IndexSelectorComponent`
  - Pass parent resource dimensions (`items_x`, `items_y`) to selector
  - Pass current item states (tip presence, liquid levels) for visualization

---

## Phase 4: Visual State Overlay

Show current state of items in the grid (optional enhancement).

### Tasks

- [ ] **Item State Visualization**
  - Tips: Show presence/absence (filled vs empty circle)
  - Wells: Show liquid level (fill gradient)
  - Selectable items highlighted differently from state display

- [ ] **State Data Flow**
  - Get current deck state from `DeckGeneratorService`
  - Map item indices to state values
  - Real-time updates if state changes

---

## Phase 5: Backend Formly Integration (Partially Complete ✅)

### Current State

Protocol parameters are parsed on the backend and sent to the frontend as form field definitions.

### Tasks

- [x] **Extend Protocol Decorator Parsing** (Partial)
  - [x] Add `field_type`, `is_itemized`, `itemized_spec`, `linked_to` fields to `ProtocolParameterInfo`
  - [x] Add `num_items_x`, `num_items_y` to `DiscoveredCapabilities`
  - [ ] Include parent resource info dynamically from context

- [x] **Formly Custom Type**
  - [x] Register `index-selector` as custom Formly type
  - [x] Create `IndexSelectorFieldComponent` wrapper
  - [x] Map backend metadata to component inputs in `ParameterConfigComponent`

- [ ] **Validation** (Future)
  - [ ] Ensure selected indices are within bounds (0 to items_x*items_y - 1)
  - [ ] Validate selection count against protocol requirements (min/max)
  - [ ] Validate linked arguments have matching selection counts

---

## Technical Considerations

### Index Coordinate Systems

- Backend uses 0-indexed flat integers or (row, col) tuples
- Frontend displays A1 notation for plates (row letter + column number)
- Conversion utilities needed:

  ```typescript
  // Flat index to (row, col)
  const row = Math.floor(index / items_x);
  const col = index % items_x;

  // (row, col) to well notation
  const wellName = String.fromCharCode(65 + row) + (col + 1);
  ```

### Large Grids (384-well)

- 384-well plates (16×24) need efficient rendering
- Consider virtualization for performance
- Keyboard shortcuts for "select all", "select column", "select row"

### Touch Support

- Drag selection on touch devices
- Pinch-to-zoom for large grids

---

## Related Files

| File | Purpose |
|------|---------|
| `praxis/backend/utils/plr_static_analysis/` | Protocol parsing, type inference |
| `praxis/backend/utils/plr_static_analysis/resource_hierarchy.py` | Itemized resource detection |
| `praxis/web-client/src/app/features/run-protocol/` | Protocol execution forms |
| `praxis/web-client/src/app/shared/components/` | Shared components |

---

## Success Criteria

1. [ ] Users can click/drag to select indices instead of typing
2. [ ] Grid renders correctly based on `items_x` × `items_y`
3. [ ] Linked arguments stay synchronized
4. [ ] Shift+click extends selection appropriately
5. [ ] Protocol arguments with itemized resource types auto-use visual selector
6. [ ] Selected indices correctly passed to protocol execution
7. [ ] Works for various grid sizes (96, 384, custom)
