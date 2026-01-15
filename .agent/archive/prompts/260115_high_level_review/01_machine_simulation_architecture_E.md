# Agent Prompt: Machine Simulation Architecture Refactor (Execution)


**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260115_high_level_review](./README.md)
**Difficulty:** Complex
**Dependencies:** `implementation_plan.md` (approved in planning phase)

---

## 1. The Task

**Objective**: Execute the refactor to **Stop Machine Seeding**, **Clean Up Inventory**, and implement **Runtime Simulation Configuration** as detailed in the approved `implementation_plan.md`.

**Scope**:

1. **Backend Cleanup**:
    * Modify `SqliteService` to disable auto-seeding.
    * Add migration to delete existing default machines.
2. **Frontend Implementation**:
    * Create `SimulationConfigDialogComponent`.
    * Update `RunProtocolComponent` to inject "Templates" and handle their configuration.
    * Update `MachineSelectionComponent` to visually distinguish templates.

## 2. Technical Implementation Strategy

Refer to the approved `implementation_plan.md` in the conversation context.

## 3. Context & References

**Relevant Skills**:
* `backend-dev-guidelines`
* `senior-fullstack`

## 4. Constraints & Conventions

* **Type**: Execution (Type E).
* **Style**: Use Theme CSS Variables and Tailwind.

## 5. Verification Plan

Follow the Verification Plan detailed in `implementation_plan.md`.

---

## On Completion

* [ ] Mark this prompt complete in batch README
