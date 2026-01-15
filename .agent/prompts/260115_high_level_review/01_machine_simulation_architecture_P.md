# Agent Prompt: Machine Simulation Architecture Refactor (Planning)


**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Medium
**Dependencies:** `references/machine_sim_audit.md`
**Backlog Reference:** None

---

## 1. The Task

**Objective**: Plan and design the code changes required to **Stop Machine Seeding**, **Clean Up Inventory**, and implement **Runtime Simulation Configuration**.
**Context**: The inspection phase confirmed that we currently pre-seed ~70 simulated instances. The goal is to replace this with a "Factory Pattern" where users can configure simulation traits (backend, deck type) on-the-fly during a protocol run using placeholders.

**Goal**: Create an `implementation_plan.md` that details:

1. **Removing Logic**: Modifying `SqliteService` to stop auto-seeding.
2. **Data Cleanup**: SQL migration to delete existing auto-seeded machines.
3. **UI Implementation**:
    - Injecting "Definition Placeholders" into the machine selection UI.
    - Creating a runtime configuration step for these placeholders.

## 2. Technical Implementation Strategy

**Reference Artifact**: `references/machine_sim_audit.md`, `implementation_plan.md` (in current conversation context).

**Key Components to Plan**:

- **SqliteService**: Disable loop, add cleanup SQL.
- **MachineSelectionComponent**: Add support for definition-based cards.
- **SimulationConfigDialogComponent**: New component for on-the-fly trait configuration.
- **RunProtocolComponent**: Wiring the new configuration flow.

## 3. Context & References

**Relevant Skills**:

- `backend-dev-guidelines` (Database migration/seeding logic)
- `senior-fullstack` (UI/UX for configuration flows)

## 4. Constraints & Conventions

- **Do Not Execute**: This is a PLANNING task (Type P).
- **Scope**: Includes `SqliteService` and Frontend `RunProtocol` components.

## 5. Verification Plan

**Definition of Done**:

1. `implementation_plan.md` is created and approved.
2. The plan covers logic removal, cleanup, and runtime UI.

---

## On Completion

- [ ] Create `01_machine_simulation_architecture_E.md` (Type E)
- [ ] Mark this prompt complete in batch README
