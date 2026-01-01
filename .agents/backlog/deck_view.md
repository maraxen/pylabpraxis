# Deck Visualizer & UX Backlog

**Focus**: Accurate physical representation of the deck, carriers, slots, and labware status.
**Created**: 2025-12-30
**Last Updated**: 2025-12-30

---

## High Priority

### 1. Structure: Rails, Carriers, Slots

- [x] **Basic Rails Rendering** - ⚠️ PARTIAL:
  - Rails are rendered via `getRails()` loop in `deck-view.component.ts`.
  - **Current Gap**: Uses `$index * 22.5mm` approximation, not hardware-spec positions.
  - **Remaining**: Rails should be a property of the Deck resource, rendered at specific X-coordinates.
- [x] **Carriers Styling** - ⚠️ PARTIAL:
  - `type-carrier` CSS class with gradient styling exists.
  - **Current Gap**: Carriers are styled but not rendered as distinct physical mounting bars.
- [ ] **Slots (Sites)**:
  - Carriers must show distinct "Slots" or "Sites" (e.g., 5 positions on a PLR_Titan_Carrier).
  - **Empty Slots**: Should be visible even when no labware is present (dashed outline or "empty" state).
  - **Full Slots**: Labware should visually "snap" into these slots.
  - **Goal**: Move away from absolute X/Y placement for labware; place labware *into* lists of Slots on a Carrier.

### 2. Itemized Resource Status

- [x] **Tip Status** - ⚠️ PARTIAL:
  - `hasTip(res)` helper exists in deck-view.component.ts
  - `.has-tip` CSS class with styling exists
  - **Remaining**: Support "Tip Masks" or bitmasks to render partial racks efficiently.
- [x] **Well Status** - ⚠️ PARTIAL:
  - `hasLiquid(res)` helper checks for volume > 0
  - `.has-liquid` and `.empty` CSS classes exist
  - **Remaining**: Color-coding based on liquid type/sample group.
- [ ] **State Data**:
  - Ensure `DeckGeneratorService` or the backend state includes granular tip/well data.

### 3. Slot Inference for Deck Rendering

- [ ] **Slot Type Inference**:
  - Infer slot types for deck and protocol setup.
  - Determine compatible carrier/labware combinations automatically.

### 4. Carrier Inference (Minimum Needed)

- [ ] **Auto-Determine Carriers**:
  - For each protocol, calculate minimum carriers needed.
  - Factor in required labware and positions.

### 5. Enhanced Guided Deck Setup (Interactive)

- [x] **Resource Adding Bug** - ✅ RESOLVED 2025-12-31:
  - Fixed issues where adding resources to deck.
  - Resources now snap to valid slots correctly.

- [ ] **Step-by-Step Wizard**:
  - After parameter selection: "Asset Selection" step (current appearance).
  - Final step before initiation: "Deck Setup" section.
  - Walk user through: "Slide carriers into these rails", "Place X into this slot".
  - Skippable with confirmation: "Are you sure the deck is properly configured?"

- [ ] **Z-Axis Ordering Heuristic**:
  - For complex protocols with pre-defined decks, infer order using bottom z-axis.
  - Lower z-axis resources placed first.

- [ ] **Custom/Partial Deck Support**:
  - Handle user-defined deck layouts.
  - Support partial configurations (not all slots used).

### 6. Itemized Resource Spacing

- [ ] **Proper Spacing/Rendering**:
  - Fix spacing and rendering of items in itemized resources (wells, tips).
  - Ensure consistent visual alignment.

---

## Medium Priority

### 7. Interaction & UX

- [ ] **Drag & Drop**: Allow dragging labware from a sidebar into an Empty Slot.
- [ ] **Hover Details**: Hovering a slot should show its ID/Coordinate (e.g., "Carrier 1, Pos 3").
- [ ] **Resource Properties**: Click to inspect specific well data.

---

## Completed - ✅

### 4. Theming - COMPLETE (2025-12-30)

- [x] **PLR-Style Colors**: Implemented dark/light theme support with PLR-style colors.
  - Plates: Blue gradient
  - Tip Racks: Orange gradient
  - Troughs/Reservoirs: Green gradient
  - Carriers: Gray gradient
  - Trash: Dark gray
  - Lids: Translucent with dashed border
  - Petri Dishes: Amber/yellow, circular
  - Tubes/TubeRacks: Purple/violet gradient
  - Plate Adapters: Gray with dotted border
- [x] **Theme Inheritance**: Uses CSS variables (`--plr-bg`, `--plr-deck-bg`, etc.) with `:host-context(.light-theme)` overrides.
- [x] **Full Resource Type Coverage**: All PLR resource types now have themed styling.

---

## Technical Refactoring

- [ ] **Deck Model**: Update `PlrDeckData` to explicitly model `rails` and `slots` if they aren't native PLR resources (PLR often treats Carrier Sites as child resources).
- [ ] **State Sync**: Optimize sending status for 96-well plates (don't send 96 objects if 1 bitmask works).

---

## Related Backlogs

- [ui-ux.md](./ui-ux.md) - General UI/UX items
- [asset_management.md](./asset_management.md) - Deck Setup debugging
