# Agent Prompt: Migrate tests/services Files

**Status:** 🔴 Not Started
**Priority:** P1
**Batch:** 260112
**Parallel Group:** 3 of 5

---

## 1. The Task

Migrate 10 test files in `tests/services/` to use unified SQLModel domain imports instead of legacy `pydantic_internals` and `orm` module imports.

**Files to Modify:**

```
tests/services/test_deck_service.py
tests/services/test_deck_type_definition_service.py
tests/services/test_plate_viz.py
tests/services/test_protocol_definition_service.py
tests/services/test_protocol_run_service.py
tests/services/test_resource_type_definition_service.py
tests/services/test_scheduler_service.py
tests/services/test_user_service.py
tests/services/test_well_outputs.py
tests/services/test_workcell_service.py
```

## 2. Migration Pattern

### Import Transformations

```python
# BEFORE - pydantic_internals
from praxis.backend.models.pydantic_internals.deck import DeckCreate, DeckUpdate
from praxis.backend.models.pydantic_internals.protocol import (
    FunctionProtocolDefinitionCreate,
    ProtocolRunCreate,
)
from praxis.backend.models.pydantic_internals.outputs import (
    WellDataOutputCreate,
    PlateDataVisualization,
)
from praxis.backend.models.pydantic_internals.user import UserCreate, UserUpdate
from praxis.backend.models.pydantic_internals.workcell import WorkcellCreate

# AFTER - domain
from praxis.backend.models.domain.deck import DeckCreate, DeckUpdate
from praxis.backend.models.domain.protocol import (
    FunctionProtocolDefinitionCreate,
    ProtocolRunCreate,
)
from praxis.backend.models.domain.outputs import (
    WellDataOutputCreate,
    PlateDataVisualization,
)
from praxis.backend.models.domain.user import UserCreate, UserUpdate
from praxis.backend.models.domain.workcell import WorkcellCreate
```

```python
# BEFORE - orm
from praxis.backend.models.orm.protocol import ProtocolSourceRepositoryOrm
from praxis.backend.models.orm.resource import ResourceDefinitionOrm

# AFTER - domain (drop Orm suffix)
from praxis.backend.models.domain.protocol import ProtocolSourceRepository
from praxis.backend.models.domain.resource import ResourceDefinition
```

### Class Name Transformations

| Old Name | New Name |
|----------|----------|
| `ProtocolSourceRepositoryOrm` | `ProtocolSourceRepository` |
| `FunctionProtocolDefinitionOrm` | `FunctionProtocolDefinition` |
| `ProtocolRunOrm` | `ProtocolRun` |
| `ResourceDefinitionOrm` | `ResourceDefinition` |
| `ScheduleEntryOrm` | `ScheduleEntry` |
| `AssetReservationOrm` | `AssetReservation` |

### Code Body Transformations

1. Replace all class instantiations: `XOrm(...)` → `X(...)`
2. Replace all type hints: `-> XOrm` → `-> X`
3. Replace fixture return types: `async def fixture() -> XOrm:` → `async def fixture() -> X:`

## 3. Reference

**Already migrated (use as pattern):**

- `tests/services/test_machine_service.py` - Clean domain imports
- `tests/services/test_resource_service.py` - Partial migration (still has one orm import to fix)

**Domain module exports:**

- `praxis/backend/models/domain/__init__.py`
- `praxis/backend/models/domain/protocol.py` - Protocol models including `ProtocolSourceRepository`

## 4. Constraints

- Use `uv run` for all Python commands
- Changes must be purely mechanical refactors - no logic changes
- Preserve all test functionality
- Check for inline imports within test functions (common pattern)

## 5. Verification

```bash
# Test collection for this file group
uv run pytest tests/services/ --collect-only

# Run tests
uv run pytest tests/services/ -v
```

**Definition of Done:**

1. All 10 files import from `praxis.backend.models.domain`
2. No imports from `pydantic_internals` or `orm`
3. No `Orm` suffix in any class reference
4. `uv run pytest tests/services/ --collect-only` shows 0 errors
5. All tests pass

---

## On Completion

- [ ] Mark this prompt complete in README.md
- [ ] Report any issues encountered
