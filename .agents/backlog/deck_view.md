# Deck Visualizer & UX Backlog

**Focus**: Accurate physical representation of the deck, carriers, slots, and labware status.
**Created**: 2025-12-30

## High Priority

### 1. Structure: Rails, Carriers, Slots

- [ ] **Accurate Rails**:
  - Rails should be rendered as straight vertical mounting tracks along the X-axis.
  - **Current Gaps**: Currently determined by a simple loop (`i * 22.5mm`), which approximates a STAR deck but isn't semantic.
  - **Goal**: Rails should be a property of the Deck resource, rendered at specific X-coordinates defined by the hardware spec.
- [ ] **Carriers**:
  - Carriers should be rendered as visible physical objects (grey/metallic bars) attached to specific rails.
  - **Current Gaps**: Carriers are currently just transparent containers for labware.
- [ ] **Slots (Sites)**:
  - Carriers must distinct "Slots" or "Sites" (e.g., 5 positions on a PLR_Titan_Carrier).
  - **Empty Slots**: Should be visible even when no labware is present (dashed outline or "empty" state).
  - **Full Slots**: Labware should visual "snap" into these slots.
  - **Goal**: Move away from absolute X/Y placement for labware; place labware *into* lists of Slots on a Carrier.

### 2. Itemized Resource Status

- [ ] **Tip Status**:
  - Visualize individual tip presence (full vs empty spots in a rack).
  - Support "Tip Masks" or bitmasks to render partial racks efficiently.
- [ ] **Well Status**:
  - **Volume**: Visual indication of liquid level (heatmap or fill level).
  - **Contents**: Color-coding based on liquid type/sample group.
- [ ] **State Data**:
  - Ensure `DeckGeneratorService` or the backend state includes this granular data (it currently mocks empty/full states broadly).

## Medium Priority

### 3. Interaction & UX

- [ ] **Drag & Drop**: Allow dragging labware from a sidebar into an Empty Slot.
- [ ] **Hover Details**: Hovering a slot should show its ID/Coordinate (e.g., "Carrier 1, Pos 3").
- [ ] **Resource Properties**: Click to inspect specific well data.

## Technical Refactoring

- [ ] **Deck Model**: Update `PlrDeckData` to explicitly model `rails` and `slots` if they aren't native PLR resources (PLR often treats Carrier Sites as child resources).
- [ ] **State Sync**: Optimize sending status for 96-well plates (don't send 96 objects if 1 bitmask works).

### 4. Theming

- [ ] **Theme Inheritance**:
  - The visuals (rails, slots, carriers) currently use hardcoded styling (e.g. `background: #f5f5f5`).
  - **Goal**: Use CSS variables (`var(--sys-surface)`, `var(--sys-outline)`) so the deck view respects Light/Dark mode.
