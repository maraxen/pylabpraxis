# Agent Prompt: Migrate tests/core Files

**Status:** 🔴 Not Started
**Priority:** P1
**Batch:** 260112
**Parallel Group:** 4 of 5

---

## 1. The Task

Migrate 12 test files in `tests/core/` to use unified SQLModel domain imports instead of legacy `pydantic_internals` and `orm` module imports.

**Files to Modify:**

```
tests/core/test_asset_manager.py
tests/core/test_celery_tasks.py
tests/core/test_container.py
tests/core/test_orchestrator.py
tests/core/test_protocol_execution_service.py
tests/core/test_scheduler.py
tests/core/test_workcell_runtime.py
tests/core/test_asset_lock_manager.py
tests/core/decorators/test_definition_builder.py
tests/core/decorators/test_models.py
tests/core/decorators/test_parameter_processor.py
tests/core/decorators/test_protocol_decorator.py
tests/core/decorators/test_protocol_decorator_runtime.py
```

## 2. Migration Pattern

### Import Transformations

```python
# BEFORE - pydantic_internals
from praxis.backend.models.pydantic_internals.protocol import (
    AssetRequirementModel,
    FunctionProtocolDefinitionCreate,
)
from praxis.backend.models.pydantic_internals.runtime import (
    AcquireAsset,
    AcquireAssetLock,
    RuntimeAssetRequirement,
)

# AFTER - domain
from praxis.backend.models.domain.protocol import (
    AssetRequirementModel,
    FunctionProtocolDefinitionCreate,
)
from praxis.backend.models.pydantic_internals.runtime import (
    AcquireAsset,
    AcquireAssetLock,
    RuntimeAssetRequirement,
)
# NOTE: runtime models MAY still be in pydantic_internals - check if they exist in domain
```

```python
# BEFORE - orm
from praxis.backend.models.orm.protocol import (
    ProtocolRunOrm,
    FunctionProtocolDefinitionOrm,
)

# AFTER - domain (drop Orm suffix)
from praxis.backend.models.domain.protocol import (
    ProtocolRun,
    FunctionProtocolDefinition,
)
```

### Class Name Transformations

| Old Name | New Name |
|----------|----------|
| `ProtocolRunOrm` | `ProtocolRun` |
| `FunctionProtocolDefinitionOrm` | `FunctionProtocolDefinition` |
| `MachineOrm` | `Machine` |
| `ResourceOrm` | `Resource` |
| `WorkcellOrm` | `Workcell` |
| `ScheduleEntryOrm` | `ScheduleEntry` |
| `AssetReservationOrm` | `AssetReservation` |

### Special Cases

**test_scheduler.py**: Has many inline imports within test functions. Search for all `from praxis.backend.models.orm` patterns throughout the file.

**decorator tests**: May import protocol metadata models - check if they've been moved to domain.

**runtime models**: `AcquireAsset`, `AcquireAssetLock`, `RuntimeAssetRequirement` may still be in `pydantic_internals.runtime`. Check `praxis/backend/models/pydantic_internals/runtime.py` if it still exists. If moved, update accordingly.

## 3. Reference

**Domain module exports:**

- `praxis/backend/models/domain/__init__.py`
- `praxis/backend/models/domain/protocol.py`

**Check runtime module location:**

```bash
ls -la praxis/backend/models/pydantic_internals/runtime.py
```

## 4. Constraints

- Use `uv run` for all Python commands
- Changes must be purely mechanical refactors - no logic changes
- Pay special attention to inline imports within test functions
- Preserve all test functionality

## 5. Verification

```bash
# Test collection for this file group
uv run pytest tests/core/ --collect-only

# Run tests
uv run pytest tests/core/ -v
```

**Definition of Done:**

1. All 12 files import ORM models from `praxis.backend.models.domain`
2. No imports from `orm` module
3. No `Orm` suffix in any class reference
4. `uv run pytest tests/core/ --collect-only` shows 0 errors
5. All tests pass

---

## On Completion

- [ ] Mark this prompt complete in README.md
- [ ] Report any issues encountered
