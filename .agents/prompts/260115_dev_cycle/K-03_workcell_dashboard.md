# Agent Prompt: Workcell Dashboard Container

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260115](README.md)
**Difficulty:** Medium
**Dependencies:** K-02_workcell_service.md
**Backlog Reference:** WCX-001-IMPL (P1.1)

---

## 1. The Task

Create the main container component for the Workcell Dashboard as defined in Phase 1.1 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This provides the layout shell for the feature.

## 2. Technical Implementation Strategy

**(From workcell_implementation_plan.md)**

**Frontend Components:**

- Generate `src/app/features/workcell/workcell-dashboard/` with:
  - `workcell-dashboard.component.ts`
  - `workcell-dashboard.component.scss`
  - `workcell-dashboard.component.spec.ts`
- Implement Split Layout: Sidebar (280px) + Main Canvas.
- Define State: `viewMode` signal (`'grid' | 'list' | 'focus'`).
- Template Structure:
  - Sidebar placeholder (will hold Explorer).
  - Main Canvas with `@switch` for view modes.
- Route Configuration:
  - Create `src/app/features/workcell/workcell.routes.ts`.
  - Add path `'workcell'` and register in `app.routes.ts`.

**Backend/Services:**

- Consumes `WorkcellViewService` for data loading on init.

**Data Flow:**

1. Route activated -> Component initializes.
2. `ngOnInit` -> Calls `service.loadWorkcellGroups()`.
3. Template renders loading state -> then splits into Sidebar/Canvas.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `src/app/features/workcell/workcell-dashboard/workcell-dashboard.component.ts` | Main container |
| `src/app/features/workcell/workcell.routes.ts` | Routing config |
| `src/app/app.routes.ts` | Global routing registration |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `.agents/artifacts/workcell_ux_redesign.md` | Design reference |
| `.agents/prompts/260115_dev_cycle/K-02_workcell_service.md` | Service definition |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Styling**: Scoped SCSS, use tokens where possible.
- **Linting**: Run `eslint` or equivalent before committing.

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors.
2. The following tests pass:

   ```bash
   npm run test -- workcell-dashboard
   ```

3. Navigating to `/workcell` shows the basic layout structure.

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
