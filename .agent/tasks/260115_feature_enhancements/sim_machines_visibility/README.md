# Task: Simulation Machine Visibility

**ID**: FE-04
**Status**: ⚪ Not Started
**Priority**: P1
**Difficulty**: Hard

---

## 📋 Phase 1: Inspection (I)

**Objective**: Understand why simulation machine backends appear in inventory and workcell incorrectly.

- [ ] Trace machine population in `praxis/web-client/src/app/core/services/sqlite.service.ts`
- [ ] Review `praxis/web-client/src/app/core/services/machine.service.ts` filtering
- [ ] Understand `MachineDefinition` vs `Machine` vs backend config in models
- [ ] Check deck definition mapping in workcell component
- [ ] Review Playground instantiation flow

**Findings**:
> - Source of unwanted machines in inventory
> - Backend leakage mechanism
> - Deck definition alignment issues
> - Current instantiation flow gaps

---

## 📐 Phase 2: Planning (P)

**Objective**: Design frontend-only simulation placeholders with deferred instantiation.

- [ ] Define machine definition vs instance model
- [ ] Plan inventory display strategy (virtual entries)
- [ ] Design instantiation flow for all contexts
- [ ] Plan deck alignment fix

**Implementation Plan**:

1. **Machine Definition vs Instance**:
   - `MachineDefinition`: Catalog entry (simulated or real)
   - `Machine`: Actual instance with backend config
   - Simulated definitions = placeholders until instantiated

2. **Inventory Display**:
   - Real machines: Normal display
   - Simulated definitions: "Add Simulation" cards with definition info
   - Visual distinction: Different styling, "Virtual" badge

3. **Instantiation Contexts**:
   - **Inventory**: "Add Simulation" button creates instance
   - **Protocol Setup**: Selecting simulated definition triggers config dialog
   - **Playground**: "Add Machine" workflow with simulation config

4. **Workcell Filtering**:
   - Display only instantiated machines
   - Align deck view to machine's actual backend config

**Definition of Done**:

1. Inventory shows simulation definitions as "Add" options
2. Workcell displays only explicitly instantiated machines
3. Backend configs don't appear as separate inventory items
4. Playground can instantiate new simulations
5. Protocol setup can select and configure simulations

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement frontend-only simulation placeholders.

- [ ] Clean up `SqliteService` - remove backend-specific seeding
- [ ] Update `MachineService`:
  ```typescript
  getSimulationDefinitions(): Observable<MachineDefinition[]>
  getInstantiatedMachines(): Observable<Machine[]>
  getWorkcellMachines(): Observable<Machine[]> // only instantiated
  ```
- [ ] Update inventory component - show "Add Simulation" cards
- [ ] Update workcell component - filter to instantiated only
- [ ] Verify Playground instantiation flow

**Work Log**:

- [Pending]

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify simulation visibility and instantiation.

- [ ] Clear local data, reload app
- [ ] Check inventory: Should see "Add Simulation" options, not 70+ machines
- [ ] Add a simulation from inventory
- [ ] Verify it appears in workcell with correct deck
- [ ] Add simulation from Playground
- [ ] Set up protocol with simulated machine

**Results**:
> [To be captured]

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Previous Work**: `01_machine_simulation_architecture` (archived)
- **Files**:
  - `praxis/web-client/src/app/core/services/sqlite.service.ts`
  - `praxis/web-client/src/app/core/services/machine.service.ts`
  - `praxis/web-client/src/app/features/workcell/`
  - `praxis/web-client/src/app/features/playground/`
  - `praxis/web-client/src/app/features/assets/`
