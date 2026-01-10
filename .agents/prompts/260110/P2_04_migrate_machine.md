# Agent Prompt: Migrate Machine + MachineDefinition to SQLModel

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 2.2 — Model Migration: Machine
**Parallelizable:** ❌ Sequential — Requires P2_03 (Asset base) completion

---

## 1. The Task

Unify `Machine` and `MachineDefinition` models from separate ORM and Pydantic definitions into SQLModel domain models. `Machine` inherits polymorphically from `Asset`.

**User Value:** Single source of truth for Machine schema with automatic API type generation.

---

## 2. Technical Implementation Strategy

### Current Architecture

**ORM** (`praxis/backend/models/orm/machine.py`):
- `MachineOrm(AssetOrm)` — Polymorphic child of Asset
- `MachineDefinitionOrm(PLRTypeDefinitionOrm)` — Catalog of machine types

**Key MachineOrm Fields:**
- Inherits: `asset_type`, `name`, `fqn`, `location`, `plr_state`, `plr_definition`
- Own: `status`, `machine_definition_accession_id`, `workcell_accession_id`, many JSON fields

**Key MachineDefinitionOrm Fields:**
- `machine_category`, `manufacturer`, `material`
- Dimensions: `size_x_mm`, `size_y_mm`, `size_z_mm`
- JSON: `plr_definition_details_json`, `capabilities`, `compatible_backends`, etc.
- Relationships: `deck_definition`, `resource_definition`

**Pydantic** (`praxis/backend/models/pydantic_internals/machine.py`):
- `MachineBase`, `MachineCreate`, `MachineResponse`, `MachineUpdate`
- `MachineDefinitionCreate`, `MachineDefinitionResponse`, `MachineDefinitionUpdate`

### Target Architecture

Create `praxis/backend/models/domain/machine.py`:

```python
from praxis.backend.models.domain.asset import Asset, AssetBase
from praxis.backend.models.enums import AssetType, MachineStatusEnum, MachineCategoryEnum

class MachineBase(AssetBase):
    """Shared fields for Machine CRUD schemas."""
    status: MachineStatusEnum = Field(default=MachineStatusEnum.AVAILABLE)
    machine_definition_accession_id: uuid.UUID | None = None
    workcell_accession_id: uuid.UUID | None = None

class Machine(Asset, table=True):
    """Machine ORM - polymorphic child of Asset."""
    # Note: No __tablename__ for single-table inheritance
    # Or __tablename__ = "machines" for joined-table inheritance
    
    status: MachineStatusEnum = Field(
        default=MachineStatusEnum.AVAILABLE,
        sa_column=Column(SAEnum(MachineStatusEnum)),
    )
    machine_definition_accession_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="machine_definition_catalog.accession_id",
    )
    workcell_accession_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="workcells.accession_id",
    )
    # ... additional fields
    
    __mapper_args__: ClassVar[dict] = {
        "polymorphic_identity": AssetType.MACHINE,
    }
```

### Inheritance Strategy

**Single-Table Inheritance** (current):
- All Machine columns are in `assets` table
- `asset_type` discriminator selects Machine rows
- No separate `machines` table

**Joined-Table Inheritance** (alternative):
- Machine-specific columns in `machines` table
- Join on `accession_id` to `assets`

**Verify current schema** by checking if `machines` table exists:
```sql
SELECT table_name FROM information_schema.tables WHERE table_name = 'machines';
```

---

## 3. Context & References

**Primary Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/machine.py` | Unified Machine + MachineDefinition SQLModel |

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/__init__.py` | Export Machine models |

