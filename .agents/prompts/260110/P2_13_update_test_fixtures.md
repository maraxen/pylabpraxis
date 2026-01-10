# Agent Prompt: Update Test Factories and Fixtures for SQLModel

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 5.2 — Infrastructure Updates: Test Fixtures
**Parallelizable:** ⚠️ Can run in parallel with P2_12 after Phase 2-4 complete

---

## 1. The Task

Refactor test factories, fixtures, and helpers to use the unified SQLModel domain models instead of separate ORM models. Ensure all tests continue to pass with the new model structure.

**User Value:** Consistent test infrastructure using the same models as production code.

---

## 2. Technical Implementation Strategy

### Current Test Infrastructure

**Factories** (`tests/factories.py`):
```python
from factory.alchemy import SQLAlchemyModelFactory
from praxis.backend.models.orm.machine import MachineOrm

class MachineFactory(SQLAlchemyModelFactory):
    class Meta:
        model = MachineOrm
    
    name = factory.Faker("word")
    ...
```

**Fixtures** (`tests/conftest.py`):
```python
from praxis.backend.utils.db import Base

@pytest_asyncio.fixture
async def db_session(engine):
    async with AsyncSession(engine) as session:
        yield session
```

**Helpers** (`tests/helpers.py`):
```python
# Entity creation helpers using ORM models
```

### Target Architecture

Update factories to use SQLModel domain models:

```python
from factory.alchemy import SQLAlchemyModelFactory
from praxis.backend.models.domain.machine import Machine

class MachineFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Machine  # SQLModel table class
    
    name = factory.Faker("word")
    ...
```

### SQLModel + Factory Boy Compatibility

SQLModel tables work with SQLAlchemyModelFactory because they inherit from SQLAlchemy's declarative base. Key considerations:

1. **Session binding**: Factory needs `Session` bound
2. **Relationship handling**: Use `SubFactory` for related models
3. **Default values**: SQLModel defaults should be respected

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `tests/conftest.py` | Update fixtures for SQLModel metadata |
| `tests/factories.py` | Update factories to use domain models |
| `tests/factories_schedule.py` | Update schedule-specific factories |
| `tests/helpers.py` | Update helper functions |

**Reference Files (Read-Only):**

| Path | Pattern Source |
|:-----|:---------------|
| `tests/conftest.py` | Current fixture structure |
| `tests/factories.py` | Current factory patterns |
| `tests/models/test_orm/` | Test files using factories |
| `praxis/backend/models/domain/` | New unified models |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands.
- **Test framework**: pytest + pytest-asyncio
- **Factory library**: factory_boy with SQLAlchemyModelFactory
- **Database**: SQLite in-memory for fast tests, PostgreSQL optional

### Sharp Bits / Technical Debt

1. **Dual metadata**: During transition, some tests may use old ORM, some use SQLModel
2. **Factory session scoping**: Ensure session is properly bound per test
3. **Polymorphic factories**: Asset → Machine/Resource needs careful setup
4. **UUID7 generation**: Factory should use same uuid7() function as production

---

## 5. Verification Plan

**Definition of Done:**

1. Factories import and create objects:
   ```bash
   uv run python -c "
   from tests.factories import MachineFactory, ResourceFactory, WorkcellFactory
   print('Factories import OK')
   "
   ```

2. All model tests pass:
   ```bash
   uv run pytest tests/models/ -x -q
   ```

3. All API tests pass:
   ```bash
   uv run pytest tests/api/ -x -q
   ```

4. All service tests pass:
   ```bash
   uv run pytest tests/services/ -x -q
   ```

5. Full test suite passes:
   ```bash
   uv run pytest tests/ -v --tb=short
   ```

---

## 6. Implementation Steps

1. **Update conftest.py metadata**:
   - Import SQLModel metadata alongside Base
   - Ensure `create_all` includes both

2. **Update WorkcellFactory**:
   ```python
   from praxis.backend.models.domain.workcell import Workcell
   
   class WorkcellFactory(SQLAlchemyModelFactory):
       class Meta:
           model = Workcell
   ```

3. **Update MachineFactory**:
   - Import from domain.machine
   - Handle polymorphic identity

4. **Update ResourceFactory**:
   - Similar to MachineFactory

5. **Update remaining factories**:
   - ResourceDefinitionFactory
   - DeckFactory, DeckDefinitionFactory
   - ProtocolRunFactory, FunctionCallLogFactory
   - FunctionDataOutputFactory, WellDataOutputFactory

6. **Update factories_schedule.py**:
   - ScheduleEntryFactory
   - AssetReservationFactory

7. **Update helpers.py**:
   - Any entity creation helpers

8. **Run incremental tests**:
   ```bash
   uv run pytest tests/models/test_orm/ -v  # Start with ORM tests
   uv run pytest tests/models/test_domain/ -v  # Then domain tests
   uv run pytest tests/api/ -v  # Then API tests
   ```

9. **Fix any failures**:
   - Check field name changes
   - Check relationship loading
   - Check JSON field handling

---

## 7. Factory Migration Checklist

| Factory | Source Model | Target Model | Status |
|:--------|:-------------|:-------------|:-------|
| `WorkcellFactory` | `WorkcellOrm` | `Workcell` | ⬜ |
| `MachineFactory` | `MachineOrm` | `Machine` | ⬜ |
| `ResourceFactory` | `ResourceOrm` | `Resource` | ⬜ |
| `ResourceDefinitionFactory` | `ResourceDefinitionOrm` | `ResourceDefinition` | ⬜ |
| `DeckFactory` | `DeckOrm` | `Deck` | ⬜ |
| `DeckDefinitionFactory` | `DeckDefinitionOrm` | `DeckDefinition` | ⬜ |
| `ProtocolRunFactory` | `ProtocolRunOrm` | `ProtocolRun` | ⬜ |
| `FunctionProtocolDefinitionFactory` | `FunctionProtocolDefinitionOrm` | `FunctionProtocolDefinition` | ⬜ |
| `FunctionCallLogFactory` | `FunctionCallLogOrm` | `FunctionCallLog` | ⬜ |
| `FunctionDataOutputFactory` | `FunctionDataOutputOrm` | `FunctionDataOutput` | ⬜ |
| `WellDataOutputFactory` | `WellDataOutputOrm` | `WellDataOutput` | ⬜ |

---

## On Completion

- [ ] Commit changes with message: `refactor(tests): update factories and fixtures for SQLModel`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 5.2 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
- [Factory Boy with SQLAlchemy](https://factoryboy.readthedocs.io/en/stable/orms.html#sqlalchemy)
