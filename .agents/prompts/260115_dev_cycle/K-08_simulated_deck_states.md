# Agent Prompt: Simulated Deck States

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P1
**Batch:** [260115](README.md)
**Difficulty:** High
**Dependencies:** K-07_machine_focus_view.md
**Backlog Reference:** WCX-001-IMPL (P3.1)

---

## 1. The Task

Connect `plr_state` to `DeckViewComponent` to visualize live liquid levels and tip presence as defined in Phase 3.1 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This brings the visualization to life.

## 2. Technical Implementation Strategy

**(From workcell_implementation_plan.md)**

**Frontend Components:**

- Update `DeckViewComponent` (`src/app/shared/components/deck-view/deck-view.component.ts`):
  - Add Input: `stateSource` ('live' | 'simulated' | 'definition').
  - Styling: Apply border/overlay styles based on `stateSource`.
- Enhance `LabwareComponent` (and similar sub-components):
  - Render liquid levels in wells (using gradient or opacity).
  - Render tip presence in TipRacks based on bitmask.

**Backend/Services:**

- Update `WorkcellViewService`:
  - Extract state from `Machine.plr_state`.
  - Transform it into `PlrState` interface for consumption by the component.

**Data Flow:**

1. Service parses `plr_state` JSON.
2. Service computed signal updates.
3. Deck View binds to this data and updates visuals (liquid height, tip visibility).

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `src/app/shared/components/deck-view/deck-view.component.ts` | Main visualization component |
| `src/app/features/workcell/services/workcell-view.service.ts` | Data transformation logic |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `.agents/artifacts/workcell_ux_redesign.md` | UX specs (Section 2.4) |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Performance**: Optimize rendering updates (avoid full re-render if possible).
- **Linting**: Run `eslint` or equivalent before committing.

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors.
2. The following tests pass:

   ```bash
   npm run test -- deck-view
   ```

3. "Live" state shows liquid levels clearly.
4. "Definition" state shows empty deck (or default).
5. Tip racks correctly show missing tips.

---

## On Completion

- [ ] Commit changes with descriptive message referencing the backlog item
- [ ] Update backlog item status
- [ ] Update DEVELOPMENT_MATRIX.md if applicable
- [ ] Mark this prompt complete in batch README and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `TECHNICAL_DEBT.md` - Known issues
