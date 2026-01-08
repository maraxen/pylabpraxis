# Prompt 1: PLR Frontend/Backend Schema (COMPLETED)

**Priority**: P1
**Difficulty**: Large
**Type**: Complex Architecture Change

> **IMPORTANT**: Do NOT use the browser agent. Verify with automated tests only.

---

## Context

Currently, `MachineDefinitionOrm` stores only the backend FQN (e.g., `pylabrobot.plate_reading.clario_star_backend.CLARIOstarBackend`), but the REPL and protocol execution need to know the paired frontend class (e.g., `pylabrobot.plate_reading.PlateReader`).

The CST analysis already classifies classes into `PLRClassType.LH_BACKEND`, `PLRClassType.PR_BACKEND`, etc., which directly maps to frontend types.

---

## Tasks

### 1. Add Frontend FQN to Schema

Update `MachineDefinitionOrm` in `praxis/backend/models/orm/machine.py`:

```python
class MachineDefinitionOrm(Base):
    # Existing fields...
    fqn: Mapped[str]  # This is the BACKEND fqn
    
    # NEW: Add frontend FQN
    frontend_fqn: Mapped[str | None] = mapped_column(String(512), nullable=True)
```

### 2. Create Backend-to-Frontend Map

In `praxis/backend/utils/plr_static_analysis/models.py`, add:

```python
BACKEND_TYPE_TO_FRONTEND_FQN: dict[PLRClassType, str] = {
    PLRClassType.LH_BACKEND: "pylabrobot.liquid_handling.LiquidHandler",
    PLRClassType.PR_BACKEND: "pylabrobot.plate_reading.PlateReader",
    PLRClassType.HS_BACKEND: "pylabrobot.heating_shaking.HeaterShaker",
    PLRClassType.SHAKER_BACKEND: "pylabrobot.shaking.Shaker",
    PLRClassType.TEMP_BACKEND: "pylabrobot.temperature_controlling.TemperatureController",
    PLRClassType.CENTRIFUGE_BACKEND: "pylabrobot.centrifuging.Centrifuge",
    PLRClassType.THERMOCYCLER_BACKEND: "pylabrobot.thermocycling.Thermocycler",
    PLRClassType.PUMP_BACKEND: "pylabrobot.pumping.Pump",
    PLRClassType.PUMP_ARRAY_BACKEND: "pylabrobot.pumping.PumpArray",
    PLRClassType.FAN_BACKEND: "pylabrobot.fans.Fan",
    PLRClassType.SEALER_BACKEND: "pylabrobot.sealing.Sealer",
    PLRClassType.PEELER_BACKEND: "pylabrobot.peeling.Peeler",
    PLRClassType.POWDER_DISPENSER_BACKEND: "pylabrobot.powder_dispensing.PowderDispenser",
    PLRClassType.INCUBATOR_BACKEND: "pylabrobot.incubating.Incubator",
    PLRClassType.SCARA_BACKEND: "pylabrobot.scara.SCARA",
}
```

> **NOTE**: Verify these import paths against actual PLR source code!

### 3. Update `_upsert_definition` in MachineTypeDefinitionService

In `praxis/backend/services/machine_type_definition.py`:

```python
async def _upsert_definition(self, cls: DiscoveredClass) -> MachineDefinitionOrm:
    # ...existing code...
    
    # NEW: Determine frontend FQN from class_type
    frontend_fqn = BACKEND_TYPE_TO_FRONTEND_FQN.get(cls.class_type)
    
    if existing_def:
        # Add to update
        existing_def.frontend_fqn = frontend_fqn
        # ...
    else:
        # Add to create
        new_def = MachineDefinitionOrm(
            # ...existing fields...
            frontend_fqn=frontend_fqn,
        )
```

### 4. Update Pydantic Models

In `praxis/backend/models/pydantic_internals/machine.py`:

```python
class MachineDefinitionBase(BaseModel):
    # ...existing...
    frontend_fqn: str | None = None

class MachineDefinitionCreate(MachineDefinitionBase):
    # includes frontend_fqn

class MachineDefinitionUpdate(BaseModel):
    frontend_fqn: str | None = None
    # ...
```

### 5. Regenerate Browser Schema

```bash
uv run scripts/generate_browser_schema.py
uv run scripts/generate_browser_db.py
```

### 6. Update Frontend (TypeScript)

In `praxis/web-client/src/assets/demo-data/plr-definitions.ts`:

```typescript
export interface MachineDefinition {
  // ...existing...
  frontend_fqn?: string;
}
```

### 7. Update REPL Code Generation

In `jupyterlite-repl.component.ts`, update `generateMachineCode()` to use `frontend_fqn` instead of inferring from `machine_category`:

```typescript
private generateMachineCode(machine: Machine): string {
  const frontendFqn = machine.definition?.frontend_fqn;
  const backendFqn = machine.definition?.fqn;
  
  if (!frontendFqn || !backendFqn) {
    // Fallback to current logic
  }
  
  const frontendClass = frontendFqn.split('.').pop();
  const backendClass = backendFqn.split('.').pop();
  const frontendModule = frontendFqn.substring(0, frontendFqn.lastIndexOf('.'));
  const backendModule = backendFqn.substring(0, backendFqn.lastIndexOf('.'));
  
  return `from ${frontendModule} import ${frontendClass}
from ${backendModule} import ${backendClass}
# ... rest of code gen
`;
}
```

---

## Verification

1. Run backend tests:

   ```bash
   uv run pytest tests/services/test_machine_type_definition.py -v
   ```

2. Verify PLR definitions sync:

   ```bash
   uv run python -c "from praxis.backend.utils.plr_static_analysis.models import BACKEND_TYPE_TO_FRONTEND_FQN; print(BACKEND_TYPE_TO_FRONTEND_FQN)"
   ```

3. Run frontend tests:

   ```bash
   cd praxis/web-client && npm test -- --include='**/jupyterlite-repl*'
   ```

---

## Success Criteria

- [x] `MachineDefinitionOrm` has `frontend_fqn` column
- [x] CST discovery populates `frontend_fqn` for all backend types
- [x] Browser schema regenerated
- [x] REPL uses `frontend_fqn` for code generation
- [x] All existing tests pass
