# Agent Prompt: Workcell Polish & Animations

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P3
**Batch:** [260115](README.md)
**Difficulty:** Medium
**Dependencies:** K-07_machine_focus_view.md
**Backlog Reference:** WCX-001-IMPL (P4.1)

---

## 1. The Task

Apply premium design guidelines and animations as defined in Phase 4.1 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This ensures the "wow" factor.

## 2. Technical Implementation Strategy

**(From workcell_implementation_plan.md)**

**Frontend Components:**

- **Visual Polish**:
  - Apply glassmorphism (backdrop-filter) to sidebar and floating panels.
  - Ensure typography hierarchy matches design system.
  - Verify Dark Mode contrast.
- **Animations**:
  - Implement View Transitions (Grid <-> Focus) using Angular animations or CSS transitions (300ms ease).
  - Add micro-interactions (hover lift, click ripple).
  - Refine 'Running' status pulse.

**Backend/Services:**

- None.

**Data Flow:**

- CSS/Animation changes only.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `src/app/features/workcell/` | Styles across the feature |
| `src/app/shared/components/workcell/` | Component styles |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `.agents/artifacts/workcell_ux_redesign.md` | Design guidelines |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Performance**: Animations must be 60fps (use transform/opacity).
- **Linting**: Run `eslint` or equivalent before committing.

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors.
2. The following tests pass:

   ```bash
   npm run build
   ```

3. Animations are smooth and non-blocking.
4. Dark mode looks consistent and readable.

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
