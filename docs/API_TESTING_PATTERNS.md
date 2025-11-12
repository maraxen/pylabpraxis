# API Testing Patterns for PyLabPraxis

This guide defines the standard patterns for writing API tests in PyLabPraxis. Follow these patterns to ensure consistency, reliability, and maintainability.

## Table of Contents
1. [Test Structure](#test-structure)
2. [Fixtures](#fixtures)
3. [Helper Functions](#helper-functions)
4. [Assertion Patterns](#assertion-patterns)
5. [Common Pitfalls](#common-pitfalls)
6. [Complete Examples](#complete-examples)

---

## Test Structure

All API tests follow the **SETUP / ACT / ASSERT** pattern with clear comments:

```python
@pytest.mark.asyncio
async def test_operation_name(client: AsyncClient, db_session: AsyncSession) -> None:
    """Docstring describing what this test verifies."""

    # 1. SETUP: Create test data and dependencies
    workcell = await create_workcell(db_session, name="test_workcell")
    machine = await create_machine(db_session, workcell=workcell)

    # 2. ACT: Call the API endpoint
    response = await client.post("/api/v1/endpoint", json={...})

    # 3. ASSERT: Verify the response and side effects
    assert response.status_code == 201
    assert response.json()["name"] == "expected_value"
```

### Key Principles:
- **Clear comments** separating SETUP, ACT, and ASSERT sections
- **Descriptive test names** using `test_<verb>_<noun>` format (e.g., `test_create_deck`, `test_get_multi_schedules`)
- **Focused tests** - each test verifies ONE operation or behavior
- **Type hints** on all function parameters and return values

---

## Fixtures

### Core Fixtures (from `tests/conftest.py`)

#### `db_session: AsyncSession`
Provides an async database session for test data setup.

**Key Features:**
- Function-scoped (fresh session for each test)
- Transaction auto-rollback after test (no cleanup needed)
- PostgreSQL-specific (uses JSONB, UUID7, etc.)

**Usage:**
```python
async def test_example(db_session: AsyncSession) -> None:
    # Create test data using helpers
    deck = await create_deck(db_session)

    # Session auto-commits via flush in helpers
    # Auto-rollback happens after test completes
```

#### `client: AsyncClient`
Provides an HTTP client for making API requests.

**Key Features:**
- Overrides app's `get_db()` dependency to use test session
- Same session for test data setup AND API calls (critical!)
- Automatically configured in `tests/api/conftest.py`

**Usage:**
```python
async def test_example(client: AsyncClient) -> None:
    response = await client.get("/api/v1/decks/")
    assert response.status_code == 200
```

### API-Specific Fixtures (from `tests/api/conftest.py`)

The `client` fixture handles the crucial session sharing:

```python
@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Override get_db to use the test session."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session  # Same session as test!

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    del app.dependency_overrides[get_db]
```

**Why This Matters:**
- Test creates data in `db_session`
- API uses same `db_session` via dependency override
- All changes in same transaction → consistent test isolation

---

## Helper Functions

Use async helper functions from `tests/helpers.py` for creating test data.

### Why Not Factory Boy?
Factory Boy only supports **synchronous** sessions. PyLabPraxis uses **async SQLAlchemy**, so we need async helpers.

### Available Helpers

All helpers follow the same pattern:
1. Accept `db_session: AsyncSession` as first parameter
2. Auto-create dependencies if not provided
3. Generate UUIDs using `uuid7()` if not provided
4. Use `db_session.add()` + `await db_session.flush()` to persist
5. Return the created ORM instance

#### `create_workcell()`
```python
async def create_workcell(
    db_session: AsyncSession,
    name: str = "test_workcell",
    **kwargs: Any
) -> WorkcellOrm:
    """Create a workcell for testing."""
```

**Example:**
```python
workcell = await create_workcell(db_session, name="my_workcell")
```

#### `create_machine()`
```python
async def create_machine(
    db_session: AsyncSession,
    workcell: WorkcellOrm | None = None,
    name: str = "test_machine",
    fqn: str = "test.machine",
    **kwargs: Any
) -> MachineOrm:
    """Create a machine for testing."""
```

**Example:**
```python
# Auto-creates workcell
machine = await create_machine(db_session)

# Or pass existing workcell
workcell = await create_workcell(db_session)
machine = await create_machine(db_session, workcell=workcell)
```

#### `create_resource_definition()`
```python
async def create_resource_definition(
    db_session: AsyncSession,
    name: str = "test_resource_definition",
    fqn: str = "test.resource.definition",
    **kwargs: Any
) -> ResourceDefinitionOrm:
    """Create a resource definition for testing."""
```

#### `create_deck_definition()`
```python
async def create_deck_definition(
    db_session: AsyncSession,
    resource_definition: ResourceDefinitionOrm | None = None,
    name: str = "test_deck_definition",
    fqn: str = "test.deck.definition",
    **kwargs: Any
) -> DeckDefinitionOrm:
    """Create a deck definition for testing."""
```

**Example:**
```python
# Auto-creates resource_definition
deck_def = await create_deck_definition(db_session)

# Or pass existing resource_definition
resource_def = await create_resource_definition(db_session)
deck_def = await create_deck_definition(db_session, resource_definition=resource_def)
```

#### `create_deck()`
```python
async def create_deck(
    db_session: AsyncSession,
    machine: MachineOrm | None = None,
    deck_definition: DeckDefinitionOrm | None = None,
    name: str = "test_deck",
    **kwargs: Any
) -> DeckOrm:
    """Create a deck for testing."""
```

**Example:**
```python
# Auto-creates all dependencies (machine, workcell, deck_definition, resource_definition)
deck = await create_deck(db_session)

# Or control dependencies
machine = await create_machine(db_session)
deck_def = await create_deck_definition(db_session)
deck = await create_deck(db_session, machine=machine, deck_definition=deck_def)
```

### Helper Best Practices

1. **Let helpers auto-create dependencies** unless you need to share them across tests:
   ```python
   # Good - simple and clean
   deck = await create_deck(db_session)

   # Only if you need the machine for assertions
   machine = await create_machine(db_session)
   deck = await create_deck(db_session, machine=machine)
   ```

2. **Use kwargs for additional fields**:
   ```python
   deck = await create_deck(
       db_session,
       name="special_deck",
       description="Custom description"
   )
   ```

3. **Don't manually set accession_id** (auto-generated with uuid7):
   ```python
   # Good
   deck = await create_deck(db_session)

   # Bad - unnecessary
   deck = await create_deck(db_session, accession_id=uuid7())
   ```

---

## Assertion Patterns

### HTTP Status Codes

Always assert status code first:

```python
# Create (POST)
assert response.status_code == 201

# Read (GET)
assert response.status_code == 200

# Update (PATCH/PUT)
assert response.status_code == 200

# Delete (DELETE)
assert response.status_code == 200

# Not Found
assert response.status_code == 404

# Validation Error
assert response.status_code == 422
```

### Response Body

Parse JSON once and assert fields:

```python
data = response.json()
assert data["name"] == "expected_name"
assert data["accession_id"] == str(deck.accession_id)  # Convert UUID to string!
```

### Database Verification

For CREATE, UPDATE, DELETE, verify database state:

```python
# After CREATE - verify data persisted
deck = await create_deck(db_session)
response = await client.get(f"/api/v1/decks/{deck.accession_id}")
assert response.status_code == 200
# No need to query DB - API response confirms persistence

# After UPDATE - verify change persisted
response = await client.patch(f"/api/v1/decks/{deck.accession_id}", json={"name": "new_name"})
await db_session.refresh(deck)  # Reload from DB
assert deck.name == "new_name"

# After DELETE - verify record removed
response = await client.delete(f"/api/v1/decks/{deck.accession_id}")
deleted = await db_session.get(DeckOrm, deck.accession_id)
assert deleted is None
```

### List Endpoints

Use `>=` for list sizes (other tests may create data):

```python
# Bad - brittle
assert len(data) == 3

# Good - flexible
assert len(data) >= 3
```

### UUID Comparison

Always convert UUIDs to strings when comparing with JSON:

```python
# Good
assert data["accession_id"] == str(deck.accession_id)

# Bad - will fail
assert data["accession_id"] == deck.accession_id
```

---

## Common Pitfalls

### 1. Missing Required Fields in Helpers

**Problem:** ORM requires fields not set in helper.

**Symptoms:**
```
TypeError: __init__() missing 1 required positional argument: 'parent_accession_id'
```

**Fix:** Update helper to include required field:
```python
# helpers.py
async def create_deck(...) -> DeckOrm:
    deck = DeckOrm(
        name=name,
        deck_type_id=deck_definition.accession_id,
        parent_accession_id=machine.accession_id,  # Add this!
        resource_definition_accession_id=deck_definition.resource_definition.accession_id,
        **kwargs
    )
```

### 2. Field Name Mismatches

**Problem:** API expects `parent_accession_id` but code uses `machine_id`.

**Symptoms:**
```
ValidationError: field required
```

**Fix:** Use correct field name in API call:
```python
# Bad
json={"machine_id": str(machine.accession_id)}

# Good
json={"parent_accession_id": str(machine.accession_id)}
```

### 3. Enum Value Mismatches

**Problem:** Database uses different enum value than code.

**Symptoms:**
```
AssertionError: 'STATUS_CHANGE' != 'STATUS_CHANGED'
```

**Fix:** Check database enum definition and use correct value:
```python
# Check enum
await db_session.execute(text("SELECT unnest(enum_range(NULL::schedule_history_event_type))"))

# Use correct value
event = ScheduleHistoryOrm(event_type=ScheduleHistoryEventType.STATUS_CHANGED)  # Not STATUS_CHANGE
```

### 4. Not Using Async Session

**Problem:** Using sync methods on async session.

**Symptoms:**
```
MissingGreenlet: greenlet_spawn has not been called
```

**Fix:** Always await async session methods:
```python
# Bad
db_session.add(deck)
db_session.flush()

# Good
db_session.add(deck)
await db_session.flush()
```

### 5. Session Not Shared

**Problem:** Test data not visible to API.

**Symptoms:** 404 errors even though data was created.

**Fix:** Ensure `client` fixture overrides `get_db`:
```python
# In tests/api/conftest.py
app.dependency_overrides[get_db] = override_get_db
```

### 6. Hardcoded IDs Instead of Creating Data

**Problem:** Using fake UUIDs that don't exist in DB.

**Symptoms:**
```
404 Not Found
```

**Fix:** Always create actual test data:
```python
# Bad
response = await client.get("/api/v1/decks/00000000-0000-0000-0000-000000000000")

# Good
deck = await create_deck(db_session)
response = await client.get(f"/api/v1/decks/{deck.accession_id}")
```

---

## Complete Examples

### Example 1: Simple CRUD Test

```python
"""Test creating a single resource."""
@pytest.mark.asyncio
async def test_create_workcell(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a workcell via API."""

    # 1. SETUP: Prepare request data
    workcell_data = {
        "name": "production_workcell",
        "description": "Main production workcell"
    }

    # 2. ACT: Call the API
    response = await client.post("/api/v1/workcells/", json=workcell_data)

    # 3. ASSERT: Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "production_workcell"
    assert data["description"] == "Main production workcell"
    assert "accession_id" in data
```

### Example 2: Test with Dependencies

```python
"""Test creating a resource with foreign key dependencies."""
@pytest.mark.asyncio
async def test_create_deck(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a deck via API."""

    # 1. SETUP: Create dependencies
    workcell = await create_workcell(db_session)
    machine = await create_machine(db_session, workcell=workcell)
    resource_definition = await create_resource_definition(db_session)
    deck_type = await create_deck_definition(
        db_session,
        resource_definition=resource_definition
    )

    # 2. ACT: Call the API with all required foreign keys
    response = await client.post(
        "/api/v1/decks/",
        json={
            "name": "test_deck",
            "asset_type": "DECK",
            "deck_type_id": str(deck_type.accession_id),
            "parent_accession_id": str(machine.accession_id),
            "resource_definition_accession_id": str(resource_definition.accession_id),
        },
    )

    # 3. ASSERT: Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_deck"
    assert data["parent_accession_id"] == str(machine.accession_id)
```

### Example 3: GET Test

```python
"""Test retrieving an existing resource."""
@pytest.mark.asyncio
async def test_get_machine(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving a single machine by ID."""

    # 1. SETUP: Create a machine to retrieve
    machine = await create_machine(db_session, name="test_machine")

    # 2. ACT: Call the API
    response = await client.get(f"/api/v1/machines/{machine.accession_id}")

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_machine"
    assert data["accession_id"] == str(machine.accession_id)
```

### Example 4: LIST Test

```python
"""Test retrieving multiple resources."""
@pytest.mark.asyncio
async def test_list_schedules(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving multiple schedules."""

    # 1. SETUP: Create multiple schedules
    await create_schedule(db_session, name="schedule_1")
    await create_schedule(db_session, name="schedule_2")
    await create_schedule(db_session, name="schedule_3")

    # 2. ACT: Call the API
    response = await client.get("/api/v1/schedules/")

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # Use >= because other tests may create schedules

    # Verify all our schedules are present
    names = {item["name"] for item in data}
    assert "schedule_1" in names
    assert "schedule_2" in names
    assert "schedule_3" in names
```

### Example 5: UPDATE Test

```python
"""Test updating an existing resource."""
@pytest.mark.asyncio
async def test_update_deck_name(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test updating a deck's name."""

    # 1. SETUP: Create a deck to update
    deck = await create_deck(db_session, name="original_name")

    # 2. ACT: Call the API with new data
    response = await client.patch(
        f"/api/v1/decks/{deck.accession_id}",
        json={"name": "updated_name"},
    )

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated_name"

    # Verify the change was persisted in the database
    await db_session.refresh(deck)
    assert deck.name == "updated_name"
```

### Example 6: DELETE Test

```python
"""Test deleting a resource."""
@pytest.mark.asyncio
async def test_delete_machine(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test deleting a machine."""

    # 1. SETUP: Create a machine to delete
    machine = await create_machine(db_session, name="machine_to_delete")
    machine_id = machine.accession_id

    # 2. ACT: Call the API to delete
    response = await client.delete(f"/api/v1/machines/{machine_id}")

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["accession_id"] == str(machine_id)

    # Verify the machine is no longer in the database
    deleted = await db_session.get(MachineOrm, machine_id)
    assert deleted is None
```

### Example 7: Error Handling Test

```python
"""Test API error responses."""
@pytest.mark.asyncio
async def test_get_nonexistent_deck(client: AsyncClient) -> None:
    """Test retrieving a deck that doesn't exist."""

    # 1. SETUP: Generate a UUID that doesn't exist in DB
    fake_uuid = uuid7()

    # 2. ACT: Call the API with non-existent ID
    response = await client.get(f"/api/v1/decks/{fake_uuid}")

    # 3. ASSERT: Verify 404 response
    assert response.status_code == 404
    assert "detail" in response.json()
```

### Example 8: Validation Test

```python
"""Test request validation."""
@pytest.mark.asyncio
async def test_create_deck_missing_required_field(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test that creating a deck without required fields fails."""

    # 1. SETUP: Create minimal dependencies
    machine = await create_machine(db_session)

    # 2. ACT: Call API with incomplete data (missing deck_type_id)
    response = await client.post(
        "/api/v1/decks/",
        json={
            "name": "incomplete_deck",
            "parent_accession_id": str(machine.accession_id),
            # Missing: deck_type_id, resource_definition_accession_id
        },
    )

    # 3. ASSERT: Verify validation error
    assert response.status_code == 422  # Unprocessable Entity
    error_data = response.json()
    assert "detail" in error_data
```

---

## Checklist for New API Tests

When writing a new API test, ensure:

- [ ] Test name follows `test_<verb>_<noun>` format
- [ ] Docstring describes what the test verifies
- [ ] SETUP/ACT/ASSERT sections clearly commented
- [ ] Using async helpers from `tests/helpers.py` for test data
- [ ] Both `client` and `db_session` fixtures used correctly
- [ ] Status code asserted first
- [ ] UUIDs converted to strings when comparing with JSON
- [ ] Database state verified for CREATE/UPDATE/DELETE operations
- [ ] List assertions use `>=` not `==`
- [ ] Type hints on function parameters and return values
- [ ] `@pytest.mark.asyncio` decorator present

---

## Next Steps

1. **Review existing tests** in `tests/api/test_decks.py` for reference
2. **Use helpers** from `tests/helpers.py` - create new helpers if needed
3. **Follow SETUP/ACT/ASSERT** structure consistently
4. **Run tests frequently** to catch issues early: `pytest tests/api/ -v`
5. **Check coverage** to ensure all endpoints tested: `pytest --cov=praxis.backend.api tests/api/`

---

## Questions?

If you encounter issues not covered here:
1. Check the [Common Pitfalls](#common-pitfalls) section
2. Review similar existing tests in `tests/api/`
3. Ask for help with specific error messages
