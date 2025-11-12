# API Test Debugging Session Summary

**Date:** 2025-11-12
**Branch:** `claude/fix-api-tests-deck-creation-011CV4FEJWPNYHiS7VKWCDzW`
**Objective:** Debug and fix API tests, then define clear testing patterns for Jules

---

## Environment Setup ✅ COMPLETE

### PostgreSQL Setup
- **Status:** ✅ Running successfully
- **Version:** PostgreSQL 16.10 (Ubuntu)
- **Port:** 5432 (default)
- **Test Database:** `test_db`
- **Test User:** `test_user` / `test_password`
- **Connection String:** `postgresql+asyncpg://test_user:test_password@localhost:5432/test_db`

**Setup Steps Completed:**
1. Started PostgreSQL server using `pg_ctlcluster 16 main start`
2. Fixed SSL key permissions (`/etc/ssl/private/ssl-cert-snakeoil.key`)
3. Created `test_user` with SUPERUSER privileges
4. Created `test_db` database owned by `test_user`

### Python Dependencies
- **Status:** ✅ Installed
- **Method:** `uv pip install --system -e ".[test]"`
- **Key Packages:**
  - pytest 8.4.2
  - pytest-asyncio 1.3.0
  - httpx 0.24.0+
  - sqlalchemy[asyncio] 2.0.44
  - asyncpg 0.27.0+

---

## Bugs Fixed ✅

### 1. Helper Function: Missing `accession_id` Parameter
**Issue:** `TypeError: __init__() missing 1 required keyword-only argument: 'accession_id'`

**Root Cause:**
- `DeckOrm` has `accession_id` marked as `kw_only=True` in SQLAlchemy
- Helper `create_deck()` wasn't providing this required parameter

**Fix:**
```python
# tests/helpers.py
async def create_deck(...):
    if 'accession_id' not in kwargs:
        kwargs['accession_id'] = uuid7()  # ← Added

    deck = DeckOrm(
        name=name,
        accession_id=...,  # Now provided
        ...
    )
```

**Commit:** `e2ef5de`

### 2. Helper Function: Wrong `asset_type`
**Issue:** `SAWarning: Flushing object <DeckOrm> with incompatible polymorphic identity <AssetType.ASSET: 'GENERIC_ASSET'>`

**Root Cause:**
- `AssetOrm` has `asset_type` with default value `AssetType.ASSET`
- `DeckOrm` expects `asset_type=AssetType.DECK` (polymorphic_identity="DECK")
- Helper wasn't explicitly setting the correct asset_type

**Fix:**
```python
# tests/helpers.py
from praxis.backend.models.enums.asset import AssetType

async def create_deck(...):
    deck = DeckOrm(
        name=name,
        asset_type=AssetType.DECK,  # ← Added
        ...
    )

async def create_machine(...):
    machine = MachineOrm(
        name=name,
        asset_type=AssetType.MACHINE,  # ← Added
        ...
    )
```

**Commit:** `e2ef5de`

---

## Current Test Status

### Passing Tests (2/8 = 25%)
1. ✅ `test_api_smoke` - FastAPI app starts and `/docs` returns 200
2. ✅ `test_create_workcell` - Workcell retrieval from session works

### Failing Tests (6/8 = 75%)

#### Issue #1: API Response Missing Field
**Test:** `test_create_deck`
**Status:** 🔴 FAILING
**Error:** `AssertionError: assert None == '019a...'` (parent_accession_id is None in response)

**Details:**
- API successfully creates deck (201 status)
- Deck is saved to database with correct `parent_machine_accession_id`
- **Response serialization issue**: `parent_accession_id` field returns `None` instead of the actual UUID

**Likely Cause:**
Pydantic response model (`DeckResponse`) may not be mapping `parent_machine_accession_id` to `parent_accession_id` correctly, or the relationship isn't being loaded.

