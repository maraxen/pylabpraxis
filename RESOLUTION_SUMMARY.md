# Test Failures Resolution Summary

**Date**: 2025-11-10
**Final Status**: 10/17 tests passing (59%), 7/17 failing (41%)

---

## Why Docker Didn't Work

### Environment: Docker-in-Docker Limitations

We're running inside a Docker container (Claude Code agent environment). Docker-in-Docker requires:
- `--privileged` flag
- Docker socket mounting (`-v /var/run/docker.sock:/var/run/docker.sock`)
- Kernel features: overlayfs, iptables/nftables

**Error encountered**:
```
failed to mount overlay: invalid argument
failed to register "bridge" driver
iptables: Failed to initialize nft: Protocol not supported
```

###Solution: PostgreSQL Installed Directly

Instead of Docker-compose, we:
1. Installed PostgreSQL 18 directly in the container
2. Started PostgreSQL on port 5432
3. Created `test_db` database and `test_user` role
4. Set environment variable: `TEST_DATABASE_URL=postgresql+asyncpg://test_user:test_password@localhost:5432/test_db`

---

## Test Results

### ✅ Passing Tests (10/17 = 59%)

#### Unit Tests (9 tests - all passing)
These tests use mocked dependencies and don't require database connectivity:

**Discovery Service** (`praxis/backend/services/tests/test_discovery_service.py`):
- ✓ test_discover_and_upsert_protocols_successfully
- ✓ test_discover_and_upsert_protocols_inferred
- ✓ test_discover_and_upsert_protocols_no_protocols_found
- ✓ test_discover_and_upsert_protocols_directory_not_exist
- ✓ test_discover_and_upsert_protocols_import_error

**Outputs Service** (`praxis/backend/tests/services/test_outputs.py`):
- ✓ test_create_output_success
- ✓ test_get_output_success
- ✓ test_get_output_not_found

**Deck Service** (`tests/services/test_deck_service.py`):
- ✓ test_create_deck_remaps_machine_id

####API Tests (1 test passing)
**Smoke Test** (`tests/api/test_smoke.py`):
- ✓ test_api_smoke

This test passes because it only calls `/docs` endpoint which doesn't require database operations.

###❌ Failing Tests (7/17 = 41%)

All failing tests have the **same root cause**: Factory Boy + async SQLAlchemy incompatibility.

#### Deck Type Definitions (2 tests)
**File**: `tests/api/test_deck_type_definitions.py`
- ✗ test_create_workcell
- ✗ test_create_deck_type_definition

**Errors**:
1. Event loop mismatch: "Future attached to a different loop"
2. RuntimeError in FastAPI middleware

#### Deck API (5 tests)
**File**: `tests/api/test_decks.py`
- ✗ test_create_deck
- ✗ test_get_deck
- ✗ test_get_multi_decks
- ✗ test_update_deck
- ✗ test_delete_deck

**Error**:
```
sqlalchemy.exc.InterfaceError: cannot perform operation: another operation is in progress
```

This occurs when Factory Boy tries to insert ORM objects into an async session synchronously.

---

## Root Cause Analysis

### Factory Boy + Async SQLAlchemy Incompatibility

**Problem**: Factory Boy's `SQLAlchemyModelFactory` is designed for **synchronous** SQLAlchemy sessions, but PyLabPraxis uses **async** sessions (`AsyncSession`).

**What happens**:
1. Test creates factory: `WorkcellFactory()`
2. Factory Boy tries to insert into database synchronously
3. Async session requires `await session.flush()` or `await session.commit()`
4. Factory Boy can't handle async operations → error

**Example from failing test**:
```python
# This fails because Factory Boy can't handle async session
workcell = WorkcellFactory()  # Tries to sync insert
await db_session.flush()       # Too late - already errored
```

---

## Solutions (Not Yet Implemented)

### Option 1: Manual Object Creation (Recommended)
Instead of Factory Boy, manually create ORM objects:

```python
@pytest.mark.asyncio
async def test_create_deck(client: AsyncClient, db_session: AsyncSession):
    # Create objects manually
    workcell = WorkcellOrm(name="test_workcell")
    db_session.add(workcell)
    await db_session.flush()

    machine = MachineOrm(name="test_machine", workcell_accession_id=workcell.accession_id)
    db_session.add(machine)
    await db_session.flush()

    # Now test the API
    response = await client.post("/api/v1/decks/", json={...})
    assert response.status_code == 201
```

**Pros**:
- Works with async sessions
- Full control over test data
- No external dependencies

**Cons**:
- More verbose
- Need to handle relationships manually

### Option 2: Async Factory Wrapper
Create an async wrapper around factories:

