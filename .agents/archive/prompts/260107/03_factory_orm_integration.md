# Agent Prompt: 03_factory_orm_integration

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260107](./README.md)
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)

---

## Task

Fix Factory Boy and SQLAlchemy ORM integration issues causing `NOT NULL constraint failed` errors in test factories.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Work item tracking (Section 5) |
| [tests/factories.py](file:///Users/mar/Projects/pylabpraxis/tests/factories.py) | Factory definitions |
| [tests/services/test_well_outputs.py](file:///Users/mar/Projects/pylabpraxis/tests/services/test_well_outputs.py) | Failing tests |
| [praxis/backend/models/orm/outputs.py](file:///Users/mar/Projects/pylabpraxis/praxis/backend/models/orm/outputs.py) | ORM models |

---

## Problem Description

`FunctionDataOutputFactory` and related factories fail to correctly populate foreign key fields:

```
sqlalchemy.exc.IntegrityError: NOT NULL constraint failed: function_data_outputs.function_call_log_id
```

### Root Cause

SQLAlchemy's dataclass-style ORM mapping requires `kw_only=True` for non-default fields. Factories use `SubFactory` and `LazyAttribute` which don't properly flush before dependent ORM creation.

---

## Implementation Details

### 1. Investigate Factory Flush Timing

```python
# Check if SubFactory creates are flushed before parent
class FunctionDataOutputFactory(factory.alchemy.SQLAlchemyModelFactory):
    function_call_log = factory.SubFactory(FunctionCallLogFactory)
    # Is function_call_log.id available at this point?
```

### 2. Potential Fixes

**Option A:** Add explicit flush in factory

```python
@factory.lazy_attribute
def function_call_log_id(self):
    log = FunctionCallLogFactory.create()
    self._meta.sqlalchemy_session.flush()
    return log.id
```

**Option B:** Review ORM field ordering (ensure FK fields have defaults or are nullable during construction)

**Option C:** Use `factory.post_generation` hooks

### 3. Verify All Related Factories

- `FunctionDataOutputFactory`
- `FunctionCallLogFactory`
- `WellDataOutputFactory`

---

## Project Conventions

- **Backend Tests**: `uv run pytest tests/services/test_well_outputs.py -v`
- **Type Check**: `uv run pyright praxis/backend`

See [codestyles/python.md](../../codestyles/python.md) for guidelines.

---

## On Completion

- [ ] All tests in `test_well_outputs.py` pass
- [ ] Update [quality_assurance.md](../../backlog/quality_assurance.md) Section 5
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) "Factory ORM Integration"
- [ ] Mark this prompt complete in batch README

---

## References

- [Factory Boy SQLAlchemy Docs](https://factoryboy.readthedocs.io/en/stable/orms.html#sqlalchemy)
- [.agents/README.md](../../README.md)
