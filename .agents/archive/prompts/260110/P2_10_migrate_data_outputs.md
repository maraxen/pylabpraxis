# Agent Prompt: Migrate Data Output Models to SQLModel

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 4.1 — Model Migration: Data Outputs
**Parallelizable:** ⚠️ Can run after Phase 2 and 3.1 (ProtocolRun)

---

## 1. The Task

Unify `FunctionDataOutput` and `WellDataOutput` models from separate ORM and Pydantic definitions into SQLModel domain models. These models store measurement data, images, and files generated during protocol execution.

**User Value:** Single source of truth for experiment data output with automatic API type generation.

---

## 2. Technical Implementation Strategy

### Current Architecture

**ORM** (`praxis/backend/models/orm/outputs.py`):
- `FunctionDataOutputOrm` — Data output from a function call
- `WellDataOutputOrm` — Well-specific data (plate reader measurements)

**Key Relationships:**
```
FunctionDataOutputOrm
    └── ProtocolRunOrm (which protocol run)
    └── FunctionCallLogOrm (which function call)
    └── ResourceOrm (optional resource reference)
    └── WellDataOutputOrm[] (well-level data)

WellDataOutputOrm
    └── FunctionDataOutputOrm (parent output)
    └── well_data JSON (measurements, readings)
```

**Pydantic** (`praxis/backend/models/pydantic_internals/outputs.py`):
- `FunctionDataOutputBase`, `FunctionDataOutputCreate`, `FunctionDataOutputResponse`, `FunctionDataOutputUpdate`
- `WellDataOutputBase`, `WellDataOutputCreate`, `WellDataOutputResponse`, `WellDataOutputUpdate`
- `FunctionDataOutputFilters`, `WellDataOutputFilters`
- `ProtocolRunDataSummary`, `DataExportRequest`

---

## 3. Context & References

**Primary Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/outputs.py` | Unified Data Output models |

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/__init__.py` | Export Output models |

**Files to Deprecate (Do NOT delete yet):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/orm/outputs.py` | Legacy ORM |
| `praxis/backend/models/pydantic_internals/outputs.py` | Legacy Pydantic |

**Reference Files (Read-Only):**

| Path | Pattern Source |
|:-----|:---------------|
| `praxis/backend/models/orm/outputs.py` | Full ORM definition |
| `praxis/backend/models/pydantic_internals/outputs.py` | Pydantic schemas |
| `praxis/backend/api/outputs.py` | API router |
| `tests/models/test_orm/test_function_data_output_orm.py` | Output tests |
| `tests/models/test_orm/test_well_data_output_orm.py` | Well tests |
| `tests/api/test_function_data_outputs.py` | API tests |
| `tests/api/test_well_data_outputs.py` | API tests |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands.
- **Backend Path**: `praxis/backend`
- **JSON fields**: `well_data` contains measurement arrays
- **Cascade delete**: WellDataOutputs cascade-delete with parent FunctionDataOutput

### Sharp Bits / Technical Debt

1. **Nested JSON**: `well_data` can contain complex measurement structures
2. **Filter models**: `FunctionDataOutputFilters`, `WellDataOutputFilters` are query params (not tables)
3. **Resource relationship**: Optional link to Resource for context

---

## 5. Verification Plan

**Definition of Done:**

1. Models import successfully:
   ```bash
   uv run python -c "
   from praxis.backend.models.domain.outputs import (
       FunctionDataOutput, WellDataOutput,
       FunctionDataOutputCreate, FunctionDataOutputRead,
       WellDataOutputCreate, WellDataOutputRead
   )
   print('OK')
   "
   ```

2. Nested well data works:
   ```bash
   uv run python -c "
   from sqlmodel import SQLModel, create_engine, Session
   from praxis.backend.models.domain.outputs import FunctionDataOutput, WellDataOutput
   
   engine = create_engine('sqlite:///:memory:')
   SQLModel.metadata.create_all(engine)
   
   with Session(engine) as s:
       fdo = FunctionDataOutput(name='measurement_1', output_type='plate_reader')
       wdo = WellDataOutput(
           name='well_A1',
           well_position='A1',
           well_data={'absorbance': 0.5, 'wavelength': 450},
           function_data_output=fdo,
       )
       s.add(fdo)
       s.add(wdo)
       s.commit()
       print(f'FunctionDataOutput with {len(fdo.well_data_outputs)} wells')
   "
   ```

3. Existing tests still pass:
   ```bash
   uv run pytest tests/models/test_orm/test_function_data_output_orm.py tests/models/test_orm/test_well_data_output_orm.py -x -q
   uv run pytest tests/api/test_function_data_outputs.py tests/api/test_well_data_outputs.py -x -q
   ```

4. New domain tests pass:
   ```bash
   uv run pytest tests/models/test_domain/test_outputs_sqlmodel.py -v
   ```

---

## 6. Implementation Steps

1. **Audit ORM models**:
   - FunctionDataOutputOrm fields, relationships
   - WellDataOutputOrm fields, well_data JSON structure

2. **Create domain/outputs.py**:
   - Import base classes

3. **Implement WellDataOutputBase**:
   - well_position, well_data JSON, row/column fields

4. **Implement WellDataOutput(table=True)**:
   - FK to FunctionDataOutput
   - Cascade-delete relationship

5. **Implement FunctionDataOutputBase**:
   - output_type, output_data, optional FKs

6. **Implement FunctionDataOutput(table=True)**:
   - FKs to ProtocolRun, FunctionCallLog, Resource
   - Relationship to WellDataOutputs

7. **Implement CRUD schemas**

8. **Keep filter models as plain Pydantic** (query param models)

9. **Export from domain/__init__.py**

10. **Create test file**:
    - `tests/models/test_domain/test_outputs_sqlmodel.py`

---

## On Completion

- [ ] Commit changes with message: `feat(models): migrate FunctionDataOutput + WellDataOutput to SQLModel`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 4.1 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