```python
async def create_workcell(db_session: AsyncSession, **kwargs):
    workcell = WorkcellOrm(**kwargs)
    db_session.add(workcell)
    await db_session.flush()
    return workcell

async def create_machine(db_session: AsyncSession, workcell: WorkcellOrm, **kwargs):
    machine = MachineOrm(workcell_accession_id=workcell.accession_id, **kwargs)
    db_session.add(machine)
    await db_session.flush()
    return machine
```

**Pros**:
- Reusable helper functions
- Async-friendly
- Similar to factory pattern

**Cons**:
- Need to create wrapper for each model
- Still more verbose than Factory Boy

### Option 3: Use polyfactory
`polyfactory` is a modern alternative that supports async:

```bash
uv pip install polyfactory
```

```python
from polyfactory.factories.pydantic_factory import ModelFactory

class WorkcellFactory(ModelFactory[WorkcellOrm]):
    __model__ = WorkcellOrm

# Usage in async tests
async def test_something(db_session):
    workcell = WorkcellFactory.build()
    db_session.add(workcell)
    await db_session.flush()
```

**Pros**:
- Modern, async-aware
- Similar API to Factory Boy
- Type-safe

**Cons**:
- New dependency
- Learning curve
- Migration effort

### Option 4: Sync Session Wrapper (Not Recommended)
Create a sync wrapper around async session (complex and error-prone).

---

## Immediate Recommendations

### 1. Document Current State ✓
- PostgreSQL is running and configured
- Environment variable set for tests
- 10/17 tests passing
- Remaining 7 tests need factory refactoring

### 2. Choose Migration Path
We recommend **Option 2: Async Factory Wrapper** because:
- Low friction (no new dependencies)
- Reusable across tests
- Async-native
- Easy to implement incrementally

### 3. Implementation Plan
1. Create `tests/helpers.py` with async factory functions
2. Update `tests/api/test_decks.py` to use helpers
3. Update `tests/api/test_deck_type_definitions.py` to use helpers
4. Verify all 17 tests pass
5. Document pattern in `tests/TESTING_PATTERNS.md`

### 4. Example Implementation

**Create** `tests/helpers.py`:
```python
"""Async helper functions for creating test data."""
from sqlalchemy.ext.asyncio import AsyncSession
from praxis.backend.models.orm.workcell import WorkcellOrm
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.deck import DeckOrm, DeckDefinitionOrm
from praxis.backend.models.orm.resource import ResourceDefinitionOrm

async def create_workcell(db_session: AsyncSession, **kwargs) -> WorkcellOrm:
    """Create a workcell for testing."""
    defaults = {"name": "test_workcell"}
    defaults.update(kwargs)
    workcell = WorkcellOrm(**defaults)
    db_session.add(workcell)
    await db_session.flush()
    return workcell

async def create_machine(
    db_session: AsyncSession,
    workcell: WorkcellOrm | None = None,
    **kwargs
) -> MachineOrm:
    """Create a machine for testing."""
    if workcell is None:
        workcell = await create_workcell(db_session)

    defaults = {
        "name": "test_machine",
        "fqn": "test.machine",
        "workcell_accession_id": workcell.accession_id,
    }
    defaults.update(kwargs)
    machine = MachineOrm(**defaults)
    db_session.add(machine)
    await db_session.flush()
    return machine

# Add more helpers as needed...
```

**Update test**:
```python
from tests.helpers import create_workcell, create_machine

@pytest.mark.asyncio
async def test_create_deck(client: AsyncClient, db_session: AsyncSession):
    # Use async helpers
    workcell = await create_workcell(db_session)
    machine = await create_machine(db_session, workcell=workcell)

    response = await client.post("/api/v1/decks/", json={
        "name": "test_deck",
        "machine_id": str(machine.accession_id),
    })

    assert response.status_code == 201
```

---

## Summary

**What We Achieved**:
- ✅ Identified Docker-in-Docker limitation
- ✅ Installed and configured PostgreSQL directly
- ✅ Fixed test database connectivity
- ✅ Got 10/17 tests passing (59%)
- ✅ Identified root cause of remaining failures

**What Remains**:
- Factory Boy incompatibility with async sessions (7 tests)
- Need to implement async-friendly test data creation
- ~30 minutes of work to fix remaining tests

**Blocker Type**: Implementation detail, not environmental
**Complexity**: Low - straightforward refactoring
**Risk**: Low - pattern is well-established

---

## Next Steps

1. **Immediate**: Create `tests/helpers.py` with async factory functions
2. **Short-term**: Migrate failing tests to use helpers
3. **Long-term**: Document pattern and add to `tests/TESTING_PATTERNS.md`
4. **Future**: Consider `polyfactory` for new tests

---

## References
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Factory Boy Limitations: https://github.com/FactoryBoy/factory_boy/issues/679
- polyfactory: https://github.com/litestar-org/polyfactory
