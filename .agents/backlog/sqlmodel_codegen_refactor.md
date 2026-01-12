# SQLModel + OpenAPI Codegen Unification Refactor

> **Status**: Planning  
> **Priority**: High  
> **Estimated Prompts**: 17

A phased migration from 4 sources of truth (SQLAlchemy ORM + Pydantic + TypeScript interfaces + services) to 1.5 sources of truth using SQLModel for unified backend models and OpenAPI Generator for auto-generated frontend code.

---

## 📁 Archived Items

Phases 1, 2.1, 5.1, 6.1, and 6.2 have been archived.
See: [sqlmodel_openapi_migration.md](../archive/sqlmodel_openapi_migration.md)

---

---

## Phase 2: Model Migration — Core Entities (4 prompts)

### 2.1 — Migrate `Asset` polymorphic base (✅ Done)

- [x] Archived. See above.

### 2.2 — Migrate `Machine` + `MachineDefinition`

- Unify `praxis/backend/models/orm/machine.py` + `praxis/backend/models/pydantic_internals/machine.py`
- `Machine(Asset, table=True)` inherits polymorphically from unified Asset
- Create `MachineDefinitionBase`, `MachineDefinition(table=True)`, CRUD schemas
- Update `praxis/backend/api/v1/machines.py`
- **Tests**: `pytest tests/backend/models/orm/test_machine*.py tests/backend/models/pydantic/test_machine*.py tests/backend/api/v1/test_machines.py`

### 2.3 — Migrate `Resource` + `ResourceDefinition`

- Same pattern as Machine for `praxis/backend/models/orm/resource.py` + Pydantic
- Handle `properties_json`, `dimensions_json` JSON columns
- Update `praxis/backend/api/v1/resources.py`
- **Tests**: `pytest tests/backend/models/orm/test_resource*.py tests/backend/models/pydantic/test_resource*.py tests/backend/api/v1/test_resources.py`

### 2.4 — Migrate `Deck` + `DeckDefinition` + `DeckPositionDefinition`

- Unify `praxis/backend/models/orm/deck.py` + `praxis/backend/models/pydantic_internals/deck.py`
- Handle nested relationships (`DeckPositionDefinition` → `DeckDefinition`)
- Update `praxis/backend/api/v1/decks.py`
- **Tests**: `pytest tests/backend/models/orm/test_deck*.py tests/backend/models/pydantic/test_deck*.py tests/backend/api/v1/test_deck*.py`

---

## Phase 3: Model Migration — Protocol & Scheduling (3 prompts)

### 3.1 — Migrate `ProtocolRun` + related entities

- Unify `praxis/backend/models/orm/protocol_run.py` + `praxis/backend/models/pydantic_internals/protocol_run.py`
- Include `FunctionCallLog`, `AssetRequirement`, `ParameterDefinition`
- Handle complex JSON fields (`parameters`, `arguments`, `result`)
- **Tests**: `pytest tests/backend/models/orm/test_protocol_run*.py tests/backend/models/orm/test_function_call*.py tests/backend/api/v1/test_protocol*.py`

### 3.2 — Migrate `Schedule` + `ScheduleEntry` + `ScheduleHistory` + `AssetReservation`

- Unify `praxis/backend/models/orm/scheduler.py` + `praxis/backend/models/pydantic_internals/scheduler.py`
- Preserve `AssetReservation` relationship to unified Asset
- **Note**: Resolve `asset_reservations` relationship conflict in `Asset` model (currently commented out) when migrating this entity
- **Tests**: `pytest tests/backend/models/orm/test_schedule*.py tests/backend/models/orm/test_asset_reservation*.py tests/backend/api/v1/test_scheduler*.py`

### 3.3 — Migrate `ProtocolSource` (Repository + FileSystem)

- Unify `praxis/backend/models/orm/protocol_source.py` + Pydantic
- Handle polymorphic inheritance (`FileSystemProtocolSource`, `ProtocolSourceRepository`)
- **Tests**: `pytest tests/backend/models/orm/test_*protocol_source*.py`

---

## Phase 4: Model Migration — Data & Supporting (2 prompts)

### 4.1 — Migrate `FunctionDataOutput` + `WellDataOutput`

- Unify `praxis/backend/models/orm/function_data_output.py` + `praxis/backend/models/pydantic_internals/data_output.py`
- Handle `well_data` JSON and nested `WellDataOutput` relationship
- **Tests**: `pytest tests/backend/models/orm/test_*data_output*.py tests/backend/api/v1/test_*data_output*.py`

### 4.2 — Migrate `Workcell` + `User`

- Unify `praxis/backend/models/orm/workcell.py` + `praxis/backend/models/pydantic_internals/workcell.py`
- Unify `praxis/backend/models/orm/user.py` + `praxis/backend/models/pydantic_internals/user.py`
- **Tests**: `pytest tests/backend/models/orm/test_workcell*.py tests/backend/models/orm/test_user*.py tests/backend/api/v1/test_workcells.py`

---

## Phase 5: Infrastructure Updates (2 prompts)

### 5.1 — Update CRUD services and router factory (✅ Done)

- [x] Archived. See above.

### 5.2 — Update test factories and fixtures

