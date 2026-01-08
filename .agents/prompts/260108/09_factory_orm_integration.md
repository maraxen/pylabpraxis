# Agent Prompt: 09_factory_orm_integration

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)  
**Priority:** P2

---

## Task

Fix Factory Boy integration issues causing `NOT NULL constraint failed` errors in tests. Resolve foreign key population timing between SubFactory/LazyAttribute and SQLAlchemy ORM.

---

## Problem Statement

`FunctionDataOutputFactory` and related factories fail to correctly populate foreign key fields:

```
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed
```

**Root Cause**: SQLAlchemy's dataclass-style ORM mapping requires `kw_only=True` for non-default fields. Factories use `SubFactory` and `LazyAttribute` which don't properly flush before dependent ORM creation.

---

## Implementation Steps

### 1. Investigate Factory Flush Timing

Analyze the factory creation order in `tests/factories.py`:

```python
# Check if SubFactory creates are flushed before parent
class FunctionDataOutputFactory(BaseFactory):
    function_call_log = factory.SubFactory(FunctionCallLogFactory)
    # Is function_call_log.id available when FunctionDataOutput is created?
```

### 2. Review ORM Model Field Ordering

Check `praxis/backend/models/orm/outputs.py`:

- Verify `kw_only=True` is set correctly
- Ensure FK fields are properly ordered

### 3. Fix Factory Definitions

Options:

- Add manual `session.flush()` calls in factories
- Use `factory.LazyAttribute` with explicit ID retrieval
- Refactor to `@factory.post_generation` hooks

### 4. Verify Tests Pass

```bash
uv run pytest tests/services/test_well_outputs.py -v
```

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Backlog tracking |
| [tests/factories.py](file:///Users/mar/Projects/pylabpraxis/tests/factories.py) | Factory definitions |
| [tests/services/test_well_outputs.py](file:///Users/mar/Projects/pylabpraxis/tests/services/test_well_outputs.py) | Failing tests |
| [praxis/backend/models/orm/outputs.py](file:///Users/mar/Projects/pylabpraxis/praxis/backend/models/orm/outputs.py) | ORM models |

---

## Project Conventions

- **Backend Tests**: `uv run pytest tests/ -v`

See [codestyles/python.md](../../codestyles/python.md) for conventions.

---

## On Completion

- [ ] Commit changes with message: `fix(tests): resolve Factory Boy ORM foreign key population`
- [ ] Update [quality_assurance.md](../../backlog/quality_assurance.md) - mark Factory ORM Integration complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
