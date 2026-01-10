# SQLModel + OpenAPI Codegen Unification Refactor

> **Status**: Planning  
> **Priority**: High  
> **Estimated Prompts**: 17

A phased migration from 4 sources of truth (SQLAlchemy ORM + Pydantic + TypeScript interfaces + services) to 1.5 sources of truth using SQLModel for unified backend models and OpenAPI Generator for auto-generated frontend code.

---

## Phase 1: Foundation Setup (2 prompts)

### 1.1 — Add SQLModel dependency and base infrastructure (✅ Done)

- Add `sqlmodel>=0.0.22` to `pyproject.toml`
- Create `praxis/backend/models/sqlmodel_base.py` with unified `PraxisBase(SQLModel)` that combines `BaseOrm` metadata (accession_id UUID7, timestamps) with Pydantic config
- Update `alembic/env.py` to import SQLModel metadata alongside existing ORM metadata
- **Tests**: `pytest tests/backend/models/orm/ -k "base"`

### 1.2 — Setup frontend OpenAPI codegen pipeline (✅ Done)

- Add `openapi-typescript-codegen` to `frontend/package.json` devDependencies
- Create `npm run generate-api` script targeting `src/app/core/api-generated/`
- Update `scripts/generate_openapi.py` to output to frontend assets
- Create `.openapi-generator-ignore` for custom overrides
- **Tests**: Run generation, verify TypeScript compiles

---

## Phase 2: Model Migration — Core Entities (4 prompts)

### 2.1 — Migrate `Asset` polymorphic base

- Unify `praxis/backend/models/orm/asset.py` + `praxis/backend/models/pydantic_internals/asset.py` into `praxis/backend/models/domain/asset.py`
- Create `AssetBase(SQLModel)`, `Asset(AssetBase, table=True)`, `AssetCreate`, `AssetRead`, `AssetUpdate`
- Preserve polymorphic inheritance (`polymorphic_on="asset_type"`)
- Update imports in `praxis/backend/api/v1/`
- **Tests**: `pytest tests/backend/models/orm/test_asset_orm.py tests/backend/models/pydantic/test_asset_pydantic.py tests/backend/api/v1/test_machines.py`

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

### 5.1 — Update CRUD services and router factory

- Refactor `praxis/backend/api/crud_router.py` to use SQLModel schemas
- Update `praxis/backend/services/base_service.py` for SQLModel compatibility
- Ensure `model_config = {"from_attributes": True}` works with SQLModel
- **Tests**: `pytest tests/backend/api/v1/` (full API test suite)

### 5.2 — Update test factories and fixtures

- Refactor `tests/conftest.py` database fixtures for SQLModel
- Update `tests/factories.py` to use unified models
- Update `tests/helpers.py` entity creation helpers
- **Tests**: `pytest tests/` (full test suite)

---

## Phase 6: Frontend Migration (2 prompts)

### 6.1 — Generate and integrate TypeScript client

- Run `npm run generate-api` to create `frontend/src/app/core/api-generated/`
- Delete manual interfaces from `frontend/src/app/features/assets/models/asset.models.ts`, `frontend/src/app/features/protocols/models/protocol.models.ts`
- Update imports across feature modules
- **Tests**: `ng build --configuration=production`

### 6.2 — Migrate Angular services to generated client

- Replace manual HTTP calls in `frontend/src/app/features/assets/services/asset.service.ts`, `frontend/src/app/features/protocols/services/protocol.service.ts`
- Use generated `PraxisClient` service methods
- Update signal stores to use generated types
- **Tests**: `ng test`, `ng e2e` (if available)

---

## Phase 7: Cleanup & Validation (2 prompts)

### 7.1 — Remove legacy model files and update documentation

- Delete deprecated files from `praxis/backend/models/orm/`, `praxis/backend/models/pydantic_internals/`
- Update `CONTRIBUTING.md` with new model creation workflow
- Update relevant docs in `docs/` folder
- **Tests**: `pytest tests/` (full suite)

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