- Refactor `tests/conftest.py` database fixtures for SQLModel
- Update `tests/factories.py` to use unified models
- Update `tests/helpers.py` entity creation helpers
- **Tests**: `pytest tests/` (full test suite)

---

## Phase 6: Frontend Migration (2 prompts)

### 6.1 — Generate and integrate TypeScript client (✅ Done)

- [x] Archived. See above.

### 6.2 — Migrate Angular services to generated client (✅ Done)

- [x] Archived. See above.

---

## Phase 7: Cleanup & Validation (2 prompts)

### 7.1 — Unified Model Migration (Pivot: Table-Per-Class)

- **Pivot Decision (2025-01-12)**: Joined Table Inheritance (JTI) in SQLModel is unstable for JSON fields. We are pivoting to **Table-Per-Class** (Abstract Base) inheritance.
  - Parent `Asset` will be `table=False` (Abstract).
  - Children `Machine`, `Resource` will be `table=True` (Concrete Tables).
  - The shared `assets` table will be removed.
- **Database Implication**: `AssetReservation` can no longer have a physical Foreign Key to `assets.id`.
  - **Solution**: Use "Soft" Foreign Keys. Remove the SQL constraint but keep the indexed `asset_id` column. Rely on UUID7 global uniqueness for application-level integrity.
- **Action Items**:
  - [ ] Consolidate `orm/` and `domain/` into a single `models/` directory (renaming `domain/` to `models/` effectively).
  - [ ] Refactor `Asset` to `table=False`.
  - [ ] Refactor `Machine`, `Resource` to inherit from `Asset` with `table=True`.
  - [ ] Update `AssetReservation` to remove FK constraint.
  - [ ] Delete `praxis/backend/models/orm/` directory.
  - [ ] Update all imports.
- **Tests**: Full test suite validation.

### 7.2 — Final review: Alembic migration + full integration test

- Generate Alembic migration to verify SQLModel metadata compatibility
- Run `alembic upgrade head` against test database
- Execute full test suite: `pytest tests/ -v --cov`
- Verify OpenAPI schema matches expectations
- Run `npm run generate-api && ng build` to confirm pipeline

---

## Design Decisions

### 1. SQLModel JSON field handling

SQLModel has quirks with complex `sa_column=Column(JSON)` types. Create a reusable `JsonVariant` SQLModel-compatible type in Phase 1.

### 2. Polymorphic inheritance

`Asset` → `Machine`/`Resource` uses SQLAlchemy's `polymorphic_on`. Phase 2.1 is intentionally first to prototype this pattern.

#### 2025-01-12 Discovery: Potential Fix for SQLModel Inheritance Bug

**Problem:** SQLModel cannot inherit from parent classes with `dict` fields using `sa_column=Column(JSON)`. The `sa_column` config doesn't inherit, causing `ValueError: <class 'dict'> has no matching SQLAlchemy type`.

**Root Cause:** SQLModel's metaclass re-resolves field types during inheritance. `sa_column` is class-specific and doesn't propagate to children.

**Potential Fix:** Use `sa_type=JsonVariant` instead of `sa_column=Column(JsonVariant)`. The `sa_type` parameter is designed to be inheritable.

```python
# Instead of:
properties_json: dict[str, Any] | None = Field(sa_column=Column(JsonVariant), default=None)

# Use:
properties_json: dict[str, Any] | None = Field(sa_type=JsonVariant, default=None)
```

**References:**

- [GitHub Discussion #1346](https://github.com/fastapi/sqlmodel/discussions/1346)
- [GitHub Discussion #1051](https://github.com/fastapi/sqlmodel/discussions/1051)
- [GitHub Issue #469](https://github.com/fastapi/sqlmodel/issues/469)

**Codebase Analysis (2025-01-12):**

- Polymorphic queries (`select(AssetOrm)` returning mixed types) are NOT used
- All queries target specific subtypes: `select(MachineOrm)`, `select(ResourceOrm)`
- `AssetReservation.asset` relationship exists but is never navigated in code
- Polymorphism may be unnecessary, but fixing the inheritance enables full SQLModel unification

**Status:** Prototype needed to validate `sa_type` approach works with joined table inheritance.

### 3. Frontend codegen tool

Starting with `openapi-typescript-codegen` for simplicity. Can switch to `orval` later if Angular-specific features needed.

### 4. Incremental vs big-bang migration

Batch Alembic migrations in Phase 7 since table structure shouldn't change—only Python class definitions.

---

## Files Affected

### Backend (to unify/replace)

- `praxis/backend/models/orm/*.py` (10+ files)
- `praxis/backend/models/pydantic_internals/*.py` (10+ files)
- `praxis/backend/api/v1/*.py` (router imports)
- `praxis/backend/api/crud_router.py`
- `praxis/backend/services/base_service.py`
- `alembic/env.py`
- `pyproject.toml`

### Frontend (to generate/replace)

- `frontend/src/app/features/*/models/*.ts`
- `frontend/src/app/features/*/services/*.ts`
- `frontend/package.json`
- `scripts/generate_openapi.py`

### Tests (to update)

- `tests/backend/models/orm/*.py` (19 files)
- `tests/backend/models/pydantic/*.py` (7 files)
- `tests/conftest.py`
- `tests/factories.py`
- `tests/helpers.py`
