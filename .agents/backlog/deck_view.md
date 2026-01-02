# Deck Visualizer & UX Backlog

**Focus**: Accurate physical representation of the deck, carriers, slots, and labware status.
**Created**: 2025-12-30
**Last Updated**: 2026-01-02

> 📋 **Detailed Implementation Plan Available**
>
> For the **Enhanced Guided Deck Setup** feature and related phases (Semantic Deck Model, Slot-Based Rendering, Carrier Inference), see:
> **[guided_deck_setup.md](./guided_deck_setup.md)** - Full 5-phase implementation plan with architecture, code examples, and success criteria.

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

- [x] **Tip Status** - ✅ COMPLETE:
  - `hasTip(res)` helper exists in deck-view.component.ts
  - `.has-tip` CSS class with styling exists
  - Bitmask/Parent state support added.
- [x] **Well Status** - ✅ COMPLETE:
  - `hasLiquid(res)` helper checks for volume > 0 and renders gradient fill.
  - `.has-liquid` and `.empty` CSS classes exist
  - Color-coding based on resource color or default liquid blue.
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

- [x] **Proper Spacing/Rendering** - ✅ COMPLETE:
  - Fixed spacing and rendering of items in itemized resources (wells, tips).
  - Implemented `scaleBottom` to correctly map PLR Bottom-Left coordinate system.

---

## Medium Priority

### 7. Interaction & UX

- [x] **Drag & Drop**: ✅ COMPLETE (2026-01-01) - Drag labware into slots.
- [x] **Hover Details**: ✅ COMPLETE (2026-01-02) - Rich tooltip with name, type, dimensions, volume, tip status.
- [x] **Resource Properties**: ✅ COMPLETE (2026-01-02) - Click-to-inspect side panel with detailed properties.

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

- [x] **Deck Model**: ✅ COMPLETE (2026-01-02) - Updated `PlrDeckData` to include optional `rails` and `carriers` fields. Added `PlrResourceDetails` interface.
- [x] **State Sync**: ✅ COMPLETE (2026-01-02) - Implemented bitmask encoding (`tip_mask`, `liquid_mask`) for efficient 96-well state transmission.

---

## Related Backlogs

- [ui-ux.md](./ui-ux.md) - General UI/UX items
- [asset_management.md](./asset_management.md) - Deck Setup debugging
