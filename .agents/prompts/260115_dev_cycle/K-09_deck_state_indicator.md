# Agent Prompt: Deck State Indicator

Examine `.agents/README.md` for development context.

**Status:** 📋 Not Started
**Priority:** P3
**Batch:** [260115](README.md)
**Difficulty:** Low
**Dependencies:** K-08_simulated_deck_states.md
**Backlog Reference:** WCX-001-IMPL (P3.2)

---

## 1. The Task

Create a badge showing the source of the deck state (Live vs Simulated vs Computed) as defined in Phase 3.2 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This helps users trust the data they are seeing.

## 2. Technical Implementation Strategy

**(From workcell_implementation_plan.md)**

**Frontend Components:**

- Generate `src/app/shared/components/workcell/deck-state-indicator/deck-state-indicator.component.ts`.
- Inputs: `source` ('live' | 'simulated' | 'cached' | 'definition').
- Template:
  - 'Live' -> Green/Pulse animation.
  - 'Simulated' -> Blue.
  - 'Definition' -> Gray/Static.
- Integration:
  - Add to `MachineFocusViewComponent` header.
  - Add to `MachineCardComponent` header.

**Backend/Services:**

- None.

**Data Flow:**

- Component accepts `source` string and renders appropriate badge.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `src/app/shared/components/workcell/deck-state-indicator/` | New component directory |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `.agents/artifacts/workcell_ux_redesign.md` | Design specs (Section 7.2) |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use design tokens.
- **Linting**: Run `eslint` or equivalent before committing.

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors.
2. The following tests pass:

   ```bash
   npm run test -- deck-state-indicator
   ```

3. Badge renders correctly for all enum values.

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
