# Agent Prompt: Simulation Architecture Audit & Design

Examine `.agents/README.md` for development context.

**Status:** 🔵 Planning Complete
**Priority:** P2
**Batch:** [260114_frontend_feedback](../README.md)
**Difficulty:** 🔴 Complex
**Dependencies:** None
**Backlog Reference:** [simulation.md](../../backlog/simulation.md)

---

## 1. The Task

**Objective:**
Design a new architecture for handling simulated machines that separates the "frontend" machine definition from the "backend" simulation implementation.

**Current Problem:**
Currently, the system discovers ~73 simulated backends (one for every PLR machine type) and potentially exposes them as 73 separate machine types in the "Add Machine" dialog. This floods the user interface. We want users to select a generic "Simulated Liquid Handler" and then choose *which* simulation backend to use (e.g., Chatterbox vs. Core Simulator) at runtime.

**Target Architecture:**

- **One Simulated Frontend per Category**: The catalog should contain generic entries like "Simulated Liquid Handler", "Simulated Plate Reader".
- **Runtime Backend Selection**: When instantiating a simulated machine, the user selects the specific backend implementation (e.g., `ChatterboxBackend`).
- **Persisted Selection**: The selected backend class is stored with the Machine instance.

**Goal:**
Produce a detailed `implementation_plan.md` that audits the current state and defines the changes needed for:

1. Backend registration/discovery (grouping simulated backends).
2. Machine Definition Schema (supporting generic machine definitions).
3. Machine Instance Schema (storing the selected backend).
4. Frontend UI (`MachineDialogComponent`) for selecting the backend.

---

## 2. Technical Implementation Strategy

This is a **Planning Task**. You must investigate the codebase and produce an architecture document.

**Investigation Areas:**

1. **Backend Discovery (`class_discovery.py`)**:
    - Audit how simulated backends are currently discovered and classified.
    - Determine how to suppress them from being created as separate `MachineDefinition` entries in the catalog.
    - Determine how to group them into lists compatible with generic definitions (e.g., "All Liquid Handler Simulators").

2. **Schema (`machine.py`)**:
    - Check if `Machine` or `MachineDefinition` needs new fields to store `simulation_backend_class`.
    - Review `compatible_backends` JSON field in `MachineDefinition`.

3. **Frontend (`MachineDialogComponent`)**:
    - Audit the current add machine flow.
    - Design how the secondary dropdown for "Simulation Backend" will work.

**Deliverables:**

- **`implementation_plan.md`**: A detailed plan covering:
  - **Audit**: List of all 73 currently discovered simulated backends and their categories.
  - **Schema Changes**: Proposed SQLModel changes.
  - **API Changes**: Updates to `MachineCreate` / `MachineRead` schemas.
  - **Frontend Design**: Pseudo-code or description of the UI changes.
  - **Migration**: How to handle existing simulated machines.

---

## 3. Context & References

**Primary Files to Audit:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/utils/plr_static_analysis/visitors/class_discovery.py` | Logic for finding and classifying PLR backends. |
| `praxis/backend/models/domain/machine.py` | Database schema for machines and definitions. |
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Frontend component for adding machines (verify path). |
| `praxis/web-client/src/assets/browser-data/machines.ts` | Current browser-mode mock data. |

---

## 4. Constraints & Conventions

- **Plan First**: Do not implement changes in this step. Only design.
- **Chatterbox**: Ensure `ChatterboxBackend` is explicitly handled as a primary simulation option.
- **Browser Mode**: The design must work for both Server Mode (Python backend) and Browser Mode (static JS data).
- **Documentation**: The plan should be clear enough for a junior engineer to implement.

---

## 5. Verification Plan

**Definition of Done:**

1. `implementation_plan.md` is created in `.agents/prompts/260114_frontend_feedback/artifacts/`.
2. The plan addresses all requirements (1:1 mapping, runtime selection).
3. The plan includes a list of affected files and specific changes for each.

---

## On Completion

- [x] Commit the plan to git (if applicable/requested).
- [x] Mark this prompt as 🔵 Planning Complete.
- [ ] Generate the downstream implementation prompt `C-01_implement_simulation_arch.md`.
