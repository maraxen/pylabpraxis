# Agent Prompt: Machine Card Component

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260115](README.md)
**Difficulty:** Medium
**Dependencies:** K-04_workcell_explorer.md, K-05_machine_status_badge.md
**Backlog Reference:** WCX-001-IMPL (P2.1)

---

## 1. The Task

Create the machine card component for the dashboard grid view as defined in Phase 2.1 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This constitutes the primary view item for the grid layout.

## 2. Technical Implementation Strategy

**(From workcell_implementation_plan.md)**

**Frontend Components:**

- Generate `src/app/shared/components/workcell/machine-card/`:
  - `machine-card.component.ts`
  - `machine-card.component.scss`
  - `machine-card-mini.component.ts` (Compact variant)
- Structure:
  - Header: Icon + Name + `app-machine-status-badge`.
  - Content: Mini `DeckView` (or placeholder) + Protocol Progress bar (if running).
  - Footer: "Focus View" button + Context Menu trigger.
- Integration: Add to `WorkcellDashboardComponent` template.

**Backend/Services:**

- None.

**Data Flow:**

- Inputs: `MachineWithRuntime` object.
- Outputs: `machineSelected` event.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `src/app/shared/components/workcell/machine-card/` | New component directory |
| `src/app/features/workcell/workcell-dashboard/workcell-dashboard.component.ts` | Integration point |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `.agents/artifacts/workcell_ux_redesign.md` | Design reference (Section 3.3) |
| `.agents/prompts/260115_dev_cycle/K-05_machine_status_badge.md` | Dependency |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Styling**: Adhere to card styling tokens.
- **Linting**: Run `eslint` or equivalent before committing.

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors.
2. The following tests pass:

   ```bash
   npm run test -- machine-card
   ```

3. Cards render correctly in the dashboard grid.
4. Clicking a card navigates/emits event correctly.

---

## On Completion

- [ ] Commit changes with descriptive message referencing the backlog item
- [ ] Update backlog item status
- [ ] Update DEVELOPMENT_MATRIX.md if applicable
- [x] Mark this prompt complete in batch README and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `TECHNICAL_DEBT.md` - Known issues
