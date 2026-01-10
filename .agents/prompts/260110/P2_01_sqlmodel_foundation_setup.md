# Agent Prompt: SQLModel Foundation Setup

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 1.1 — Foundation Setup
**Parallelizable:** ✅ Can run in parallel with P2_02

---

## 1. The Task

Add SQLModel dependency and create the unified base infrastructure that combines the existing `BaseOrm` (SQLAlchemy) patterns with Pydantic config. This establishes the foundation for all subsequent model migrations.

**User Value:** Enables unified Python models that serve as both ORM definitions AND Pydantic schemas, eliminating the need to maintain duplicate model definitions.

---

## 2. Technical Implementation Strategy

### Architecture Overview

The current codebase has two separate inheritance hierarchies:

1. **ORM Base** (`praxis/backend/utils/db.py`):
   - `Base(MappedAsDataclass, DeclarativeBase)` with:
     - `accession_id` (UUID7 primary key)
     - `created_at`, `updated_at` (timestamps with `server_default`)
     - `properties_json` (JsonVariant)
     - `name` (indexed string)

2. **Pydantic Base** (`praxis/backend/models/pydantic_internals/pydantic_base.py`):
   - `PraxisBaseModel(BaseModel)` with:
     - `accession_id` (UUID7 with `default_factory=uuid7`)
     - `created_at`, `updated_at` (datetime with factories)
     - `name` (random hex default)
     - `properties_json` (dict)
     - `model_config = ConfigDict(from_attributes=True, use_enum_values=True, validate_assignment=True)`

### New Unified Structure

Create `praxis/backend/models/domain/sqlmodel_base.py`:

```python
# Pseudocode structure
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from praxis.backend.utils.db import JsonVariant
from praxis.backend.utils.uuid import uuid7

class PraxisBase(SQLModel):
    """Unified base for all Praxis domain models.
    
    Provides:
    - UUID7 accession_id as primary key (when table=True)
    - Timestamps (created_at, updated_at)
    - Generic properties_json field
    - Pydantic config for serialization
    """
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
    )
    
    # When subclassed with table=True, these become columns
    accession_id: uuid.UUID = Field(
        default_factory=uuid7,
        primary_key=True,  # Only applies when table=True
        index=True,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": func.now()},
    )
    name: str = Field(index=True)
    properties_json: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JsonVariant),
    )
```

### JSON Field Handling

SQLModel has quirks with `sa_column=Column(JSON)`. Create a reusable pattern:

```python
# In sqlmodel_base.py
from typing import Any
from sqlalchemy import Column
from praxis.backend.utils.db import JsonVariant

def json_field(
    default: Any = None,
    nullable: bool = True,
    **kwargs
) -> Any:
    """Create a SQLModel-compatible JSON field using JsonVariant."""
    return Field(
        default=default,
        sa_column=Column(JsonVariant, nullable=nullable),
        **kwargs
    )
```

### Alembic Integration

Update `alembic/env.py` to import SQLModel metadata:

```python
# Add alongside existing imports
from sqlmodel import SQLModel

# Merge metadata for migration detection
# SQLModel tables will be registered when domain models are imported
```

---

## 3. Context & References

**Primary Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/__init__.py` | New package for unified domain models |
| `praxis/backend/models/domain/sqlmodel_base.py` | Unified `PraxisBase(SQLModel)` class |

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `pyproject.toml` | Add `sqlmodel>=0.0.22` dependency |
| `alembic/env.py` | Import SQLModel metadata alongside existing ORM |

**Reference Files (Read-Only):**

| Path | Pattern Source |
|:-----|:---------------|
| `praxis/backend/utils/db.py` | Current `Base` class with UUID7, timestamps |
| `praxis/backend/models/pydantic_internals/pydantic_base.py` | Current `PraxisBaseModel` config |
| `praxis/backend/utils/uuid.py` | UUID7 generation function |
| `praxis/backend/models/orm/types.py` | `JsonVariant` type alias |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python, `npm` for Angular.
- **Backend Path**: `praxis/backend`
- **Package Manager**: `uv` (not pip directly)
- **SQLModel Version**: `>=0.0.22` (latest stable with Pydantic v2 support)
- **Linting**: Run `uv run ruff check .` before committing.
- **Type Checking**: Ensure `mypy` passes on new files.

### Sharp Bits / Technical Debt

1. **SQLModel JSON quirks**: `sa_column=Column(JSON)` requires careful handling. The `json_field()` helper abstracts this.
2. **Dual metadata**: During migration, both `Base.metadata` (SQLAlchemy) and `SQLModel.metadata` will coexist. Alembic must see both.
3. **MappedAsDataclass**: The current `Base` uses `MappedAsDataclass`. SQLModel handles this differently via Pydantic. Don't mix inheritance.

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors.
2. SQLModel is installed and importable:

   ```bash
   uv run python -c "from sqlmodel import SQLModel; print('SQLModel OK')"
   ```

3. New base class is importable:

   ```bash
   uv run python -c "from praxis.backend.models.domain.sqlmodel_base import PraxisBase; print('PraxisBase OK')"
   ```

4. Alembic can detect both metadata sources:

   ```bash
   uv run alembic check
   ```

5. Existing tests still pass (no regressions):

   ```bash
   uv run pytest tests/models/test_orm/ -x -q
   ```

---

## 6. Implementation Steps

1. **Add SQLModel dependency** to `pyproject.toml`:
   - Add `"sqlmodel>=0.0.22"` to `dependencies` list
   - Run `uv sync` to install

2. **Create domain package**:
   - Create `praxis/backend/models/domain/__init__.py` (empty or minimal exports)
   - Create `praxis/backend/models/domain/sqlmodel_base.py`

3. **Implement PraxisBase**:
   - Import from `sqlmodel`, `sqlalchemy`, and existing utils
   - Define `PraxisBase(SQLModel)` with all base fields
   - Create `json_field()` helper for JSON columns
   - Add comprehensive docstrings

4. **Update Alembic**:
   - Import the new domain models in `alembic/env.py`
   - Ensure `target_metadata` includes SQLModel tables

5. **Write unit test** for base class:
   - Create `tests/models/test_domain/test_sqlmodel_base.py`
   - Test field defaults, serialization, and table creation

---

## On Completion

- [ ] Commit changes with message: `feat(models): add SQLModel foundation and PraxisBase class`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 1.1 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
