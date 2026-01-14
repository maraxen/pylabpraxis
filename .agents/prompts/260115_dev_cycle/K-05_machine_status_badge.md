# Agent Prompt: Machine Status Badge

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260115](README.md)
**Difficulty:** Low
**Dependencies:** K-01_workcell_models.md
**Backlog Reference:** WCX-001-IMPL (P1.3)

---

## 1. The Task

Create a reusable status indicator component as defined in Phase 1.3 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This provides a consistent way to display machine state across the app.

## 2. Technical Implementation Strategy

**(From workcell_implementation_plan.md)**

**Frontend Components:**

- Create `src/app/shared/components/workcell/machine-status-badge/machine-status-badge.component.ts`.
- Inputs:
  - `status`: MachineStatus (idle, running, error, etc.)
  - `stateSource`: 'live' | 'simulated' | 'cached'
  - `showLabel`: boolean
  - `compact`: boolean
- Logic:
  - Map status to CSS classes/colors (Green, Amber, Red, Gray).
  - Implement pulse animation for 'running' status.

**Backend/Services:**

- None.

**Data Flow:**

- Pure presentation component receiving inputs and rendering UI.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `src/app/shared/components/workcell/machine-status-badge/` | New component directory |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `.agents/artifacts/workcell_ux_redesign.md` | Design specs (Section 7.2 for tokens) |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use CSS variables defined in design system.
- **Linting**: Run `eslint` or equivalent before committing.

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors.
2. The following tests pass:

   ```bash
   npm run test -- machine-status-badge
   ```

3. Visual verification in Storybook (if available) or demo page confirms correct colors/animations for all states.

---

## On Completion

- [x] Commit changes with descriptive message referencing the backlog item
- [x] Update backlog item status
- [x] Update DEVELOPMENT_MATRIX.md if applicable
- [x] Mark this prompt complete in batch README and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `TECHNICAL_DEBT.md` - Known issues
