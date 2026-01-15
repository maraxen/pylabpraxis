# Agent Prompt: Machine Simulation Architecture Inspection


**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Hard
**Dependencies:** None
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Inspect the current machine simulation implementation and design a new architecture that supports "Configurable Backends" on the fly, establishing a general principle for the application where specific backend configurations are traits, not permanent instances.
**Problem**: Currently, `SqliteService` auto-seeds ~70 simulated machines (one per definition). This is rigid, creates inventory clutter, and fails to distinguish between a "Machine Category" and a configured "Simulated Instance".
**Goal**: Design a system where:

1. **One Simulated Entry per Category**: We expose exactly ONE "Simulated Machine" placeholder for each Machine Category (Definition) in the UI (Playground, Workcell Manager, Protocol), rather than pre-seeding 70 unique instances.
2. **Runtime Instantiation**: When a user "Adds" or "Uses" this simulated machine, they configure the backend (Simulator, Chatterbox, Serial, etc.) and its specific capabilities (e.g. specific deck type) *there and then*.
3. **Configurable Backends**: The backend is treated as a selectable trait/configuration of the machine, not a hardcoded property of a persistent instance.
4. **No Mass Seeding**: Remove the logic that auto-seeds unique asset instances for every definition.

## 2. Technical Implementation Strategy

**Inspection Phase**:

1. **Seeding Logic**: Review `praxis/web-client/src/app/core/services/sqlite.service.ts` -> `seedDefaultAssets` to identify exactly what is being seeded and how to stop it without breaking the "Available Machines" list.
2. **Backend Parity**: Review `praxis/backend/core/asset_manager/machine_manager.py` to ensure the backend supports instantiating machines with dynamic backend configurations passed from the frontend.
3. **Selection UX**: Review `praxis/web-client/src/app/features/run-protocol/components/machine-selection` and the Workcell Manager to see how they currently rely on `machine_id` vs `machine_definition_id`, and how to shift this to "Select Definition -> Configure Backend -> Instantiate Ephemeral/Persistent Machine".
4. **Data Structure**: Inspect `praxis/backend/models/domain/machine.py` to see how we can model "SimulatedBackend" as a configuration object rather than a machine type.

**Output Generation**:

- Create/Update `references/machine_sim_audit.md` detailing:
  - Analysis of the current `SqliteService` seeding.
  - Proposal for the "Factory Pattern" in the UI (selecting a definition to spawn a machine).
  - Backend requirements to support `machine_definition + backend_config` instantiation.

## 3. Context & References

**Relevant Skills**:

- `senior-architect` (Use for analyzing the backend/frontend split)
- `backend-dev-guidelines` (Ensure Python backend correctness)

**Primary Files to Inspect**:

| Path | Description |
| :--- | :--- |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | Machine Seeding Logic |
| `praxis/backend/models/domain/machine.py` | Machine Data Model |
| `praxis/web-client/src/app/features/assets/components/device-registration-dialog` | Device Registration UX |
| `praxis/backend/core/workcell_runtime/machine_manager.py` | Backend Runtime Instantiation |

## 4. Constraints & Conventions

- **Do Not Implement**: This is an INSPECTION task (Type I).
- **No Code Changes**: Do not modify code. Only read and log.
- **Output**: `references/machine_sim_audit.md` artifact.

## 5. Verification Plan

**Definition of Done**:

1. `references/machine_sim_audit.md` exists and contains detailed analysis of the shift from "Seeded Instances" to "Factory Configuration".
2. Prompt `01_machine_simulation_architecture_P.md` is queued for creation.

---

## On Completion

- [ ] Create `01_machine_simulation_architecture_P.md` (Type P) based on findings
- [ ] Mark this prompt complete in batch README and set status to ✅ Completed
