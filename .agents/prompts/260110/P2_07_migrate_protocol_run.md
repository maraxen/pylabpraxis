# Agent Prompt: Migrate ProtocolRun + Related Entities to SQLModel

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 3.1 — Model Migration: Protocol Run
**Parallelizable:** ⚠️ Can run after Phase 2 completion (Asset, Machine, Resource, Deck)

---

## 1. The Task

Unify `ProtocolRun` and related entities (`FunctionCallLog`, `AssetRequirement`, `ParameterDefinition`) from separate ORM and Pydantic definitions into SQLModel domain models. These models track protocol execution state.

**User Value:** Single source of truth for protocol execution tracking with automatic API type generation.

---

## 2. Technical Implementation Strategy

### Current Architecture

**ORM** (`praxis/backend/models/orm/protocol.py`):
- `ProtocolRunOrm` — Instance of a protocol execution
- `FunctionCallLogOrm` — Log of individual function calls during execution
- `FunctionProtocolDefinitionOrm` — Protocol definition (function signature, parameters)
- `AssetRequirementOrm` — Required assets for a protocol
- `ParameterDefinitionOrm` — Parameter metadata for protocols

**Key Relationships:**
```
FunctionProtocolDefinitionOrm (definition)
    └── ParameterDefinitionOrm[] (parameters)
    └── AssetRequirementOrm[] (required assets)
    └── ProtocolRunOrm[] (executions)

ProtocolRunOrm (execution instance)
    └── FunctionProtocolDefinitionOrm (which protocol)
    └── FunctionCallLogOrm[] (call trace)
    └── AssetReservationOrm[] (reserved assets)
```

**Complex JSON Fields:**
- `ProtocolRunOrm.parameters` — User-provided parameter values
- `FunctionCallLogOrm.arguments` — Function call arguments
- `FunctionCallLogOrm.result` — Function return value

**Pydantic** (`praxis/backend/models/pydantic_internals/protocol.py`):
- `ProtocolRunBase`, `ProtocolRunCreate`, `ProtocolRunResponse`, `ProtocolRunUpdate`
- `FunctionCallLogBase`, `FunctionCallLogCreate`, `FunctionCallLogResponse`, `FunctionCallLogUpdate`
- `FunctionProtocolDefinitionCreate`
- `AssetRequirementModel`, `ParameterMetadataModel`, `ParameterConstraintsModel`
- Various helper models for protocol workflow

---

## 3. Context & References

**Primary Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/protocol.py` | Unified Protocol domain models |

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/__init__.py` | Export Protocol models |

**Files to Deprecate (Do NOT delete yet):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/orm/protocol.py` | Legacy ORM |
| `praxis/backend/models/pydantic_internals/protocol.py` | Legacy Pydantic |

**Reference Files (Read-Only):**

| Path | Pattern Source |
|:-----|:---------------|
| `praxis/backend/models/orm/protocol.py` | Full ORM definition |
| `praxis/backend/models/pydantic_internals/protocol.py` | Pydantic schemas |
| `praxis/backend/api/protocols.py` | API router |
| `tests/models/test_orm/test_protocol_run_orm.py` | ORM tests |
| `tests/models/test_orm/test_function_call_log_orm.py` | Call log tests |
| `tests/models/test_orm/test_function_protocol_definition_orm.py` | Definition tests |
| `tests/models/test_orm/test_asset_requirement_orm.py` | Requirement tests |
| `tests/models/test_orm/test_parameter_definition_orm.py` | Parameter tests |
| `tests/api/test_protocol_runs.py` | API tests |
| `tests/api/test_protocol_definitions.py` | API tests |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands.
- **Backend Path**: `praxis/backend`
- **JSON fields**: `parameters`, `arguments`, `result` use `json_field()` helper
- **Enums**: Preserve `ProtocolStatus` enum values

### Sharp Bits / Technical Debt

1. **Five related models**: ProtocolRun, FunctionCallLog, FunctionProtocolDefinition, AssetRequirement, ParameterDefinition
2. **Complex JSON**: Arguments and results can be arbitrary Python objects (serialized)
3. **Status tracking**: ProtocolRun has detailed status enum with many states
4. **Timing fields**: `start_time`, `end_time`, execution duration calculations

---

## 5. Verification Plan

**Definition of Done:**

1. All five models import successfully:
   ```bash
   uv run python -c "
   from praxis.backend.models.domain.protocol import (
       ProtocolRun, FunctionCallLog, FunctionProtocolDefinition,
       AssetRequirement, ParameterDefinition,
       ProtocolRunCreate, ProtocolRunRead
   )
   print('OK')
   "
   ```

2. Protocol run with call log works:
   ```bash
   uv run python -c "
   from sqlmodel import SQLModel, create_engine, Session
   from praxis.backend.models.domain.protocol import ProtocolRun, FunctionCallLog
   
   engine = create_engine('sqlite:///:memory:')
   SQLModel.metadata.create_all(engine)
   
   with Session(engine) as s:
       run = ProtocolRun(name='test_run')
       log = FunctionCallLog(
           name='call_1',
           function_name='transfer',
           arguments={'source': 'A1', 'dest': 'B1'},
           protocol_run=run,
       )
       s.add(run)
       s.add(log)
       s.commit()
       print(f'ProtocolRun with {len(run.function_call_logs)} calls')
   "
   ```

3. Existing tests still pass:
   ```bash
   uv run pytest tests/models/test_orm/test_protocol_run_orm.py tests/models/test_orm/test_function_call_log_orm.py -x -q
   uv run pytest tests/api/test_protocol_runs.py tests/api/test_protocol_definitions.py -x -q
   ```

4. New domain tests pass:
   ```bash
   uv run pytest tests/models/test_domain/test_protocol_sqlmodel.py -v
   ```

---

## 6. Implementation Steps

1. **Audit all five ORM models**:
   - ProtocolRunOrm fields, status enum, relationships
   - FunctionCallLogOrm with JSON arguments/result
   - FunctionProtocolDefinitionOrm with source info
   - AssetRequirementOrm with constraints
   - ParameterDefinitionOrm with type hints

2. **Create domain/protocol.py**:
   - Import base classes and enums
   - Plan model order (leaf models first)

3. **Implement ParameterDefinition**:
   - Base + table model
   - Type hint and constraint fields

4. **Implement AssetRequirement**:
   - Base + table model
   - Constraint JSON fields

5. **Implement FunctionProtocolDefinition**:
   - Base + table model
   - Relationships to parameters and requirements

6. **Implement FunctionCallLog**:
   - Base + table model
   - JSON fields for arguments and result

7. **Implement ProtocolRun**:
   - Base + table model
   - Status enum, timing fields
   - Relationship to definition and call logs

8. **Implement all CRUD schemas**

9. **Export from domain/__init__.py**

10. **Create test file**:
    - `tests/models/test_domain/test_protocol_sqlmodel.py`

---

## On Completion

- [ ] Commit changes with message: `feat(models): migrate ProtocolRun + related entities to SQLModel`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 3.1 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
