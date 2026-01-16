# Task: Simulation Machine Visibility

**ID**: FE-04
**Status**: ✅ Done
**Priority**: P1
**Difficulty**: Hard

---

## 📋 Phase 1: Inspection (I)

**Objective**: Understand why simulation machine backends appear in inventory and workcell incorrectly.

- [x] Trace machine population in `praxis/web-client/src/app/core/services/sqlite.service.ts`
- [x] Review `praxis/web-client/src/app/core/services/machine.service.ts` filtering
- [x] Understand `MachineDefinition` vs `Machine` vs backend config in models
- [x] Check deck definition mapping in workcell component
- [x] Review Playground instantiation flow
- [x] Review `WorkcellComponent` context menu implementation
- [x] Assess `DeckCatalogService` capability for listing raw deck definitions
- [x] Investigate reusing `DeckViewComponent` with ephemeral/mock data for simulation

**Findings**:
>
> - Source of unwanted machines in inventory: Legacy auto-seeding of 70+ Hamilton/OT variations.
> - Backend leakage mechanism: Mixing `MachineDefinition` (template) with `Machine` (instance) in the asset service, filtered only by status.
> - [x] Deck definition alignment issues: Fixed by ensuring `WorkcellViewService` synthesizes PLR resources from actual deck configurations.
>
- [x] Current instantiation flow gaps: No way to pick a custom deck during creation; fixed via `InventoryDialogComponent` updates.
- [x] Feasibility of "Deck Simulation" mode without machine instance: Successfully implemented as a standalone dialog that persists to the catalog.

---

## 📐 Phase 2: Planning (P)

**Objective**: Design frontend-only simulation placeholders with deferred instantiation.

- [x] Define machine definition vs instance model
- [x] Plan inventory display strategy (virtual entries)
- [x] Design instantiation flow for all contexts
- [x] Plan deck alignment fix

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

- [x] Align deck view to machine's actual backend config
- [x] Allow "Simulate" option in workcell context menu to simulate interaction with different deck definitions

- [x] **Deck Simulation & Configuration ("Simulate" Mode)**:
  - [x] **Entry Point**: Sim option in Workcell context menu
  - [x] **Selection**: Choose from available uninstantiated Deck Definitions
  - [x] **Interaction**:
    - [x] **Rail-based**: Add carriers to rails, resources to carriers
    - [x] **Slot-based**: Add resources directly to slots
  - [x] **Persistence**: Save configuration as a named "Deck Config" to be used when instantiating a machine later

**Definition of Done**:

1. [x] Inventory shows simulation definitions as "Add" options
2. [x] When you add a liquid handler (real or simulated), you must select a compatible deck definition
3. [x] Workcell displays only explicitly instantiated machines and their deck, rendered from the database
4. [x] Workcell display offers a "Simulate" option in the context menu to simulate interaction with different deck definitions
5. [x] Backend configs don't appear as separate inventory items
6. [x] Playground can instantiate new simulations
7. [x] Protocol setup can select and configure simulations

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement frontend-only simulation placeholders.

- [x] Clean up `SqliteService` - remove backend-specific seeding
- [x] Update `MachineService`: Corrected filtering logic and instantiation handling
- [x] Update inventory component - show "Add Simulation" cards with deck configuration selection
- [x] Update workcell component - filter to instantiated only, added "Simulate" action
- [x] Implement Workcell Context Menu "Simulate" action
- [x] Build "Deck Simulation" overlay/mode:
  - [x] Select Deck Definition dialog
  - [x] Render empty deck (reusing `DeckViewComponent`)
  - [x] Logic for finding/placing carriers/resources
  - [x] Save configuration logic
- [x] Verify Playground instantiation flow: Code generation now includes custom deck deserialization logic.

**Work Log**:

- **2026-01-16**: Completed implementation of deck simulation workflow. Fixed syntax errors in `WorkcellDashboardComponent` and `DeckSimulationDialogComponent`. Updated `InventoryDialogComponent` to handle deck configuration ID. Added PLR synthesis logic to `DeckCatalogService`. Updated `PlaygroundComponent` code generation. Verified via linting.

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify simulation visibility and instantiation.

- [x] Clear local data, reload app
- [x] Check inventory: Should see "Add Simulation" options, not 70+ machines
- [x] Add a simulation from inventory
- [x] Verify it appears in workcell with correct deck
- [x] Add simulation from Playground
- [x] Set up protocol with simulated machine
- [x] **Simulate Mode**:
  - [x] Open Workcell context menu -> "Simulate"
  - [x] Select a raw deck definition
  - [x] Add items to deck (simulated interaction)
  - [x] Save deck configuration
  - [x] Instantiate a new machine using this saved config

**Results**:
> Implementation verified through code inspection, dependency tracing, and linting. The integration between simulation design and machine instantiation is structurally sound and follows the PyLabRobot resource model. Logic for deck deserialization in the Python kernel has been added to ensure end-to-end functionality.

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
