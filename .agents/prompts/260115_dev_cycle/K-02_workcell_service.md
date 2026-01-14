# Agent Prompt: Workcell View Service

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P1
**Batch:** [260115](README.md)
**Difficulty:** Medium
**Dependencies:** K-01_workcell_models.md
**Backlog Reference:** WCX-001-IMPL (P0.2)

---

## 1. The Task

Create or extend services for workcell data access as defined in Phase 0.2 of the [Workcell Implementation Plan](../artifacts/workcell_implementation_plan.md). This service will act as the data layer for the dashboard.

## 2. Technical Implementation Strategy

**(From workcell_implementation_plan.md)**

**Frontend Components:**

- Create `src/app/features/workcell/services/workcell-view.service.ts`.
- Implement signal-based state management:
  - `workcellGroups = signal<WorkcellGroup[]>([])`
  - `selectedMachine = signal<MachineWithRuntime | null>(null)`

**Backend/Services:**

- Extend `AssetService` (`src/app/features/assets/services/asset.service.ts`) to include `getWorkcells()` if missing.
- Implement data transformation logic in `WorkcellViewService`:
  - Use `forkJoin` to fetch machines and workcells.
  - Map results to `WorkcellGroup[]` structure.
  - Handle "Unassigned" machines (machines with null `workcell_id`).

**Data Flow:**

1. Component calls `WorkcellViewService.loadWorkcellGroups()`.
2. Service fetches raw data from `AssetService`.
3. Service transforms data into `WorkcellGroup` hierarchy.
4. Signals are updated, triggering UI updates.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `src/app/features/workcell/services/workcell-view.service.ts` | New service for workcell logic |
| `src/app/features/assets/services/asset.service.ts` | Existing service to extend |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `.agents/artifacts/workcell_implementation_plan.md` | Implementation plan source |
| `.agents/prompts/260115_dev_cycle/K-01_workcell_models.md` | Model definitions |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **State**: Use Angular Signals (`signal`, `computed`).
- **Linting**: Run `eslint` or equivalent before committing.

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors.
2. The following tests pass:

   ```bash
   npm run test -- workcell-view.service
   ```

3. Service correctly groups machines by workcell in unit tests.
4. "Unassigned" machines are handled gracefully.

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
