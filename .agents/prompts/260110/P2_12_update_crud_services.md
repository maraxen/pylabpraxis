# Agent Prompt: Update CRUD Services and Router Factory for SQLModel

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 5.1 — Infrastructure Updates: CRUD Services
**Parallelizable:** ❌ Sequential — Requires all Phase 2-4 model migrations complete

---

## 1. The Task

Refactor the CRUD router factory and base service classes to use SQLModel schemas instead of separate ORM + Pydantic models. Update all API routers to use the unified domain models.

**User Value:** Simplified API layer with automatic schema validation from unified models.

---

## 2. Technical Implementation Strategy

### Current Architecture

**CRUD Router Factory** (`praxis/backend/api/utils/crud_router_factory.py`):
```python
def create_crud_router(
    *,
    service: CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType],
    prefix: str,
    tags: list[str],
    create_schema: type[CreateSchemaType],
    update_schema: type[UpdateSchemaType],
    response_schema: type[ResponseSchemaType],
) -> APIRouter:
```

**Base Service** (`praxis/backend/services/utils/crud_base.py`):
```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
    async def get(self, db: AsyncSession, *, accession_id: UUID) -> ModelType | None:
    async def get_multi(self, db: AsyncSession, ...) -> list[ModelType]:
    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
    async def remove(self, db: AsyncSession, *, accession_id: UUID) -> ModelType | None:
```

### Target Architecture

With SQLModel, the ORM model and Pydantic schema are unified. Update the factory:

```python
def create_crud_router(
    *,
    service: CRUDBase[TableModel],
    prefix: str,
    tags: list[str],
    table_model: type[TableModel],      # Asset, Machine, etc. (table=True)
    create_schema: type[CreateSchema],  # AssetCreate
    update_schema: type[UpdateSchema],  # AssetUpdate
    read_schema: type[ReadSchema],      # AssetRead (response)
) -> APIRouter:
```

The base service can use SQLModel's built-in validation:

```python
class CRUDBase(Generic[TableModel, CreateSchema, UpdateSchema]):
    def __init__(self, model: type[TableModel]):
        self.model = model
    
    async def create(self, db: AsyncSession, *, obj_in: CreateSchema) -> TableModel:
        # SQLModel handles validation + ORM in one step
        db_obj = self.model.model_validate(obj_in)
        db.add(db_obj)
        await db.commit()
        return db_obj
```

### Router Updates

Each API router needs to switch from legacy ORM+Pydantic to domain models:

**Before** (`praxis/backend/api/machines.py`):
```python
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.pydantic_internals.machine import MachineCreate, MachineResponse

router.include_router(create_crud_router(
    service=machine_service,
    response_schema=MachineResponse,
    ...
))
```

**After**:
```python
from praxis.backend.models.domain.machine import Machine, MachineCreate, MachineRead

router.include_router(create_crud_router(
    service=machine_service,
    table_model=Machine,
    create_schema=MachineCreate,
    read_schema=MachineRead,
    ...
))
```

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/api/utils/crud_router_factory.py` | Update factory to use SQLModel schemas |
| `praxis/backend/services/utils/crud_base.py` | Update base service for SQLModel |
| `praxis/backend/api/machines.py` | Switch to domain imports |
| `praxis/backend/api/resources.py` | Switch to domain imports |
| `praxis/backend/api/decks.py` | Switch to domain imports |
| `praxis/backend/api/protocols.py` | Switch to domain imports |
| `praxis/backend/api/scheduler.py` | Switch to domain imports |
| `praxis/backend/api/outputs.py` | Switch to domain imports |
| `praxis/backend/api/workcell.py` | Switch to domain imports |

**Reference Files (Read-Only):**

| Path | Pattern Source |
|:-----|:---------------|
| `praxis/backend/api/utils/crud_router_factory.py` | Current factory implementation |
| `praxis/backend/services/utils/crud_base.py` | Current base service |
| `praxis/backend/models/domain/` | New unified models |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands.
- **Backend Path**: `praxis/backend`
- **Backward compatibility**: Keep legacy imports working during transition
- **Type hints**: Ensure Generic types work with SQLModel models

### Sharp Bits / Technical Debt

1. **AsyncSession with SQLModel**: Ensure async operations work correctly
2. **model_validate vs model_dump**: SQLModel uses Pydantic v2 methods
3. **Relationship loading**: May need `selectinload` for eager loading
4. **Response model serialization**: `response_model` in FastAPI uses Pydantic internally

---

## 5. Verification Plan

**Definition of Done:**

1. Router factory works with SQLModel:
   ```bash
   uv run python -c "
   from praxis.backend.api.utils.crud_router_factory import create_crud_router
   from praxis.backend.models.domain.machine import Machine, MachineCreate, MachineRead, MachineUpdate
   print('Factory import OK')
   "
   ```

2. All API routes still work:
   ```bash
   uv run pytest tests/api/ -x -q
   ```

3. OpenAPI schema generates correctly:
   ```bash
   uv run python scripts/generate_openapi.py
   cat praxis/web-client/src/assets/api/openapi.json | head -100
   ```

4. Full API test suite passes:
   ```bash
   uv run pytest tests/api/ -v
   ```

5. Smoke test endpoints:
   ```bash
   uv run pytest tests/api/test_smoke.py -v
   ```

---

## 6. Implementation Steps

1. **Update CRUDBase service**:
   - Accept SQLModel table class
   - Use `model_validate` for creation
   - Ensure async session compatibility

2. **Update create_crud_router**:
   - Accept table_model, create_schema, update_schema, read_schema
   - Update type hints
   - Ensure response serialization works

3. **Update machines.py**:
   - Change imports to domain models
   - Update router factory calls
   - Test machine endpoints

4. **Update resources.py**:
   - Similar pattern to machines

5. **Update decks.py**:
   - Similar pattern

6. **Update remaining routers**:
   - protocols.py, scheduler.py, outputs.py, workcell.py

7. **Run full test suite**:
   ```bash
   uv run pytest tests/api/ -v --tb=short
   ```

8. **Regenerate OpenAPI schema**:
   ```bash
   uv run python scripts/generate_openapi.py
   ```

---

## On Completion

- [ ] Commit changes with message: `refactor(api): update CRUD services and routers for SQLModel`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 5.1 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
- [SQLModel with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/)
