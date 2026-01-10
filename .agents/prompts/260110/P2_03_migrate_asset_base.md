# Agent Prompt: Migrate Asset Polymorphic Base to SQLModel

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 2.1 — Model Migration: Asset Base
**Parallelizable:** ❌ Sequential — Requires P2_01 completion

---

## 1. The Task

Unify the `Asset` polymorphic base model from separate ORM and Pydantic definitions into a single SQLModel-based domain model. This is the foundational entity that `Machine` and `Resource` inherit from using SQLAlchemy's polymorphic inheritance.

**User Value:** Single source of truth for Asset schema used in database, API requests, and API responses.

**Critical**: This prompt prototypes the polymorphic inheritance pattern that will be reused for all other model migrations.

---

## 2. Technical Implementation Strategy

### Current Architecture (Dual Definitions)

**ORM** (`praxis/backend/models/orm/asset.py`):

```python
class AssetOrm(Base):
    __tablename__ = "assets"
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType), ...)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    fqn: Mapped[str] = mapped_column(String, index=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    plr_state: Mapped[dict | None] = mapped_column(JsonVariant, nullable=True)
    plr_definition: Mapped[dict | None] = mapped_column(JsonVariant, nullable=True)
    
    __mapper_args__ = {
        "polymorphic_on": asset_type,
        "polymorphic_identity": AssetType.ASSET,
    }
```

**Pydantic** (`praxis/backend/models/pydantic_internals/asset.py`):

```python
class AssetBase(PraxisBaseModel):
    asset_type: AssetType | None
    fqn: str | None
    location: str | None

class AssetResponse(AssetBase, PraxisBaseModel):
    plr_state: dict[str, Any] | None
    plr_definition: dict[str, Any] | None

class AssetUpdate(BaseModel):
    name: str | None
    fqn: str | None
    location: str | None
    plr_state: dict[str, Any] | None
    plr_definition: dict[str, Any] | None
    properties_json: dict[str, Any] | None
```

### Target Architecture (Unified SQLModel)

Create `praxis/backend/models/domain/asset.py`:

```python
from typing import Any, ClassVar
from sqlmodel import Field, Relationship
from sqlalchemy import Column, Enum as SAEnum
from praxis.backend.models.domain.sqlmodel_base import PraxisBase, json_field
from praxis.backend.models.enums import AssetType

class AssetBase(PraxisBase):
    """Base schema for Asset - shared fields for create/update/response."""
    asset_type: AssetType = Field(
        default=AssetType.ASSET,
        sa_column=Column(SAEnum(AssetType), index=True),
    )
    fqn: str = Field(default="", index=True)
    location: str | None = Field(default=None, index=True)

class Asset(AssetBase, table=True):
    """Asset ORM model with polymorphic inheritance."""
    __tablename__ = "assets"
    
    plr_state: dict[str, Any] | None = json_field(default=None)
    plr_definition: dict[str, Any] | None = json_field(default=None)
    
    # Relationships
    asset_reservations: list["AssetReservation"] = Relationship(
        back_populates="asset",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    
    __mapper_args__: ClassVar[dict] = {
        "polymorphic_on": "asset_type",
        "polymorphic_identity": AssetType.ASSET,
    }

class AssetCreate(AssetBase):
    """Schema for creating an Asset."""
    pass

class AssetRead(AssetBase):
    """Schema for reading an Asset (API response)."""
    plr_state: dict[str, Any] | None = None
    plr_definition: dict[str, Any] | None = None

class AssetUpdate(PraxisBase):
    """Schema for updating an Asset (partial update)."""
    name: str | None = None
    fqn: str | None = None
    location: str | None = None
    plr_state: dict[str, Any] | None = None
    plr_definition: dict[str, Any] | None = None
    properties_json: dict[str, Any] | None = None
```

### Polymorphic Inheritance Pattern

SQLModel supports SQLAlchemy's polymorphic inheritance via `__mapper_args__`:

```python
class Asset(AssetBase, table=True):
    __mapper_args__: ClassVar[dict] = {
        "polymorphic_on": "asset_type",  # Use string for column reference
        "polymorphic_identity": AssetType.ASSET,
    }

class Machine(Asset, table=True):
    __tablename__ = "machines"  # Joined table inheritance
    __mapper_args__: ClassVar[dict] = {
        "polymorphic_identity": AssetType.MACHINE,
    }
```

**Important**: The current codebase uses **single-table inheritance** (all assets in `assets` table with discriminator column). Verify this pattern before implementation.

---

## 3. Context & References

**Primary Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/asset.py` | Unified Asset SQLModel |

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/__init__.py` | Export new Asset models |
| `praxis/backend/api/machines.py` | Update imports (later phase) |

