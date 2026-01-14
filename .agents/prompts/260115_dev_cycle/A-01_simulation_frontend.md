# Agent Prompt: Simulation Frontend Consolidation

Examine `.agents/README.md` for development context.

**Status**: Resolved
**Closed**: 2026-01-14
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Hard  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section A, [simulation_architecture_plan.md](../../artifacts/simulation_architecture_plan.md)

## 0. Status Details

### Investigation

- [x] Audit all simulated backend implementations
- [x] Document what each simulated frontend/backend pair does
- [x] Identify which use ChatterboxBackend vs other approaches

### Cleanup

- [x] Remove all "demo" naming from simulated frontends
- [x] Use consistent "Simulated" prefix
- [x] Document simulation behavior in code comments

### Architecture

- [x] Clarify frontend/backend separation in simulation
- [x] Consider singleton pattern for simulated frontends per category
- [x] Document simulation architecture for developers

---

## 1. The Task

Consolidate ~70 simulated backends into ONE simulated frontend definition per frontend type. Backend selection will happen at instantiation time in protocols/playground.

**User Value:** Cleaner machine selection UI; no overwhelming list of simulated backends.

**Specified Requirements:**

- One simulated frontend per type (LiquidHandler, PlateReader, etc.) - approximately 15 total
- Backend type selected at instantiation (protocols or playground)
- Backend-specific config available when needed
- Display: Short names (`chatterbox`), FQNs on hover or as animated ticker

## 2. Technical Implementation Strategy

**Backend Changes:**

### [MODIFY] `praxis/backend/models/domain/machine.py`

Add to `MachineDefinitionBase`:

```python
is_simulated_frontend: bool | None = Field(default=None)
available_simulation_backends: list[str] | None = Field(default=None, sa_type=JsonVariant)
```

Add to `MachineBase`:

```python
simulation_backend_name: str | None = Field(default=None)
```

### [MODIFY] `praxis/backend/services/machine_type_definition.py`

Update `discover_and_synchronize_type_definitions()`:

- Group simulated backends by frontend type
- Create ONE synthetic `MachineDefinition` per frontend category
- Store backend FQNs in `available_simulation_backends`

**Frontend Changes:**

### [MODIFY] `machine-dialog.component.ts`

- When `selectedDefinition?.is_simulated_frontend === true`, show secondary dropdown
- Populate with `available_simulation_backends`
- Default to `chatterbox` if available
- Store selection in `simulation_backend_name`

### [MODIFY] `browser-data/machines.ts`

Update mock machine definitions with new fields.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
| :--- | :--- |
| `praxis/backend/models/domain/machine.py` | Add 3 new fields |
| `praxis/backend/services/machine_type_definition.py` | Grouping logic |
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Backend picker |
| `praxis/web-client/src/assets/browser-data/machines.ts` | Mock data |

**Reference Files:**

| Path | Description |
| :--- | :--- |
| `.agents/artifacts/simulation_architecture_plan.md` | Full design spec |

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python, `npm` for Angular.
- **Backend Path**: `praxis/backend`
- **Frontend Path**: `praxis/web-client`
- **Short Names**: `chatterbox`, `simulator`, `demo`
- **Linting**: Run `uv run ruff check .` before committing.

## 5. Verification Plan

**Definition of Done:**

1. Backend sync creates ~15 simulated frontends (one per category)
2. Machine dialog shows backend picker when simulated frontend selected
3. Mock data updated for browser mode
4. Existing tests pass:

```bash
cd /Users/mar/Projects/pylabpraxis
uv run pytest praxis/backend/services/ -v -k "machine_type"
```

**Manual Verification:**

1. Run `curl -X POST http://localhost:8000/api/v1/discovery/sync-all`
2. Verify response shows ~15 simulated frontends
3. Open Add Machine dialog in browser mode
4. Select "Simulated Liquid Handler"
5. Verify backend dropdown appears

---

## On Completion

- [x] Commit changes
- [x] Update DEVELOPMENT_MATRIX.md
- [x] Mark this prompt complete

---

## References

- `.agents/artifacts/simulation_architecture_plan.md` - Full design
- `.agents/README.md` - Environment overview
