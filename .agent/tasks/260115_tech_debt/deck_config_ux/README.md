# Task: Deck Config UX & Validation

**ID**: TD-701
**Status**: ⚪ Not Started
**Priority**: P2
**Difficulty**: Medium

---

## 📋 Phase 1: Inspection (I)

**Objective**: Explore the codebase, identify constraints, and gather requirements for deck validation and UX improvements.

- [ ] Search for `deck-catalog.service.ts` and identify missing Vantage deck parameters.
- [ ] Review `DeckVisualizerComponent` and `WorkcellViewComponent` for UX pain points.
- [ ] Search for existing validation logic in deck configuration flows.
- [ ] Research Vantage deck dimensions and rail/slot structure in PyLabRobot.

**Findings**:
> [Captured insights, file paths, and logic flows]

---

## 📐 Phase 2: Planning (P)

**Objective**: Define the implementation strategy for validation, UX, and new deck definitions.

- [ ] Define validation rules for deck states (e.g., overlapping carriers, out-of-bounds, incompatible labware).
- [ ] Design UX improvements for the visualizer (better drag-and-rop, clearer feedback, better layout).
- [ ] Plan implementation for Vantage deck definition in `DeckCatalogService`.

**Implementation Plan**:

1. Implement `getVantageDeckSpec()` in `DeckCatalogService`.
2. Add validation logic to `DeckGeneratorService` or `DeckConstraintService`.
3. Update `DeckVisualizerComponent` with improved interactions and error state visualization.

**Definition of Done**:

1. [ ] Vantage deck is available as a simulation option.
2. [ ] Invalid deck configurations (overlaps, etc.) trigger validation warnings/errors.
3. [ ] Improved UX for deck configuration (e.g., smoother interactions, better visual feedback).

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement the planned changes.

- [ ] [Sub-task 1]
- [ ] [Sub-task 2]

**Work Log**:

- [Timestamp]: [Action taken]

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify the fix and ensure no regressions.

- [ ] Unit Tests: `npm test deck-catalog.service`
- [ ] Manual Verification: Select Vantage deck, try creating invalid layout, verify UX.

**Results**:
> [Test logs or confirmation]

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Technical Debt ID**: 701
- **Files**:
  - `praxis/web-client/src/app/features/run-protocol/services/deck-catalog.service.ts`
  - `praxis/web-client/src/app/features/run-protocol/services/deck-generator.service.ts`
  - `praxis/web-client/src/app/features/run-protocol/components/deck-visualizer/deck-visualizer.component.ts` (hypothetical path)
