# Simulation Architecture Redesign

## Problem Statement

Currently, the system discovers ~73 simulated backends (one for every PLR machine type) and potentially exposes them as separate `MachineDefinition` entries. This floods the UI. We want:

1. **One Simulated Frontend per Category** - Generic entries like "Simulated Liquid Handler"
2. **Runtime Backend Selection** - User chooses simulation backend (e.g., `ChatterboxBackend`) at instantiation
3. **Persisted Selection** - Selected backend stored with Machine instance

---

## Current State Audit

### Backend Discovery (`class_discovery.py`)

| Category | Backend Type Enum | Frontend FQN | Simulated Backends |
|:---------|:------------------|:-------------|:-------------------|
| Liquid Handler | `LH_BACKEND` | `pylabrobot.liquid_handling.LiquidHandler` | ChatterboxBackend, LiquidHandlerChatterboxBackend |
| Plate Reader | `PR_BACKEND` | `pylabrobot.plate_reading.PlateReader` | (Chatterbox variant) |
| Heater Shaker | `HS_BACKEND` | `pylabrobot.heating_shaking.HeaterShaker` | (Chatterbox variant) |
| Shaker | `SHAKER_BACKEND` | `pylabrobot.shaking.Shaker` | (Chatterbox variant) |
| Temperature Controller | `TEMP_BACKEND` | `pylabrobot.temperature_controlling.TemperatureController` | (Chatterbox variant) |
| Centrifuge | `CENTRIFUGE_BACKEND` | `pylabrobot.centrifuging.Centrifuge` | (Chatterbox variant) |
| Thermocycler | `THERMOCYCLER_BACKEND` | `pylabrobot.thermocycling.Thermocycler` | (Chatterbox variant) |
| Pump | `PUMP_BACKEND` | `pylabrobot.pumping.Pump` | (Chatterbox variant) |
| Pump Array | `PUMP_ARRAY_BACKEND` | `pylabrobot.pumping.PumpArray` | (Chatterbox variant) |
| Fan | `FAN_BACKEND` | `pylabrobot.fans.Fan` | (Chatterbox variant) |
| Plate Sealer | `SEALER_BACKEND` | `pylabrobot.plate_sealing.Sealer` | (Chatterbox variant) |
| Plate Peeler | `PEELER_BACKEND` | `pylabrobot.plate_peeling.Peeler` | (Chatterbox variant) |
| Powder Dispenser | `POWDER_DISPENSER_BACKEND` | `pylabrobot.powder_dispensing.PowderDispenser` | (Chatterbox variant) |
| Incubator | `INCUBATOR_BACKEND` | `pylabrobot.incubating.Incubator` | (Chatterbox variant) |
| SCARA Robot | `SCARA_BACKEND` | `pylabrobot.scara.SCARA` | (Chatterbox variant) |

### Schema (`machine.py`)

**Existing Fields (already in place):**

- `MachineDefinition.frontend_fqn` - Links backend to its frontend class
- `MachineDefinition.compatible_backends` - JSON list of compatible backend FQNs

**Machine Instance:**

- `Machine.connection_info` - JSON containing `backend_fqn` when hardware selected

### Frontend (`machine-dialog.component.ts`)

**Current 3-Step Flow:**

1. **Step 1: Machine Type** - Card grid of frontend types (Liquid Handler, Plate Reader, etc.)
2. **Step 2: Backend** - Filtered list of `MachineDefinition` entries with matching `frontend_fqn`
3. **Step 3: Configuration** - Name, location, capabilities, connection info

---

## Proposed Changes

### Phase 1: Backend Changes

#### 1.1 Add Simulated Frontend Definitions

Create synthetic `MachineDefinition` entries for each frontend type that:

- Have `is_simulated_frontend = True` (new field)
- Have `compatible_simulated_backends` - list of all simulated backend FQNs for this category

#### [MODIFY] [machine.py](file:///Users/mar/Projects/pylabpraxis/praxis/backend/models/domain/machine.py)

Add fields to `MachineDefinitionBase`:

```python
is_simulated_frontend: bool | None = Field(
    default=None, 
    description="True if this is a generic simulated frontend (not a real backend)"
)
available_simulation_backends: list[str] | None = Field(
    default=None, 
    sa_type=JsonVariant, 
    description="FQNs of simulation backends available for this frontend type"
)
```

Add field to `MachineBase`:

```python
simulation_backend_fqn: str | None = Field(
    default=None, 
    description="Selected simulation backend FQN (when is_simulated_frontend = True)"
)
```

