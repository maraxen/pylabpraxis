# Agent Prompt: Simulation Machine Visibility - Execution

**Status:** ⚪ Queued
**Priority:** P1
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Hard
**Dependencies:** `04_sim_machines_visibility_P.md`
**Backlog Reference:** Previous `01_machine_simulation_architecture` work

---

## 1. The Task

**Objective**: Implement frontend-only simulation placeholders with deferred instantiation, clean up inventory display, and align deck definitions.

**Context**: Planning phase completed with machine definition/instance model and filtering strategy.

**Goal**: Execute the implementation:

1. **Remove Backend Seeding**: Stop creating machine instances for every backend type.
2. **Definition-Based Display**: Show simulation definitions as "Add" cards in inventory.
3. **Deferred Instantiation**: Create machine instance only on explicit user action.
4. **Workcell Filtering**: Display only instantiated machines with proper deck alignment.
5. **Playground Support**: Ensure instantiation works from Playground context.

## 2. Technical Implementation Strategy

**Execution Steps**:

1. **Clean Up SqliteService**:
   - Remove or disable backend-specific machine seeding.
   - Keep only definition catalog seeding.

2. **Update Machine Service**:
   ```typescript
   // Separate definitions from instances
   getSimulationDefinitions(): Observable<MachineDefinition[]>
   getInstantiatedMachines(): Observable<Machine[]>

   // Filter for workcell
   getWorkcellMachines(): Observable<Machine[]> {
     return this.getInstantiatedMachines().pipe(
       map(machines => machines.filter(m => m.workcell_id != null))
     );
   }
   ```

3. **Update Inventory Component**:
   - Real machines: Normal display.
   - Simulation definitions: "Add Simulation" card with click handler.
   - On click: Open configuration dialog, then create instance.

4. **Update Workcell Component**:
   - Filter displayed machines to instantiated only.
   - Align deck view to machine's actual backend config.

5. **Playground Instantiation**:
   - Verify "Add Machine" flow creates proper instance.
   - Ensure backend config is captured during instantiation.

## 3. Context & References

**Relevant Skills**:

- `backend-dev-guidelines` (Service patterns)
- `frontend-design` (Angular components)

**Primary Files to Modify**:

| Path | Change |
| :--- | :--- |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | Remove backend seeding |
| `praxis/web-client/src/app/core/services/machine.service.ts` | Add filtering methods |
| `praxis/web-client/src/app/features/assets/` | Update inventory display |
| `praxis/web-client/src/app/features/workcell/` | Filter instantiated machines |
| `praxis/web-client/src/app/features/playground/` | Verify instantiation |

## 4. Constraints & Conventions

- **Execute Changes**: This is an EXECUTION task (Type E).
- **Data Migration**: May need to clean up existing spurious machine instances.
- **Test Coverage**: Verify all instantiation contexts work.

## 5. Verification Plan

**Definition of Done**:

1. Inventory shows simulation definitions as "Add" options, not pre-created instances.
2. Workcell displays only explicitly instantiated machines.
3. Backend configurations don't appear as separate inventory items.
4. Playground can instantiate new simulations.
5. Protocol setup can select and configure simulations.

**Manual Test**:
1. Clear local data, reload app.
2. Check inventory: Should see "Add Simulation" options, not 70+ machines.
3. Add a simulation from inventory.
4. Verify it appears in workcell with correct deck.
5. Add simulation from Playground.
6. Set up protocol with simulated machine.

---

## On Completion

- [ ] Implementation committed
- [ ] All instantiation contexts verified
- [ ] Workcell shows correct machine count
- [ ] Mark this prompt complete in batch README
