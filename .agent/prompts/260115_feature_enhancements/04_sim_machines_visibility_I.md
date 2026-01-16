# Agent Prompt: Simulation Machine Visibility - Inspection

**Status:** 🔵 Ready
**Priority:** P1
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Hard
**Dependencies:** None
**Backlog Reference:** Previous `01_machine_simulation_architecture` work (archived)

---

## 1. The Task

**Objective**: Inspect why simulation machine backends are appearing in the inventory and workcell despite previous refactoring, and why the workcell shows too many machines.

**Problem**:
- Simulation machines should be **frontend-only placeholders** until user instantiates them.
- Currently, backends (Simulator, Chatterbox, etc.) are showing up in the machine inventory incorrectly.
- The workcell displays too many machines because deck definitions aren't aligned to proper liquidhandler backends.
- Users should see simulation options in: Inventory (as virtual entries), Protocol setup, and Playground (for instantiation).

**Goal**: Document:

1. **Current Machine Population**: Trace where machines in inventory come from (seeding? API? definitions?).
2. **Backend Leakage**: Identify why backend configurations are appearing as separate inventory items.
3. **Deck Definition Alignment**: Understand the mismatch between deck definitions and liquidhandler backends.
4. **Instantiation Flow**: Document current flow for Playground machine instantiation.

## 2. Technical Implementation Strategy

**Inspection Phase**:

1. **Inventory Population**:
   - Read `praxis/web-client/src/app/core/services/sqlite.service.ts` → machine seeding.
   - Read `praxis/web-client/src/app/core/services/machine.service.ts` → how machines are fetched/filtered.

2. **Backend vs Definition**:
   - Read `praxis/web-client/src/app/core/models/machine.model.ts` → understand `MachineDefinition` vs `Machine` vs backend config.
   - Read `praxis/backend/models/domain/machine.py` → backend model.

3. **Deck Alignment**:
   - Read `praxis/web-client/src/app/features/workcell/` → how deck view selects machines.
   - Identify where deck definitions are pulled from and how they map to backends.

4. **Playground Flow**:
   - Read `praxis/web-client/src/app/features/playground/` → machine instantiation logic.

**Output Generation**:

- Create `references/sim_machines_visibility_audit.md` with:
  - Machine population flow diagram
  - Source of backend leakage
  - Deck definition mapping issues
  - Proposed filtering/instantiation model

## 3. Context & References

**Relevant Skills**:

- `backend-dev-guidelines` (Backend models)
- `frontend-design` (Angular services)

**Primary Files to Inspect**:

| Path | Description |
| :--- | :--- |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | Machine seeding |
| `praxis/web-client/src/app/core/services/machine.service.ts` | Machine data access |
| `praxis/web-client/src/app/features/workcell/` | Workcell deck view |
| `praxis/web-client/src/app/features/playground/` | Playground instantiation |
| `praxis/backend/models/domain/machine.py` | Backend machine model |

## 4. Constraints & Conventions

- **Do Not Implement**: This is an INSPECTION task (Type I).
- **Scope**: Frontend simulation visibility + backend alignment.
- **Note**: This is a continuation of previous machine simulation architecture work.

## 5. Verification Plan

**Definition of Done**:

1. `references/sim_machines_visibility_audit.md` documents the source of unwanted machines.
2. Deck definition alignment issue is understood.
3. Instantiation flow for all contexts (Inventory, Protocol, Playground) is documented.
4. Prompt `04_sim_machines_visibility_P.md` is ready to proceed.

---

## On Completion

- [ ] Create `references/sim_machines_visibility_audit.md`
- [ ] Mark this prompt complete in batch README
- [ ] Proceed to `04_sim_machines_visibility_P.md`
