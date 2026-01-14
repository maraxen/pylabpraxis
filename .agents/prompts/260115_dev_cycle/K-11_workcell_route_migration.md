# Agent Prompt: Workcell Route Migration

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P3
**Batch:** [260115](README.md)
**Difficulty:** Low
**Dependencies:** K-10_workcell_polish.md
**Backlog Reference:** WCX-001-IMPL (P4.2)

---

## 1. The Task

Replace the old visualizer with the new dashboard as defined in Phase 4.2 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This is the final switch-over.

## 2. Technical Implementation Strategy

**(From workcell_implementation_plan.md)**

**Frontend Components:**

- Update `src/app/app.routes.ts`:
  - Redirect `/visualizer` to `/workcell`.
  - Ensure `/workcell` loads the new `WorkcellDashboardComponent`.
- Update Navigation Menu (e.g., `NavDrawerComponent`):
  - Point the relevant link to `/workcell`.
- Deprecate/Remove:
  - Old `VisualizerComponent` and its routes.

**Backend/Services:**

- None.

**Data Flow:**

- Routing changes only.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `src/app/app.routes.ts` | Main routing config |
| `src/app/core/components/nav-drawer/` | Navigation menu |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `.agents/artifacts/workcell_implementation_plan.md` | Plan reference |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Safety**: Ensure no broken links remain.
- **Linting**: Run `eslint` or equivalent before committing.

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors.
2. The following tests pass:

   ```bash
   npm run test -- app.routes
   ```

3. Clicking "Workcell" acts as expected.
4. Old `/visualizer` URL redirects to `/workcell`.

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
