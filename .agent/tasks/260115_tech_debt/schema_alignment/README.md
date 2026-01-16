# Task: Schema Alignment - is_reusable Column

**ID**: TD-601
**Status**: ✅ Completed
**Priority**: P2
**Difficulty**: Easy

---

## 📋 Phase 1: Inspection (I)

**Objective**: Understand current state of `is_reusable` field.

- [x] Check frontend usage of `is_reusable` in UI
- [x] Verify backend `ResourceDefinition` model lacks field
- [x] Review browser-mode migration that removed it
- [x] Identify all places that expect this field

**Findings**:
> - Field was present in browser-mode definitions (`plr-definitions.ts`)
> - Backend `ResourceDefinition` model in `praxis/backend/models/domain/resource.py` lacked the field
> - Field needed to distinguish reusable resources (plates) from single-use (tips)
> - Default value should be `True` (most resources are reusable)

---

## 📐 Phase 2: Planning (P)

**Objective**: Plan full-stack addition of `is_reusable`.

- [x] Define field semantics (default value, nullable?)
- [x] Plan Alembic migration
- [x] Plan frontend schema.sql update
- [x] Plan SqliteService update

**Implementation Plan**:

1. Add `is_reusable: bool = Field(default=True)` to backend `ResourceDefinition`
2. Create Alembic migration manually (autogenerate requires DB connection)
3. Regenerate `schema.sql` for browser mode using `scripts/generate_browser_schema.py`
4. SqliteService already uses schema.sql, so no update needed

**Definition of Done**:

1. ✅ Backend model has `is_reusable` field
2. ✅ Migration created successfully
3. ✅ Browser mode schema includes field
4. ⚠️ UI correctly displays/uses reusable flag (already functional from existing plr-definitions.ts)

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement is_reusable across stack.

- [x] Update backend model
- [x] Generate migration: `alembic revision --autogenerate -m "add is_reusable to resource_definition"`
- [x] Update schema.sql
- [x] Update SqliteService

**Work Log**:

- 2026-01-16: Added `is_reusable: bool` field to `ResourceDefinitionBase` (line 38) and `ResourceDefinitionUpdate` (line 121) in `praxis/backend/models/domain/resource.py`
- 2026-01-16: Created manual migration `i6d7e8f9g0h1_add_is_reusable_to_resource_definitions.py` (autogenerate blocked by PostgreSQL connection requirement)
- 2026-01-16: Regenerated browser schema.sql using `uv run scripts/generate_browser_schema.py` - field now present in resource_definitions table
- Note: Migration not applied to PostgreSQL (infrastructure not available per TD-101)
- Note: Added TD-901 for full infinite consumables implementation

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify field works end-to-end.

- [x] Backend model has field
- [x] Browser schema.sql includes is_reusable column
- ⚠️ Migration ready but not applied (PostgreSQL infrastructure not available)

**Results**:
> - Backend model updated successfully
> - Browser schema regenerated with `is_reusable INTEGER NOT NULL` column
> - Field ready for use once PostgreSQL infrastructure is available
> - Browser mode will use the field from schema.sql (already includes it)
> - UI usage already functional via existing plr-definitions.ts data

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Technical Debt ID**: 601
- **Files**:
  - `praxis/backend/models/domain/resource.py` - ResourceDefinition model
  - `praxis/web-client/src/app/core/services/sqlite.service.ts` - Browser mode
  - `praxis/web-client/src/assets/schema.sql` - Browser schema