**Files to Deprecate (Do NOT delete yet):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/orm/asset.py` | Legacy ORM (keep during transition) |
| `praxis/backend/models/pydantic_internals/asset.py` | Legacy Pydantic (keep during transition) |

**Reference Files (Read-Only):**

| Path | Pattern Source |
|:-----|:---------------|
| `praxis/backend/models/orm/asset.py` | Current ORM with polymorphic config |
| `praxis/backend/models/pydantic_internals/asset.py` | Current Pydantic schemas |
| `praxis/backend/models/enums/__init__.py` | `AssetType` enum definition |
| `praxis/backend/models/orm/schedule.py` | `AssetReservationOrm` for relationship |
| `tests/models/test_orm/test_asset_requirement_orm.py` | Test patterns |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands.
- **Backend Path**: `praxis/backend`
- **Do NOT modify existing ORM/Pydantic files** — create new domain models alongside
- **Do NOT update API routers yet** — that's Phase 5
- **Table name must remain `assets`** — no schema changes in this phase

### Sharp Bits / Technical Debt

1. **Polymorphic identity**: SQLModel requires `ClassVar[dict]` type hint for `__mapper_args__`
2. **Relationship imports**: Use `TYPE_CHECKING` to avoid circular imports
3. **Single vs Joined inheritance**: Current schema uses single-table. Don't change.
4. **JSON fields**: Must use `json_field()` helper from `sqlmodel_base.py`

---

## 5. Verification Plan

**Definition of Done:**

1. New domain model is importable:

   ```bash
   uv run python -c "from praxis.backend.models.domain.asset import Asset, AssetCreate, AssetRead, AssetUpdate; print('OK')"
   ```

2. Table creation works (in-memory test):

   ```bash
   uv run python -c "
   from sqlmodel import SQLModel, create_engine
   from praxis.backend.models.domain.asset import Asset
   engine = create_engine('sqlite:///:memory:')
   SQLModel.metadata.create_all(engine)
   print('Table created OK')
   "
   ```

3. Serialization round-trip works:

   ```bash
   uv run python -c "
   from praxis.backend.models.domain.asset import Asset, AssetRead
   from praxis.backend.models.enums import AssetType
   
   # Create instance
   asset = Asset(name='test', asset_type=AssetType.MACHINE, fqn='test.Machine')
   
   # Serialize to Pydantic (response)
   response = AssetRead.model_validate(asset)
   print(f'Serialized: {response.model_dump_json()}')
   "
   ```

4. Existing ORM tests still pass:

   ```bash
   uv run pytest tests/models/test_orm/test_machine_orm.py tests/models/test_orm/test_resource_orm.py -x -q
   ```

5. Create new test file and run:

   ```bash
   uv run pytest tests/models/test_domain/test_asset_sqlmodel.py -v
   ```

---

## 6. Implementation Steps

1. **Create domain asset module**:
   - Create `praxis/backend/models/domain/asset.py`
   - Import `PraxisBase`, `json_field` from `sqlmodel_base`
   - Import `AssetType` from enums

2. **Implement AssetBase**:
   - Define shared fields: `asset_type`, `fqn`, `location`
   - Use proper Field() annotations with sa_column for indexed fields

3. **Implement Asset (table=True)**:
   - Inherit from `AssetBase`
   - Add `__tablename__ = "assets"`
   - Add JSON fields: `plr_state`, `plr_definition`
   - Add `__mapper_args__` for polymorphic setup
   - Add relationship to `AssetReservation` (forward reference)

4. **Implement CRUD schemas**:
   - `AssetCreate(AssetBase)` — for POST requests
   - `AssetRead(AssetBase)` — for GET responses, includes JSON fields
   - `AssetUpdate(PraxisBase)` — for PATCH/PUT, all fields optional

5. **Update domain **init**.py**:
   - Export all new models

6. **Create test file**:
   - Create `tests/models/test_domain/test_asset_sqlmodel.py`
   - Test instantiation, serialization, validation

7. **Verify polymorphic setup**:
   - Ensure `polymorphic_on` column detection works
   - Test that subclass creation sets correct `asset_type`

---

## 7. Test File Template

Create `tests/models/test_domain/test_asset_sqlmodel.py`:

```python
"""Tests for unified Asset SQLModel."""
import pytest
from sqlmodel import Session, SQLModel, create_engine

from praxis.backend.models.domain.asset import Asset, AssetCreate, AssetRead, AssetUpdate
from praxis.backend.models.enums import AssetType


@pytest.fixture
def engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create database session."""
    with Session(engine) as session:
        yield session


class TestAssetSQLModel:
    """Test suite for Asset SQLModel."""

    def test_asset_creation_defaults(self, session):
        """Test creating Asset with minimal fields."""
        asset = Asset(name="test_asset")
        session.add(asset)
        session.commit()
        session.refresh(asset)
        
        assert asset.accession_id is not None
        assert asset.name == "test_asset"
        assert asset.asset_type == AssetType.ASSET
        assert asset.fqn == ""
        assert asset.location is None

    def test_asset_serialization_to_read(self, session):
        """Test serializing Asset to AssetRead response."""
        asset = Asset(
            name="test_asset",
            fqn="test.Asset",
            plr_state={"key": "value"},
        )
        session.add(asset)
        session.commit()
        
        response = AssetRead.model_validate(asset)
        assert response.name == "test_asset"
        assert response.fqn == "test.Asset"
        assert response.plr_state == {"key": "value"}

    def test_asset_create_schema_validation(self):
        """Test AssetCreate schema validation."""
        create_data = AssetCreate(
            name="new_asset",
            asset_type=AssetType.MACHINE,
            fqn="machines.NewMachine",
        )
        assert create_data.name == "new_asset"
        assert create_data.asset_type == AssetType.MACHINE

    def test_asset_update_partial(self):
        """Test AssetUpdate allows partial updates."""
        update_data = AssetUpdate(location="Lab A")
        assert update_data.location == "Lab A"
        assert update_data.name is None  # Not provided
```

---

## On Completion

- [ ] Commit changes with message: `feat(models): migrate Asset to unified SQLModel domain model`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 2.1 → Done)
- [ ] Mark this prompt complete in batch README
- [ ] Document any polymorphic inheritance gotchas in `.agents/NOTES.md`

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
- [SQLModel Inheritance](https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/)
- [SQLAlchemy Polymorphic Inheritance](https://docs.sqlalchemy.org/en/20/orm/inheritance.html)
