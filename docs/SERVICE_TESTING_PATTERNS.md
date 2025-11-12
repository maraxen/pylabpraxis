# Service Testing Patterns for PyLabPraxis

**For:** Jules and the development team
**Purpose:** Test business logic at the service layer with reliable, fast tests
**Status:** ✅ READY TO USE - No session sharing issues!

---

## Why Service-Level Testing?

Service tests give you **90% of API test benefits** without the complexity:

✅ **Tests business logic** - Same as API tests
✅ **Uses real database** - Catches SQL/ORM issues
✅ **Fast execution** - No HTTP overhead
✅ **Easy debugging** - Direct Python calls
✅ **No session issues** - Works with existing fixtures
✅ **Same patterns** - You already know these from ORM tests!

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Service Testing Patterns](#service-testing-patterns)
4. [Complete Examples](#complete-examples)
5. [Common Patterns](#common-patterns)
6. [Testing Checklist](#testing-checklist)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Basic Service Test Template

```python
"""Test DeckService CRUD operations."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.deck import DeckOrm
from praxis.backend.services.deck import DeckService
from tests.helpers import create_deck, create_machine

@pytest.mark.asyncio
async def test_deck_service_get(db_session: AsyncSession) -> None:
    """Test retrieving a deck by ID."""
    # 1. SETUP: Create test data
    deck = await create_deck(db_session, name="test_deck")

    # 2. ACT: Call service method
    service = DeckService(DeckOrm)
    result = await service.get(db_session, accession_id=deck.accession_id)

    # 3. ASSERT: Verify result
    assert result is not None
    assert result.name == "test_deck"
    assert result.accession_id == deck.accession_id
```

**That's it!** This tests the exact same business logic as an API test, but:
- No HTTP client needed
- No dependency override issues
- Runs in <1 second
- Easy to debug

---

## Test Structure

### The Three Sections (SETUP / ACT / ASSERT)

Always structure service tests in three clear sections:

```python
@pytest.mark.asyncio
async def test_service_method(db_session: AsyncSession) -> None:
    """Clear docstring explaining what is tested."""

    # 1. SETUP: Create test data and prepare inputs
    deck = await create_deck(db_session)
    update_data = {"name": "new_name"}

    # 2. ACT: Call the service method being tested
    service = DeckService(DeckOrm)
    result = await service.update(db_session, db_obj=deck, obj_in=update_data)

    # 3. ASSERT: Verify results and side effects
    assert result.name == "new_name"
    await db_session.refresh(deck)
    assert deck.name == "new_name"
```

### File Organization

```
tests/
└── services/
    ├── test_deck_service.py          # Deck CRUD tests
    ├── test_machine_service.py       # Machine CRUD tests
    ├── test_resource_service.py      # Resource CRUD tests
    ├── test_scheduler_service.py     # Scheduler business logic tests
    └── test_outputs.py              # Output service tests (already exists!)
```

---

## Service Testing Patterns

### Pattern 1: CREATE (Service Method)

**What it tests:** Service can create new records with validation

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.deck import DeckOrm
from praxis.backend.models.pydantic_internals.deck import DeckCreate
from praxis.backend.services.deck import DeckService
from tests.helpers import create_machine, create_deck_definition


@pytest.mark.asyncio
async def test_deck_service_create(db_session: AsyncSession) -> None:
    """Test creating a deck via DeckService."""
    # 1. SETUP: Create dependencies and input data
    machine = await create_machine(db_session)
    deck_def = await create_deck_definition(db_session)

    deck_data = DeckCreate(
        name="new_deck",
        asset_type="DECK",
        deck_type_id=deck_def.accession_id,
        parent_accession_id=machine.accession_id,
        resource_definition_accession_id=deck_def.resource_definition.accession_id,
    )

    # 2. ACT: Create via service
    service = DeckService(DeckOrm)
    result = await service.create(db_session, obj_in=deck_data)

    # 3. ASSERT: Verify creation
    assert result.name == "new_deck"
    assert result.accession_id is not None
    assert result.parent_machine_accession_id == machine.accession_id
    assert result.deck_type_id == deck_def.accession_id
```

### Pattern 2: GET (Single Record)

**What it tests:** Service can retrieve a single record by ID

```python
@pytest.mark.asyncio
async def test_deck_service_get_existing(db_session: AsyncSession) -> None:
    """Test retrieving an existing deck."""
    # 1. SETUP: Create a deck to retrieve
    deck = await create_deck(db_session, name="findme")

    # 2. ACT: Retrieve via service
    service = DeckService(DeckOrm)
    result = await service.get(db_session, accession_id=deck.accession_id)

    # 3. ASSERT: Verify retrieval
    assert result is not None
    assert result.name == "findme"
    assert result.accession_id == deck.accession_id


@pytest.mark.asyncio
async def test_deck_service_get_nonexistent(db_session: AsyncSession) -> None:
    """Test retrieving a non-existent deck returns None."""
    # 1. SETUP: Generate a UUID that doesn't exist
    from praxis.backend.utils.uuid import uuid7
    fake_id = uuid7()

    # 2. ACT: Try to retrieve non-existent deck
    service = DeckService(DeckOrm)
    result = await service.get(db_session, accession_id=fake_id)

    # 3. ASSERT: Should return None
    assert result is None
```

### Pattern 3: GET_MULTI (List Records)

**What it tests:** Service can list multiple records with filtering

```python
from praxis.backend.models.pydantic_internals.filters import SearchFilters


@pytest.mark.asyncio
async def test_deck_service_get_multi(db_session: AsyncSession) -> None:
    """Test listing multiple decks."""
    # 1. SETUP: Create multiple decks
    machine = await create_machine(db_session)
    deck1 = await create_deck(db_session, machine=machine, name="deck_1")
    deck2 = await create_deck(db_session, machine=machine, name="deck_2")
    deck3 = await create_deck(db_session, machine=machine, name="deck_3")

    # 2. ACT: List all decks
    service = DeckService(DeckOrm)
    filters = SearchFilters()
    results = await service.get_multi(db_session, filters=filters)

    # 3. ASSERT: All decks returned
    assert len(results) >= 3
    names = {deck.name for deck in results}
    assert "deck_1" in names
    assert "deck_2" in names
    assert "deck_3" in names


@pytest.mark.asyncio
async def test_deck_service_get_multi_filtered_by_parent(db_session: AsyncSession) -> None:
    """Test filtering decks by parent machine."""
    # 1. SETUP: Create decks on different machines
    machine1 = await create_machine(db_session, name="machine1")
    machine2 = await create_machine(db_session, name="machine2")
    deck1 = await create_deck(db_session, machine=machine1, name="deck_on_m1")
    deck2 = await create_deck(db_session, machine=machine2, name="deck_on_m2")

    # 2. ACT: Filter by machine1
    service = DeckService(DeckOrm)
    filters = SearchFilters(parent_accession_id=machine1.accession_id)
    results = await service.get_multi(db_session, filters=filters)

    # 3. ASSERT: Only machine1 decks returned
    assert len(results) >= 1
    assert all(d.parent_machine_accession_id == machine1.accession_id for d in results)
    names = {d.name for d in results}
    assert "deck_on_m1" in names
    assert "deck_on_m2" not in names
```

### Pattern 4: UPDATE (Modify Record)

**What it tests:** Service can update existing records

```python
@pytest.mark.asyncio
async def test_deck_service_update(db_session: AsyncSession) -> None:
    """Test updating a deck's attributes."""
    # 1. SETUP: Create a deck to update
    deck = await create_deck(db_session, name="original_name")
    original_id = deck.accession_id

    # 2. ACT: Update via service
    service = DeckService(DeckOrm)
    update_data = {"name": "updated_name"}
    result = await service.update(db_session, db_obj=deck, obj_in=update_data)

    # 3. ASSERT: Verify update
    assert result.name == "updated_name"
    assert result.accession_id == original_id  # ID unchanged

    # Verify persistence
    await db_session.refresh(deck)
    assert deck.name == "updated_name"


@pytest.mark.asyncio
async def test_deck_service_update_multiple_fields(db_session: AsyncSession) -> None:
    """Test updating multiple fields at once."""
    # 1. SETUP
    deck = await create_deck(db_session, name="old_name")

    # 2. ACT: Update multiple fields
    service = DeckService(DeckOrm)
    update_data = {
        "name": "new_name",
        "description": "Updated description",
    }
    result = await service.update(db_session, db_obj=deck, obj_in=update_data)

    # 3. ASSERT
    assert result.name == "new_name"
    assert result.description == "Updated description"
```

### Pattern 5: DELETE (Remove Record)

**What it tests:** Service can delete records

```python
@pytest.mark.asyncio
async def test_deck_service_delete(db_session: AsyncSession) -> None:
    """Test deleting a deck."""
    # 1. SETUP: Create a deck to delete
    deck = await create_deck(db_session, name="to_delete")
    deck_id = deck.accession_id

    # 2. ACT: Delete via service
    service = DeckService(DeckOrm)
    deleted = await service.remove(db_session, accession_id=deck_id)

    # 3. ASSERT: Verify deletion
    assert deleted is not None
    assert deleted.accession_id == deck_id

    # Verify no longer in database
    result = await service.get(db_session, accession_id=deck_id)
    assert result is None


@pytest.mark.asyncio
async def test_deck_service_delete_nonexistent(db_session: AsyncSession) -> None:
    """Test deleting a non-existent deck returns None."""
    # 1. SETUP: Generate fake ID
    from praxis.backend.utils.uuid import uuid7
    fake_id = uuid7()

    # 2. ACT: Try to delete
    service = DeckService(DeckOrm)
    result = await service.remove(db_session, accession_id=fake_id)

    # 3. ASSERT: Returns None (not found)
    assert result is None
```

---

## Complete Examples

### Example 1: Testing DeckService

**File:** `tests/services/test_deck_service.py`

```python
"""Tests for DeckService CRUD operations."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.deck import DeckOrm
from praxis.backend.models.pydantic_internals.deck import DeckCreate
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.services.deck import DeckService
from praxis.backend.utils.uuid import uuid7
from tests.helpers import (
    create_deck,
    create_machine,
    create_deck_definition,
)


@pytest.mark.asyncio
async def test_create_deck_success(db_session: AsyncSession) -> None:
    """Test successfully creating a deck."""
    # SETUP
    machine = await create_machine(db_session)
    deck_def = await create_deck_definition(db_session)

    deck_data = DeckCreate(
        name="test_deck",
        asset_type="DECK",
        deck_type_id=deck_def.accession_id,
        parent_accession_id=machine.accession_id,
        resource_definition_accession_id=deck_def.resource_definition.accession_id,
    )

    # ACT
    service = DeckService(DeckOrm)
    result = await service.create(db_session, obj_in=deck_data)

    # ASSERT
    assert result.name == "test_deck"
    assert result.accession_id is not None
    assert result.parent_machine_accession_id == machine.accession_id


@pytest.mark.asyncio
async def test_get_deck_by_id_exists(db_session: AsyncSession) -> None:
    """Test retrieving an existing deck by ID."""
    # SETUP
    deck = await create_deck(db_session, name="find_me")

    # ACT
    service = DeckService(DeckOrm)
    result = await service.get(db_session, accession_id=deck.accession_id)

    # ASSERT
    assert result is not None
    assert result.name == "find_me"
    assert result.accession_id == deck.accession_id


@pytest.mark.asyncio
async def test_get_deck_by_id_not_found(db_session: AsyncSession) -> None:
    """Test retrieving a non-existent deck returns None."""
    # SETUP
    fake_id = uuid7()

    # ACT
    service = DeckService(DeckOrm)
    result = await service.get(db_session, accession_id=fake_id)

    # ASSERT
    assert result is None


@pytest.mark.asyncio
async def test_get_multi_decks(db_session: AsyncSession) -> None:
    """Test listing multiple decks."""
    # SETUP
    await create_deck(db_session, name="deck1")
    await create_deck(db_session, name="deck2")
    await create_deck(db_session, name="deck3")

    # ACT
    service = DeckService(DeckOrm)
    filters = SearchFilters()
    results = await service.get_multi(db_session, filters=filters)

    # ASSERT
    assert len(results) >= 3
    names = {d.name for d in results}
    assert "deck1" in names
    assert "deck2" in names
    assert "deck3" in names


@pytest.mark.asyncio
async def test_update_deck_name(db_session: AsyncSession) -> None:
    """Test updating a deck's name."""
    # SETUP
    deck = await create_deck(db_session, name="old_name")

    # ACT
    service = DeckService(DeckOrm)
    update_data = {"name": "new_name"}
    result = await service.update(db_session, db_obj=deck, obj_in=update_data)

    # ASSERT
    assert result.name == "new_name"
    await db_session.refresh(deck)
    assert deck.name == "new_name"


@pytest.mark.asyncio
async def test_delete_deck(db_session: AsyncSession) -> None:
    """Test deleting a deck."""
    # SETUP
    deck = await create_deck(db_session, name="to_delete")
    deck_id = deck.accession_id

    # ACT
    service = DeckService(DeckOrm)
    deleted = await service.remove(db_session, accession_id=deck_id)

    # ASSERT
    assert deleted is not None
    assert deleted.accession_id == deck_id

    # Verify deletion
    result = await service.get(db_session, accession_id=deck_id)
    assert result is None
```

### Example 2: Testing Business Logic

**File:** `tests/services/test_scheduler_service.py`

```python
"""Tests for SchedulerService business logic."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.schedule import ScheduleEntryOrm
from praxis.backend.services.scheduler_service import SchedulerService
from tests.factories_schedule import create_schedule_entry


@pytest.mark.asyncio
async def test_update_status_to_running(db_session: AsyncSession) -> None:
    """Test updating schedule entry status to RUNNING."""
    # SETUP
    entry = await create_schedule_entry(
        db_session,
        status="QUEUED"
    )

    # ACT
    service = SchedulerService(ScheduleEntryOrm)
    result = await service.update_status(
        db_session,
        entry_id=entry.accession_id,
        new_status="RUNNING"
    )

    # ASSERT
    assert result.status == "RUNNING"
    assert result.started_at is not None  # Should set timestamp


@pytest.mark.asyncio
async def test_calculate_metrics_for_completed_entries(db_session: AsyncSession) -> None:
    """Test calculating metrics for completed schedule entries."""
    # SETUP
    entry1 = await create_schedule_entry(db_session, status="COMPLETED", duration_ms=1000)
    entry2 = await create_schedule_entry(db_session, status="COMPLETED", duration_ms=2000)
    entry3 = await create_schedule_entry(db_session, status="FAILED", duration_ms=500)

    # ACT
    service = SchedulerService(ScheduleEntryOrm)
    metrics = await service.calculate_metrics(db_session, status="COMPLETED")

    # ASSERT
    assert metrics["count"] == 2
    assert metrics["avg_duration_ms"] == 1500  # (1000 + 2000) / 2
    assert metrics["total_duration_ms"] == 3000
```

---

## Common Patterns

### Testing with Relationships

```python
@pytest.mark.asyncio
async def test_deck_with_parent_machine(db_session: AsyncSession) -> None:
    """Test deck includes parent machine relationship."""
    # SETUP
    machine = await create_machine(db_session, name="parent_machine")
    deck = await create_deck(db_session, machine=machine, name="child_deck")

    # ACT
    service = DeckService(DeckOrm)
    result = await service.get(db_session, accession_id=deck.accession_id)

    # ASSERT
    assert result.parent_machine is not None
    assert result.parent_machine.name == "parent_machine"
    assert result.parent_machine_accession_id == machine.accession_id
```

### Testing Error Cases

```python
@pytest.mark.asyncio
async def test_create_deck_with_invalid_parent(db_session: AsyncSession) -> None:
    """Test creating deck with non-existent parent raises error."""
    # SETUP
    from praxis.backend.utils.uuid import uuid7
    deck_def = await create_deck_definition(db_session)

    fake_machine_id = uuid7()
    deck_data = DeckCreate(
        name="orphan_deck",
        asset_type="DECK",
        deck_type_id=deck_def.accession_id,
        parent_accession_id=fake_machine_id,  # Doesn't exist!
        resource_definition_accession_id=deck_def.resource_definition.accession_id,
    )

    # ACT & ASSERT
    service = DeckService(DeckOrm)
    with pytest.raises(Exception):  # Could be IntegrityError, etc.
        await service.create(db_session, obj_in=deck_data)
```

### Testing Filtering and Pagination

```python
@pytest.mark.asyncio
async def test_get_multi_with_pagination(db_session: AsyncSession) -> None:
    """Test listing decks with pagination."""
    # SETUP: Create 10 decks
    for i in range(10):
        await create_deck(db_session, name=f"deck_{i:02d}")

    # ACT: Get first page (limit 5)
    service = DeckService(DeckOrm)
    filters = SearchFilters(limit=5, offset=0)
    page1 = await service.get_multi(db_session, filters=filters)

    # ACT: Get second page (limit 5, offset 5)
    filters = SearchFilters(limit=5, offset=5)
    page2 = await service.get_multi(db_session, filters=filters)

    # ASSERT
    assert len(page1) == 5
    assert len(page2) >= 5

    # Pages should not overlap
    page1_ids = {d.accession_id for d in page1}
    page2_ids = {d.accession_id for d in page2}
    assert len(page1_ids & page2_ids) == 0  # No overlap
```

### Testing with JSONB Fields

```python
@pytest.mark.asyncio
async def test_update_deck_properties(db_session: AsyncSession) -> None:
    """Test updating JSONB properties field."""
    # SETUP
    deck = await create_deck(db_session, name="test_deck")

    # ACT
    service = DeckService(DeckOrm)
    update_data = {
        "properties_json": {
            "color": "blue",
            "capacity": 96,
            "barcode": "ABC123"
        }
    }
    result = await service.update(db_session, db_obj=deck, obj_in=update_data)

    # ASSERT
    assert result.properties_json is not None
    assert result.properties_json["color"] == "blue"
    assert result.properties_json["capacity"] == 96
```

---

## Testing Checklist

When writing service tests, ensure you cover:

### CRUD Operations
- [ ] Create with valid data
- [ ] Create with invalid data (should fail)
- [ ] Get existing record
- [ ] Get non-existent record (returns None)
- [ ] Get multiple records (list)
- [ ] Update existing record
- [ ] Update non-existent record
- [ ] Delete existing record
- [ ] Delete non-existent record

### Business Logic
- [ ] Status transitions work correctly
- [ ] Calculations produce correct results
- [ ] Timestamps are set automatically
- [ ] Defaults are applied
- [ ] Validations work

### Relationships
- [ ] Parent relationships are loaded
- [ ] Child relationships are loaded
- [ ] Cascade deletes work (if applicable)
- [ ] Orphan removal works (if applicable)

### Edge Cases
- [ ] Empty results (no data)
- [ ] Large datasets (pagination)
- [ ] Concurrent operations
- [ ] Null/None values handled
- [ ] JSONB field operations

---

## Troubleshooting

### Issue: "MissingGreenlet" Error

**Error:**
```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called
```

**Cause:** Trying to access a relationship without awaiting

**Fix:**
```python
# Bad
deck.parent_machine.name  # Error!

# Good
await db_session.refresh(deck, ["parent_machine"])
deck.parent_machine.name  # Works!

# Or in service method, use joinedload:
stmt = select(DeckOrm).options(joinedload(DeckOrm.parent_machine))
```

### Issue: "DetachedInstanceError"

**Error:**
```
sqlalchemy.orm.exc.DetachedInstanceError: Instance is not bound to a Session
```

**Cause:** Trying to access an object after session is closed

**Fix:**
```python
# Ensure object is in session
await db_session.refresh(deck)
```

### Issue: Test Passes But Data Not Persisted

**Cause:** Transaction rollback (this is expected!)

**Remember:** Tests use transaction rollback for isolation. Data won't be in DB after test completes. This is GOOD - it's how test isolation works.

### Issue: Unique Constraint Violation

**Error:**
```
sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint
```

**Cause:** Creating objects with same unique field (e.g., name)

**Fix:**
```python
# Generate unique names per test
import uuid

deck = await create_deck(db_session, name=f"deck_{uuid.uuid4().hex[:8]}")
```

---

## Running Service Tests

```bash
# Set database URL
export TEST_DATABASE_URL="postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"

# Run all service tests
python -m pytest tests/services/ -v

# Run specific service tests
python -m pytest tests/services/test_deck_service.py -v

# Run specific test
python -m pytest tests/services/test_deck_service.py::test_create_deck_success -v

# Run with output
python -m pytest tests/services/test_deck_service.py -vv -s

# Run with coverage
python -m pytest tests/services/ --cov=praxis.backend.services --cov-report=term-missing
```

---

## Next Steps

1. **Start with one service** - Pick DeckService, MachineService, or ResourceService
2. **Copy the template** - Use the complete example above
3. **Test CRUD operations** - Cover all 5 operations (Create, Get, Get Multi, Update, Delete)
4. **Add business logic tests** - Test any special methods or calculations
5. **Run tests frequently** - `python -m pytest tests/services/test_deck_service.py -v`
6. **Achieve >90% coverage** - Service layer should have excellent coverage

---

## Comparison: Service vs API Tests

| Aspect | Service Tests | API Tests |
|--------|--------------|-----------|
| **Speed** | ⚡ Very Fast (<100ms) | 🐌 Slower (HTTP overhead) |
| **Reliability** | ✅ Very Reliable | ⚠️ Session issues |
| **Setup** | ✅ Simple | ❌ Complex |
| **Coverage** | ✅ Business logic | ✅ Business logic + HTTP |
| **Debugging** | ✅ Easy | ⚠️ Harder |
| **Isolation** | ✅ Excellent | ⚠️ Can have issues |
| **When to use** | ✅ **ALWAYS START HERE** | Later, for E2E validation |

**Recommendation:** Write service tests for all business logic. Add API tests later for end-to-end validation once session issues are resolved.

---

## Resources

- **Working Example:** `tests/services/test_outputs.py` (3 passing tests)
- **Async Helpers:** `tests/helpers.py` (create_deck, create_machine, etc.)
- **Service Implementations:** `praxis/backend/services/` (deck.py, machine.py, etc.)
- **ORM Models:** `praxis/backend/models/orm/` (deck.py, machine.py, etc.)

---

**Questions?** Refer to this guide or check existing service tests for patterns!

**Happy Testing!** 🚀
