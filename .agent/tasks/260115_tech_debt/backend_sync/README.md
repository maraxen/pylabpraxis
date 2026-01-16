# Task: Backend Test & File Sync

**ID**: TD-301
**Status**: ✅ Completed
**Priority**: P2
**Difficulty**: Medium

---

## 📋 Phase 1: Inspection (I)

**Objective**: Identify all backend tests/files affected by recent schema changes.

- [x] Search for `_json` suffix usage in tests
- [x] Search for `ProtocolRunRead` field references
- [x] Identify repositories/services using old field names
- [x] List all failing tests related to schema changes

**Findings**:
> **Issue Found**: Two protocol_runs API tests failing with "MissingGreenlet" error
> - `test_get_protocol_run` - FAILED
> - `test_update_protocol_run` - FAILED
>
> **Root Cause**: `ProtocolRun` model has a `@property protocol_name` that accesses lazy-loaded relationship `top_level_protocol_definition`. When FastAPI serializes `ProtocolRun` → `ProtocolRunRead`, it accesses this property outside async context, causing MissingGreenlet error.
>
> **`_json` suffix**: 348 instances found in tests - all are legitimate JSONB column names that should have `_json` suffix per SQLModel schema alignment. No issues with naming conventions.

---

## 📐 Phase 2: Planning (P)

**Objective**: Define systematic update strategy.

- [x] Catalog all field name changes (old → new)
- [x] Map affected files
- [x] Order updates to avoid cascade failures

**Implementation Plan**:

1. ~~Update model imports/references~~ - No changes needed
2. ~~Update test fixtures and mocks~~ - No changes needed
3. **Add eager loading to ProtocolRunService** - Main fix needed
4. Override `get()` to use `selectinload(ProtocolRun.top_level_protocol_definition)`
5. Override `update()` to re-query with eager loading after update

**Definition of Done**:

1. ✅ All backend tests pass
2. ✅ No MissingGreenlet errors on ProtocolRun serialization
3. ✅ Consistent eager loading for protocol_name access

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement schema alignment updates.

- [x] Override `get()` in ProtocolRunService with eager loading
- [x] Override `update()` in ProtocolRunService with eager loading
- [x] Test both methods return objects safe for serialization

**Work Log**:

- 2026-01-16: Added `get()` override to `ProtocolRunService` (praxis/backend/services/protocols.py:62-74)
  - Uses `selectinload(ProtocolRun.top_level_protocol_definition)`
  - Prevents MissingGreenlet error when accessing `protocol_name` property
- 2026-01-16: Added `update()` override to `ProtocolRunService` (praxis/backend/services/protocols.py:76-93)
  - Calls parent `update()` then re-queries with eager loading
  - Ensures updated objects are safe for serialization
- **Note**: `get_multi()` already had eager loading configured with `joinedload()`

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Full test suite verification.

- [x] Fixed tests: `tests/api/test_protocol_runs.py` - All 5 tests passing
- [x] Verified: No MissingGreenlet errors
- [x] Confirmed: `_json` suffix usage is correct throughout codebase

**Results**:
> **All protocol_runs tests passing**: 5/5 ✅
> - test_create_protocol_run PASSED
> - test_get_protocol_run PASSED ⬅ Previously failing
> - test_get_multi_protocol_runs PASSED
> - test_update_protocol_run PASSED ⬅ Previously failing
> - test_delete_protocol_run PASSED
>
> **Solution**: Added eager loading for `top_level_protocol_definition` relationship in `ProtocolRunService.get()` and `ProtocolRunService.update()` methods

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Technical Debt ID**: 301
- **Files**:
  - `praxis/backend/` - Backend code
  - `tests/backend/` - Backend tests
