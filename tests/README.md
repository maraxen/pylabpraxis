# PyLabPraxis Test Suite

This directory contains all tests for the PyLabPraxis backend. Tests are organized by backend layer and mirror the structure of `praxis/backend/`.

## Prerequisites

### PostgreSQL Test Database (Required)

**The test suite requires a running PostgreSQL database.** SQLite is not supported due to PostgreSQL-specific features (JSONB, UUID extensions, etc.) used in production.

Start the test database:
```bash
docker compose -f docker-compose.test.yml up -d
```

Check database status:
```bash
docker compose -f docker-compose.test.yml ps
```

Stop the database:
```bash
docker compose -f docker-compose.test.yml down
```

### Environment Configuration

The test database URL can be configured via environment variable:
```bash
export TEST_DATABASE_URL="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
```

Default: `postgresql+asyncpg://test_user:test_password@localhost:5433/test_db`

## Running Tests

### Run All Tests
```bash
uv run pytest
```

### Run with Coverage Report
```bash
uv run pytest --cov=praxis/backend --cov-report=html --cov-report=term-missing
```

### Run Specific Test File
```bash
uv run pytest tests/api/test_decks.py -v
```

### Run Specific Test
```bash
uv run pytest tests/api/test_decks.py::test_create_deck -v
```

### Run with Detailed Output
```bash
uv run pytest tests/api/test_decks.py -vv -s
```

### Run Tests by Marker
```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Skip slow tests
uv run pytest -m "not slow"
```

## Test Organization

```
tests/
├── README.md                   # This file
├── conftest.py                 # Session-wide fixtures (db_engine, db_sessionmaker, db_session)
├── factories.py                # Factory Boy factories for test data
├── api/                        # API endpoint tests (E2E)
│   ├── conftest.py            # API-specific fixtures (client)
│   ├── test_decks.py          # Deck API CRUD tests
│   ├── test_deck_type_definitions.py
│   └── test_smoke.py          # Basic health check
├── services/                   # Service layer tests
│   ├── test_deck_service.py
│   └── test_outputs.py
└── core/                       # Core component tests (TODO)
    └── (to be created)
```

## Testing Patterns by Layer

### 1. API Layer Tests (`tests/api/`)

**Purpose**: Test HTTP endpoints end-to-end, including request validation, business logic, and database persistence.

**Pattern**:
```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.factories import DeckFactory

@pytest.mark.asyncio
async def test_create_deck(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a deck via API."""
    # 1. SETUP: Create test data using factories
    workcell = WorkcellFactory()
    machine = MachineFactory(workcell=workcell)
    await db_session.flush()

    # 2. ACT: Call the API endpoint
    response = await client.post(
        "/api/v1/decks/",
        json={"name": "test_deck", "machine_id": str(machine.accession_id)},
    )

    # 3. ASSERT: Verify response and database state
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_deck"
```

**Key Points**:
- Use `client` fixture (FastAPI AsyncClient with dependency overrides)
- Use `db_session` fixture (transactional, auto-rollback)
- Create dependencies with factories bound to the same session
- Test happy path, validation errors, not found errors, etc.

### 2. Service Layer Tests (`tests/services/`)

**Purpose**: Test business logic in isolation, mocking database interactions.

**Pattern**:
```python
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from praxis.backend.services.deck import DeckService

@pytest.mark.asyncio
async def test_get_deck_by_id(db_session: AsyncSession) -> None:
    """Test retrieving a deck by ID."""
    # SETUP: Create test data
    deck = DeckFactory()
    await db_session.flush()

    # ACT: Call service method
    service = DeckService(db_session)
    result = await service.get_by_id(deck.accession_id)

    # ASSERT: Verify result
    assert result.accession_id == deck.accession_id
    assert result.name == deck.name
```

**Key Points**:
- Use real database for service tests (transactional isolation)
- Mock external dependencies (Redis, Celery, external APIs)
- Test error handling and edge cases
- Focus on business logic correctness

### 3. Core Component Tests (`tests/core/`)

**Purpose**: Test core protocol execution components with heavy mocking of dependencies.

**Pattern** (to be implemented):
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from praxis.backend.core.asset_manager import AssetManager

@pytest.mark.asyncio
async def test_acquire_asset_success():
    """Test successful asset acquisition."""
    # SETUP: Mock all dependencies
    mock_db_session = AsyncMock()
    mock_workcell_runtime = MagicMock()
    mock_deck_service = AsyncMock()

    asset_manager = AssetManager(
        db_session=mock_db_session,
        workcell_runtime=mock_workcell_runtime,
        deck_service=mock_deck_service,
    )

    # ACT: Call the method
    result = await asset_manager.acquire_asset(...)

    # ASSERT: Verify behavior
    assert result is not None
    mock_workcell_runtime.get_live_machine.assert_called_once()
