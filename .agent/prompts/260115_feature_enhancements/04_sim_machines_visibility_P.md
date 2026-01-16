# Agent Prompt: Simulation Machine Visibility - Planning

**Status:** ⚪ Queued
**Priority:** P1
**Batch:** [260115_feature_enhancements](./README.md)
**Difficulty:** Hard
**Dependencies:** `04_sim_machines_visibility_I.md`, `references/sim_machines_visibility_audit.md`
**Backlog Reference:** Previous `01_machine_simulation_architecture` work

---

## 1. The Task

**Objective**: Plan the implementation to make simulation machines frontend-only placeholders until user instantiation, fix inventory display, and align deck definitions properly.

**Context**: Inspection phase identified the source of backend leakage and deck definition misalignment.

**Goal**: Design a solution for:

1. **Frontend-Only Placeholders**: Simulation machines exist only as definitions until instantiated.
2. **Clean Inventory Display**: Show simulated machines as "virtual" entries, distinct from real machines.
3. **Deferred Instantiation**: Machine is created only when user explicitly adds it (Protocol setup, Playground).
4. **Deck Definition Alignment**: Map deck definitions to appropriate liquidhandler backends.
5. **Workcell Filtering**: Reduce displayed machines to only those properly instantiated.

## 2. Technical Implementation Strategy

**Design Decisions**:

1. **Machine Definition vs Instance**:
   - `MachineDefinition`: Catalog entry (simulated or real hardware).
   - `Machine`: Actual instance with assigned backend config.
   - Simulated definitions should NOT create instances until user action.

2. **Inventory Display Strategy**:
   - Real machines: Show as normal inventory items.
   - Simulated definitions: Show as "Add Simulation" cards with definition info.
   - Visual distinction: Different styling, "Virtual" badge.

3. **Instantiation Contexts**:
   - **Inventory**: "Add Simulation" button creates instance.
   - **Protocol Setup**: Selecting simulated definition triggers config dialog.
   - **Playground**: "Add Machine" workflow with simulation config.

4. **Deck Alignment**:
   - Map each liquidhandler definition to its proper deck layout.
   - Filter workcell display to only instantiated machines.

**Output Generation**:

- Document implementation plan with component changes.
- Define the machine/definition filtering logic.

## 3. Context & References

**Relevant Skills**:

- `backend-dev-guidelines` (Data model refinement)
- `frontend-design` (Component patterns)

**Primary Files to Plan Changes**:

| Path | Planned Change |
| :--- | :--- |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | Remove backend-specific seeding |
| `praxis/web-client/src/app/core/services/machine.service.ts` | Add definition vs instance filtering |
| `praxis/web-client/src/app/features/assets/` | Update inventory display |
| `praxis/web-client/src/app/features/workcell/` | Filter to instantiated machines |
| `praxis/web-client/src/app/features/playground/` | Ensure instantiation flow works |

## 4. Constraints & Conventions

- **Do Not Execute**: This is a PLANNING task (Type P).
- **Scope**: Frontend display + instantiation flow.
- **Backward Compatibility**: Existing instantiated machines should continue to work.

## 5. Verification Plan

**Definition of Done**:

1. Machine definition vs instance model is documented.
2. Inventory display strategy is clear.
3. Instantiation flow for all contexts is planned.
4. Deck alignment strategy is defined.
5. Prompt `04_sim_machines_visibility_E.md` is ready for execution.

---

## On Completion

- [ ] Document implementation plan
- [ ] Define filtering logic
- [ ] Mark this prompt complete in batch README
- [ ] Proceed to `04_sim_machines_visibility_E.md`