#### Issue #2: Session Isolation Problem
**Tests:** `test_get_deck`, `test_get_multi_decks`, `test_update_deck`, `test_delete_deck`
**Status:** 🔴 FAILING
**Error:** `assert 404 == 200` (API can't find test data)

**Details:**
- Test creates deck using `create_deck()` helper
- Deck IS visible when querying directly from `db_session` in test
- Deck is NOT visible to API (returns 404)
- Dependency override IS set correctly: `app.dependency_overrides[get_db] = override_get_db`
- **Override function is NEVER called during API requests** (no debug output)

**Investigation Results:**

```python
# Verified in debug test:
✅ app.dependency_overrides is set
✅ get_db IS in app.dependency_overrides
✅ Override function is correct
✅ Deck found in test session: True
❌ API finds deck: False (404)
❌ override_get_db() never yields during API call
```

**Theories:**
1. **CRUD Router Factory Issue**: Routes may be capturing dependencies at import time before overrides are set
2. **Session Binding Issue**: The `AsyncSession` may not be properly bound to the connection/transaction
3. **FastAPI Dependency Resolution**: The dependency resolver might be using a cached reference to the original `get_db`
4. **Starlette/ASGI Issue**: The `ASGITransport` might be creating a new app context that doesn't see overrides

**Similar Working System:**
- Jules has 31/31 schedule ORM tests passing
- Those tests use `db_session` fixture with transaction rollback
- **KEY DIFFERENCE:** Jules tests ORM directly, not through FastAPI API layer

---

## Next Steps 🔍

### Immediate Investigation (Priority 1)
1. **Compare with Working Tests**
   - Check how other projects handle FastAPI test client + async session sharing
   - Look for examples in FastAPI docs or test suite

2. **Test Alternative Approaches**
   - Try using `TestClient` (sync) instead of `AsyncClient`
   - Try manual dependency injection instead of `app.dependency_overrides`
   - Try creating service instances per-request instead of module-level

3. **Deep Dive into CRUD Router Factory**
   - Check if routes are capturing `get_db` at import time
   - Verify dependency resolution happens at request time
   - Add more debugging to see when dependencies are resolved

### Alternative Patterns to Explore
1. **Service-Level Testing** (bypass API layer)
   - Test services directly with test session
   - Faster, more reliable, better isolation
   - Example: `await DeckService(DeckOrm).get(db_session, deck_id)`

2. **Integration Tests with Real Commits**
   - Don't use transaction rollback
   - Commit data, test API, then clean up
   - Slower but more realistic

3. **Mocked Services**
   - Mock the service layer entirely
   - Test API layer logic independently
   - Won't catch ORM/SQL issues

---

## Key Files Modified

### `/home/user/pylabpraxis/tests/helpers.py`
- Added `accession_id` auto-generation for `create_deck()` and `create_machine()`
- Added correct `asset_type` for polymorphic inheritance
- Import `AssetType` enum

### `/home/user/pylabpraxis/docs/API_TESTING_PATTERNS.md`
- Created comprehensive API testing patterns guide
- **NOTE:** Document written BEFORE fixing session issues
- **TODO:** Update with working patterns once session sharing is resolved

---

## Lessons Learned

### What Works ✅
1. **PostgreSQL Test Database**: Manual setup works when Docker unavailable
2. **Async Helpers**: `tests/helpers.py` pattern works for creating test data
3. **ORM Tests**: Direct ORM testing (like Jules' schedule tests) works reliably
4. **Fixture Structure**: `db_session` with transaction rollback is solid

### What's Challenging ❌
1. **FastAPI Dependency Overrides**: Not working as expected with async sessions
2. **Session Sharing**: Hard to share async session between test and API
3. **CRUD Router Factory**: May be caching dependencies at import time
4. **Debugging Async**: Harder to trace execution flow with async/await

### Best Practices Identified
1. **Always set `asset_type`** explicitly when creating polymorphic ORM instances
2. **Always generate `accession_id`** with `uuid7()` for kw_only fields
3. **Prefer service-level tests** over full API tests for faster feedback
4. **Use clear SETUP/ACT/ASSERT** structure in tests
5. **Document as you go** - this session would be impossible to reconstruct without notes

---

## Recommendations for Jules

### For API Testing
**Status:** ⚠️ BLOCKED - Session sharing issue needs resolution first

**Once Resolved:**
1. Follow patterns in `docs/API_TESTING_PATTERNS.md`
2. Use async helpers from `tests/helpers.py`
3. Always set `asset_type` and `accession_id` correctly
4. Test one endpoint at a time

### For Service Testing (RECOMMENDED NOW)
**Status:** ✅ READY - Can start immediately

**Pattern:**
```python
@pytest.mark.asyncio
async def test_deck_service_get(db_session: AsyncSession) -> None:
    """Test DeckService.get() method."""
    # SETUP: Create test data
    deck = await create_deck(db_session, name="test_deck")

    # ACT: Call service directly
    service = DeckService(DeckOrm)
    result = await service.get(db_session, deck.accession_id)

    # ASSERT: Verify result
    assert result is not None
    assert result.name == "test_deck"
    assert result.accession_id == deck.accession_id
```

**Advantages:**
- No session sharing issues
- Faster execution
- Better isolation
- Easier debugging
- Can start NOW

### For ORM Testing (CONTINUE)
**Status:** ✅ WORKING - Keep doing what you're doing!

Jules' schedule ORM tests (31/31 passing) show this pattern works perfectly. Continue with:
- Direct ORM instantiation
- Relationship testing
- Query pattern testing
- Cascade behavior testing

---

## Environment Variables

```bash
# For running tests
export TEST_DATABASE_URL="postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"

# Run tests
python -m pytest tests/api/test_decks.py -v

# Run with output
python -m pytest tests/api/test_decks.py -vv -s

# Run specific test
python -m pytest tests/api/test_decks.py::test_create_deck -vv
```

---

## References

### Working Test Examples
- `tests/models/test_orm/test_schedule_entry_orm.py` (13 passing)
- `tests/models/test_orm/test_asset_reservation_orm.py` (14 passing)
- `tests/services/test_outputs.py` (3 passing with mocked session)

### Key Files
- `tests/conftest.py` - Session fixtures
- `tests/api/conftest.py` - Client fixture with dependency override
- `tests/helpers.py` - Async test data helpers
- `praxis/backend/api/utils/crud_router_factory.py` - Generic CRUD endpoints
- `praxis/backend/services/deck.py` - Deck service implementation

### Documentation
- `tests/README.md` - Test infrastructure overview
- `tests/TESTING_PATTERNS.md` - General testing patterns
- `JULES_NEXT_STEPS.md` - Jules' task list and progress

---

## Contact / Handoff Notes

**For Next Developer:**

1. **Start Here:** Read "Issue #2: Session Isolation Problem" above
2. **Quick Test:** Run `python -m pytest tests/api/test_decks.py::test_get_deck -vv -s`
3. **Key Question:** Why isn't `app.dependency_overrides[get_db]` being called during API requests?
4. **Workaround:** Focus on service-level tests instead of API tests for now
5. **When Fixed:** Update `docs/API_TESTING_PATTERNS.md` with working patterns

**For Jules:**

1. **Continue ORM Tests:** You're doing great! (31/31 passing)
2. **Try Service Tests:** Use pattern above, should work immediately
3. **Skip API Tests:** Wait for session issue to be resolved
4. **Use Helpers:** `tests/helpers.py` has working patterns for test data creation
5. **Ask Questions:** Refer to this document if you hit similar issues

---

**Session Duration:** ~3 hours
**Lines of Code Changed:** ~10 (but 3 hours of investigation!)
**Tests Fixed:** 0 → Still investigating
**Tests Status:** 2 passing, 6 failing (was 2 passing, 6 failing - helper fixes don't show in results yet due to session issue)

**Next Session Goal:** Resolve session sharing OR pivot to service-level testing patterns