#### 1.2 Update Discovery Service

#### [MODIFY] [machine_type_definition.py](file:///Users/mar/Projects/pylabpraxis/praxis/backend/services/machine_type_definition.py)

Update `discover_and_synchronize_type_definitions()`:

```python
async def discover_and_synchronize_type_definitions(self) -> list[MachineDefinition]:
    # ... existing discovery ...
    
    # Group simulated backends by frontend type
    simulated_by_frontend: dict[str, list[DiscoveredClass]] = {}
    non_simulated: list[DiscoveredClass] = []
    
    for cls in all_discovered:
        if cls.is_simulated():
            frontend_fqn = BACKEND_TYPE_TO_FRONTEND_FQN.get(cls.class_type)
            if frontend_fqn:
                simulated_by_frontend.setdefault(frontend_fqn, []).append(cls)
        else:
            non_simulated.append(cls)
    
    # Upsert non-simulated backends as before
    for cls in non_simulated:
        await self._upsert_definition(cls)
    
    # Create ONE simulated frontend per category
    for frontend_fqn, sim_backends in simulated_by_frontend.items():
        await self._upsert_simulated_frontend(frontend_fqn, sim_backends)
```

New method:

```python
async def _upsert_simulated_frontend(
    self, 
    frontend_fqn: str, 
    sim_backends: list[DiscoveredClass]
) -> MachineDefinition:
    """Create/update a single simulated frontend definition for a category."""
    # Generate name like "Simulated Liquid Handler"
    category_name = frontend_fqn.split(".")[-1]  # LiquidHandler
    name = f"Simulated {category_name}"
    fqn = f"praxis.simulated.{category_name}"
    
    backend_fqns = [cls.fqn for cls in sim_backends]
    
    # Check for existing
    existing = await self.db.execute(
        select(MachineDefinition).filter(MachineDefinition.fqn == fqn)
    )
    existing_def = existing.scalar_one_or_none()
    
    if existing_def:
        existing_def.available_simulation_backends = backend_fqns
        existing_def.is_simulated_frontend = True
        return existing_def
    
    # Create new
    new_def = MachineDefinition(
        name=name,
        fqn=fqn,
        frontend_fqn=frontend_fqn,
        is_simulated_frontend=True,
        available_simulation_backends=backend_fqns, # Keep FQNs here for unambiguous loading
        description=f"Simulated {category_name} - select backend at instantiation"
    )
    self.db.add(new_def)
    return new_def
```

---

### Phase 2: Frontend Changes

#### [MODIFY] [machine-dialog.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts)

**Step 2 Enhancement:**

When user selects a simulated frontend (`def.is_simulated_frontend === true`), show a secondary dropdown:

```typescript
// In template, after backend selection
@if (selectedDefinition?.is_simulated_frontend && simulationBackends.length > 0) {
  <div class="section-card mt-4">
    <div class="section-header">Simulation Backend</div>
    <p class="text-sm sys-text-secondary mb-3">
      Choose the simulation implementation for this {{ getSelectedFrontendLabel() }}.
    </p>
    <app-praxis-select
      placeholder="Select Simulation Backend"
      [options]="simulationBackendOptions"
      [(ngModel)]="selectedSimulationBackend">
    </app-praxis-select>
  </div>
}
```

**Component Logic:**

```typescript
simulationBackends: string[] = []; // List of FQNs from definition
selectedSimulationBackend: string | null = null; // Stores SHORT NAME (e.g. 'chatterbox')

selectBackend(def: MachineDefinition) {
  this.selectedDefinition = def;
  
  if (def.is_simulated_frontend && def.available_simulation_backends) {
    this.simulationBackends = def.available_simulation_backends;
    // Default to 'chatterbox' if available, else first one
    const shortNames = this.simulationBackends.map(this.toShortName);
    this.selectedSimulationBackend = shortNames.includes('chatterbox') ? 'chatterbox' : shortNames[0];
  } else {
    this.simulationBackends = [];
    this.selectedSimulationBackend = null;
  }
}

// Helper to convert FQN to short name for storage
toShortName(fqn: string): string {
    if (fqn.toLowerCase().includes('chatterbox')) return 'chatterbox';
    if (fqn.toLowerCase().includes('simulator')) return 'simulator';
    return 'demo'; // Fallback
}

save() {
  // Include simulation_backend_name in payload
  this.dialogRef.close({
    ...value,
    simulation_backend_name: this.selectedSimulationBackend,
    // ...
  });
}
```