```

**Key Points**:
- Heavy use of mocks for external dependencies
- Test complex logic paths and state changes
- Test error recovery and rollback scenarios
- Focus on unit isolation

## Test Fixtures

### Session-Wide Fixtures (`conftest.py`)

- **`event_loop`**: Session-wide async event loop
- **`db_engine`**: PostgreSQL engine with schema initialization
- **`db_sessionmaker`**: Session factory for creating sessions

### Function-Wide Fixtures (`conftest.py`)

- **`db_session`**: Transactional session that rolls back after each test
  - All database changes are automatically rolled back
  - Tests are fully isolated from each other

### API Fixtures (`tests/api/conftest.py`)

- **`client`**: FastAPI AsyncClient with dependency overrides
  - Overrides `get_db` to use the test session
  - Binds factories to the test session
  - Ensures API and tests use the same database transaction

## Test Data Factories

Factories are defined in `tests/factories.py` using Factory Boy with SQLAlchemy integration.

### Available Factories

- `WorkcellFactory`: Creates workcell ORM instances
- `MachineFactory`: Creates machine ORM instances
- `ResourceDefinitionFactory`: Creates resource definitions
- `DeckDefinitionFactory`: Creates deck type definitions
- `DeckFactory`: Creates deck instances with dependencies

### Using Factories

```python
# Create single instance
workcell = WorkcellFactory()

# Create with specific attributes
machine = MachineFactory(name="special_machine")

# Create with relationships
machine = MachineFactory(workcell=workcell)

# Create batch
decks = DeckFactory.create_batch(5)

# Important: Factories must be bound to the test session
WorkcellFactory._meta.sqlalchemy_session = db_session
```

## Best Practices

### 1. Test Isolation
- Never rely on data from other tests
- Use factories to create fresh test data
- Leverage transaction rollback for cleanup

### 2. Test Naming
- Use descriptive names: `test_<action>_<scenario>`
- Examples:
  - `test_create_deck_success`
  - `test_get_deck_not_found`
  - `test_update_deck_validation_error`

### 3. Test Structure (AAA Pattern)
```python
async def test_something():
    # 1. ARRANGE/SETUP: Create test data
    deck = DeckFactory()

    # 2. ACT: Perform the action
    result = await service.do_something(deck.id)

    # 3. ASSERT: Verify the outcome
    assert result.status == "success"
```

### 4. Assertions
- Use specific assertions, not just `assert True`
- Check both response and database state for API tests
- Test error messages and status codes

### 5. Async/Await
- Mark async tests with `@pytest.mark.asyncio`
- Use `async def` for test functions
- Await all async calls

### 6. Mocking Strategy
- Mock at the **service layer**, not at ORM level
- Mock external dependencies (Redis, Celery, HTTP calls)
- Use `AsyncMock` for async functions
- Use `MagicMock` for sync functions

### 7. Coverage
- Aim for >90% line and branch coverage
- Focus on critical paths and business logic
- Don't sacrifice test quality for coverage percentage

## Common Issues

### Database Connection Refused
```
ConnectionRefusedError: [Errno 111] Connect call failed ('127.0.0.1', 5433)
```
**Solution**: Start the test database with `docker compose -f docker-compose.test.yml up -d`

### Import Errors
```
ModuleNotFoundError: No module named 'pytest_asyncio'
```
**Solution**: Install dev dependencies with `uv pip install -e '.[dev]'`

### Fixture Not Found
```
fixture 'client' not found
```
**Solution**: Ensure you're running tests from the project root and `conftest.py` files are present

### Factory Session Errors
```
DetachedInstanceError: Instance is not bound to a Session
```
**Solution**: Ensure factories are bound to the test session before use:
```python
WorkcellFactory._meta.sqlalchemy_session = db_session
```

## Debugging Tests

### Run with Print Statements
```bash
uv run pytest tests/api/test_decks.py -s
```

### Run with PDB Debugger
```bash
uv run pytest tests/api/test_decks.py --pdb
```

### View Full Traceback
```bash
uv run pytest tests/api/test_decks.py -vv --tb=long
```

### Show Test Duration
```bash
uv run pytest tests/api/test_decks.py --durations=10
```

## Contributing Tests

When adding new features:
1. Write tests alongside the implementation
2. Follow existing patterns for the layer you're testing
3. Ensure tests pass locally before committing
4. Aim for >90% coverage of new code
5. Add docstrings to test functions explaining what is being tested

## Next Steps (TODO)

- [ ] Add core component tests (AssetManager, Orchestrator, etc.)
- [ ] Add integration tests for protocol execution flow
- [ ] Expand service layer test coverage
- [ ] Add property-based tests using Hypothesis
- [ ] Set up mutation testing with mutmut