**Files to Deprecate (Do NOT delete yet):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/orm/machine.py` | Legacy ORM |
| `praxis/backend/models/pydantic_internals/machine.py` | Legacy Pydantic |

**Reference Files (Read-Only):**

| Path | Pattern Source |
|:-----|:---------------|
| `praxis/backend/models/orm/machine.py` | Full ORM with 473 lines of fields |
| `praxis/backend/models/pydantic_internals/machine.py` | Pydantic schemas |
| `praxis/backend/models/orm/plr_sync.py` | `PLRTypeDefinitionOrm` base for definitions |
| `praxis/backend/models/enums/__init__.py` | `MachineStatusEnum`, `MachineCategoryEnum` |
| `praxis/backend/api/machines.py` | API router using both ORM and Pydantic |
| `tests/models/test_orm/test_machine_orm.py` | ORM test patterns |
| `tests/models/test_orm/test_machine_definition_orm.py` | Definition test patterns |
| `tests/models/test_pydantic/test_machine_pydantic.py` | Pydantic test patterns |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands.
- **Backend Path**: `praxis/backend`
- **Inheritance**: Match existing schema (likely single-table for Machine)
- **Do NOT change table structure** — migration handles only Python definitions

### Sharp Bits / Technical Debt

1. **Large model**: `MachineOrm` has ~50 fields. Methodically transfer all.
2. **Foreign keys**: Machine has FKs to `MachineDefinition`, `Workcell`, `Deck`, etc.
3. **Bidirectional relationships**: Ensure `back_populates` matches
4. **Nullable JSON fields**: Use `json_field()` helper consistently

---

## 5. Verification Plan

**Definition of Done:**

1. Domain model imports successfully:
   ```bash
   uv run python -c "from praxis.backend.models.domain.machine import Machine, MachineDefinition, MachineCreate, MachineRead; print('OK')"
   ```

2. Polymorphic inheritance works:
   ```bash
   uv run python -c "
   from sqlmodel import SQLModel, create_engine, Session
   from praxis.backend.models.domain.asset import Asset
   from praxis.backend.models.domain.machine import Machine
   from praxis.backend.models.enums import AssetType
   
   engine = create_engine('sqlite:///:memory:')
   SQLModel.metadata.create_all(engine)
   
   with Session(engine) as s:
       m = Machine(name='test_machine', fqn='test.Machine')
       s.add(m)
       s.commit()
       s.refresh(m)
       assert m.asset_type == AssetType.MACHINE
       print(f'Machine created with asset_type={m.asset_type}')
   "
   ```

3. Existing ORM tests still pass:
   ```bash
   uv run pytest tests/models/test_orm/test_machine_orm.py tests/models/test_orm/test_machine_definition_orm.py -x -q
   ```

4. Pydantic serialization works:
   ```bash
   uv run pytest tests/models/test_pydantic/test_machine_pydantic.py -x -q
   ```

5. New domain tests pass:
   ```bash
   uv run pytest tests/models/test_domain/test_machine_sqlmodel.py -v
   ```

---

## 6. Implementation Steps

1. **Audit existing MachineOrm fields** (all ~50):
   - Read `praxis/backend/models/orm/machine.py` completely
   - Document every field, relationship, and constraint
   - Note which fields have `JsonVariant`

2. **Audit MachineDefinitionOrm fields**:
   - Separate from PLRTypeDefinitionOrm base
   - Note dimensions, capabilities, connection_config fields

3. **Create domain/machine.py**:
   - Import `Asset` from domain.asset
   - Import enums: `AssetType`, `MachineStatusEnum`, `MachineCategoryEnum`

4. **Implement MachineDefinitionBase**:
   - Shared fields for create/read/update
   - Inherit from `PraxisBase`

5. **Implement MachineDefinition(table=True)**:
   - `__tablename__ = "machine_definition_catalog"`
   - All catalog fields with proper SQLModel annotations

6. **Implement Machine(Asset, table=True)**:
   - Polymorphic identity for `MACHINE`
   - All Machine-specific fields
   - Foreign keys and relationships

7. **Implement CRUD schemas**:
   - `MachineCreate`, `MachineRead`, `MachineUpdate`
   - `MachineDefinitionCreate`, `MachineDefinitionRead`, `MachineDefinitionUpdate`

8. **Export from domain/__init__.py**

9. **Create test file**:
   - `tests/models/test_domain/test_machine_sqlmodel.py`
   - Test polymorphic creation, serialization, relationships

---

## 7. Field Mapping Reference

### Machine Fields (from ORM)

| ORM Field | SQLModel Field | Notes |
|:----------|:---------------|:------|
| `status` | `status: MachineStatusEnum` | Default AVAILABLE |
| `machine_definition_accession_id` | FK to `machine_definition_catalog` | |
| `workcell_accession_id` | FK to `workcells` | |
| `machine_category` | `MachineCategoryEnum` | |
| `current_deck_state_json` | `json_field()` | |
| `api_port`, `api_host` | String fields | |
| `backend_config_json` | `json_field()` | |
| `selected_backend_fqn` | String | |
| ... | ... | Complete from ORM file |

### MachineDefinition Fields (from ORM)

| ORM Field | SQLModel Field | Notes |
|:----------|:---------------|:------|
| `machine_category` | `MachineCategoryEnum` | |
| `manufacturer` | `str \| None` | |
| `material` | `str \| None` | |
| `size_x_mm`, `size_y_mm`, `size_z_mm` | `float \| None` | |
| `plr_definition_details_json` | `json_field()` | |
| `capabilities` | `json_field()` | |
| `compatible_backends` | `json_field()` | |
| `capabilities_config` | `json_field()` | |
| `connection_config` | `json_field()` | |
| `frontend_fqn` | `str \| None` | |
| `deck_definition_accession_id` | FK | |
| `resource_definition_accession_id` | FK | |
| ... | ... | Complete from ORM file |

---

## On Completion

- [ ] Commit changes with message: `feat(models): migrate Machine + MachineDefinition to SQLModel`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 2.2 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
- `P2_03_migrate_asset_base.md` - Asset base migration (prerequisite)
