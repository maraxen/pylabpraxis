# Task: Schema Alignment - is_reusable Column

**ID**: TD-601
**Status**: ⚪ Not Started
**Priority**: P2
**Difficulty**: Easy

---

## 📋 Phase 1: Inspection (I)

**Objective**: Understand current state of `is_reusable` field.

- [ ] Check frontend usage of `is_reusable` in UI
- [ ] Verify backend `ResourceDefinition` model lacks field
- [ ] Review browser-mode migration that removed it
- [ ] Identify all places that expect this field

**Findings**:
> [To be captured during inspection]

---

## 📐 Phase 2: Planning (P)

**Objective**: Plan full-stack addition of `is_reusable`.

- [ ] Define field semantics (default value, nullable?)
- [ ] Plan Alembic migration
- [ ] Plan frontend schema.sql update
- [ ] Plan SqliteService update

**Implementation Plan**:

1. Add `is_reusable: bool = False` to backend `ResourceDefinition`
2. Generate Alembic migration
3. Regenerate `schema.sql` for browser mode
4. Update `SqliteService` INSERT statements
5. Enable UI usage

**Definition of Done**:

1. Backend model has `is_reusable` field
2. Migration applied successfully
3. Browser mode schema includes field
4. UI correctly displays/uses reusable flag

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement is_reusable across stack.

- [ ] Update backend model
- [ ] Generate migration: `alembic revision --autogenerate -m "add is_reusable to resource_definition"`
- [ ] Apply migration: `alembic upgrade head`
- [ ] Update schema.sql
- [ ] Update SqliteService

**Work Log**:

- [Pending]

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify field works end-to-end.

- [ ] Backend tests pass
- [ ] Browser mode: Create resource, verify `is_reusable` persists
- [ ] UI displays reusable indicator correctly

**Results**:
> [To be captured]

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Technical Debt ID**: 601
- **Files**:
  - `praxis/backend/models/domain/resource.py` - ResourceDefinition model
  - `praxis/web-client/src/app/core/services/sqlite.service.ts` - Browser mode
  - `praxis/web-client/src/assets/schema.sql` - Browser schema