**Backend Display Names:**

For better UX, parse backend FQNs to human-readable names:

```typescript
get simulationBackendOptions(): SelectOption[] {
  return this.simulationBackends.map(fqn => ({
    value: this.toShortName(fqn), // Use short name as value
    label: this.formatBackendName(fqn) // "ChatterboxBackend" → "Chatterbox"
  }));
}

formatBackendName(fqn: string): string {
  const name = fqn.split('.').pop() || fqn;
  return name.replace(/Backend$/, '').replace(/([A-Z])/g, ' $1').trim();
}
```

---

### Phase 3: API Schema Updates

#### [MODIFY] [machine.py](file:///Users/mar/Projects/pylabpraxis/praxis/backend/models/domain/machine.py)

**MachineCreate:**

```python
class MachineCreate(MachineBase):
    simulation_backend_name: str | None = None  # Add this
    # ... existing fields
```

**MachineRead:**

```python
class MachineRead(AssetRead, MachineBase):
    simulation_backend_name: str | None = None  # Add this
```

---

### Phase 4: Browser Mode Support

#### [MODIFY] [machines.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/assets/browser-data/machines.ts)

Update mock machine definitions to include new fields:

```typescript
export const MOCK_MACHINE_DEFINITIONS = [
  {
    accession_id: 'simdef-001',
    name: 'Simulated Liquid Handler',
    fqn: 'praxis.simulated.LiquidHandler',
    frontend_fqn: 'pylabrobot.liquid_handling.LiquidHandler',
    is_simulated_frontend: true,
    available_simulation_backends: [
      'pylabrobot.liquid_handling.backends.ChatterboxBackend',
      'pylabrobot.liquid_handling.backends.LiquidHandlerChatterboxBackend'
    ]
  },
  // ... one per category
];
```

---

### Phase 5: Migration (CRITICAL)

**Migration Script Logic:**

1. **Iterate** all `machines` where `is_simulation_override` is True.
2. **Inspect** `connection_info` JSON for `backend_fqn`.
3. **Map** the legacy FQN to a short name:
    - `*ChatterboxBackend*` -> `chatterbox`
    - `*Simulator*` -> `simulator`
4. **Update** `machine.simulation_backend_name` with the short name.
5. **Lookup** the new "Simulated X" `MachineDefinition` for the machine's category.
6. **Update** `machine.machine_definition_accession_id` to point to this new generic definition.

**Testing the Migration:**

- Create a unit test `tests/migrations/test_simulation_migration.py`.
- Seed DB with "old style" simulated machines (linked to specific simulated definitions).
- Run migration function.
- Assert machines are now linked to generic definitions and have `simulation_backend_name` set.

---

## User Review Required

> **Backend Naming Convention**: The plan uses FQNs (e.g., `pylabrobot.liquid_handling.backends.ChatterboxBackend`) for simulation backend storage. Alternative: use short names like `chatterbox`.

> [!WARNING]
> **Breaking Change**: Existing simulated machines will need migration. A database migration script is required.

---

## Verification Plan

### Automated Tests

1. **Backend Discovery Test**:

   ```bash
   cd /Users/mar/Projects/pylabpraxis
   uv run pytest praxis/backend/services/test_machine_type_definition.py -v
   ```

   - Verify simulated frontends are created (one per category)
   - Verify `available_simulation_backends` is populated

2. **Schema Validation**:

   ```bash
   cd /Users/mar/Projects/pylabpraxis
   uv run pytest praxis/backend/models/domain/test_machine.py -v
   ```

### Manual Verification

1. **Start backend and sync definitions**:

   ```bash
   curl -X POST http://localhost:8000/api/v1/discovery/sync-all
   ```

   - Verify response contains exactly 15 simulated frontends
   - Verify each has `available_simulation_backends` list

2. **Frontend UI Test** (Browser Mode):
   - Open Add Machine dialog
   - Select "Simulated Liquid Handler"
   - Verify secondary dropdown appears with backend options
   - Complete form and verify machine is created with `simulation_backend_fqn`

---

## Files Affected Summary

| File | Change Type |
|:-----|:------------|
| `praxis/backend/models/domain/machine.py` | Add 3 new fields |
| `praxis/backend/services/machine_type_definition.py` | New grouping logic |
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Add backend picker |
| `praxis/web-client/src/assets/browser-data/machines.ts` | Update mock data |
| `praxis/backend/alembic/versions/xxx_simulation_backend.py` | New migration |
