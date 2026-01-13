# Agent Prompt: Implement Simulation Architecture

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260114_frontend_feedback](../README.md)
**Difficulty:** 🔴 Complex
**Dependencies:** None
**Backlog Reference:** [simulation.md](../../backlog/simulation.md)

---

## 1. The Task

**Objective:**
Implement the approved new simulation architecture that separates "frontend" machine definitions from "backend" simulation implementations. This involves database schema changes, updated discovery logic, and frontend UI changes.

**Plan Reference:**
You MUST follow the detailed plan at:
`.agents/prompts/260114_frontend_feedback/artifacts/simulation_architecture_plan.md`

**Core Changes:**

1. **Schema:** Add `is_simulated_frontend` and `available_simulation_backends` to `MachineDefinition`. Add `simulation_backend_name` to `Machine`.
2. **Discovery:** Update `MachineTypeDefinitionService` to deduplicate simulated backends into single per-category frontend definitions.
3. **Frontend:** Update `MachineDialogComponent` to handle backend selection for simulated types.
4. **Migration:** Write and run a migration to convert existing simulated machines to the new structure.

---

## 2. Technical Implementation Strategy

### Phase 1: Models & Schema

- Modify `praxis/backend/models/domain/machine.py` to add new fields.
- Update `MachineDefinitionBase`, `MachineDefinition`, `MachineBase`, `Machine`.
- **Constraint**: Use `simulation_backend_name` (short name like 'chatterbox') instead of FQN for storage.

### Phase 2: Discovery Service

- Modify `praxis/backend/services/machine_type_definition.py`.
- Implement the `_upsert_simulated_frontend` method as described in the plan.
- Ensure only ONE simulated frontend definition is created per machine category.
- Populate `available_simulation_backends` with the list of discovered backend FQNs.

### Phase 3: Frontend

- Modify `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts`.
- Update logic to detect `is_simulated_frontend`.
- Add secondary dropdown for simulation backend selection.
- Update `machines.ts` mock data to support browser mode.

### Phase 4: Migration & Testing

- Create a migration script (or logic within the service startup if safe) to migrate existing machines.
- **Requirement**: Create a dedicated test `tests/migrations/test_simulation_migration.py` to verify the migration logic BEFORE applying it.
- **Verification**: Ensure all existing simulated machines still load and function after migration.

---

## 3. Context & References

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/machine.py` | Core schema file. |
| `praxis/backend/services/machine_type_definition.py` | Discovery logic location. |
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Frontend dialog to update. |
| `.agents/prompts/260114_frontend_feedback/artifacts/simulation_architecture_plan.md` | **The Master Plan**. |

---

## 4. Verification Plan

**Definition of Done:**

1. `MachineDefinition` table has new columns.
2. Discovery phase logs show generic simulated frontends being created (e.g., "Simulated Liquid Handler").
3. "Add Machine" dialog allows selecting "Simulated Liquid Handler" -> "Chatterbox".
4. Created machine has `simulation_backend_name='chatterbox'` in DB.
5. Legacy simulated machines are successfully migrated.

---

## On Completion

- [ ] Run backend tests: `uv run pytest praxis/backend/services/test_machine_type_definition.py`
- [ ] Run frontend tests: `npm test -- --include '**/machine-dialog.component.spec.ts'`
- [ ] Mark this prompt as ✅ Complete in the batch README.
