# PyLabPraxis Testing Strategy

> **⚡ Performance Optimizations Added (Dec 11, 2025)**
> This document has been significantly expanded with a comprehensive "Test Suite Performance Optimizations" section.
> For quick reference on running tests efficiently, see the [Quick Performance Commands](#quick-performance-commands) section.

This document outlines the testing strategy for the PyLabPraxis backend components. Our goal is to ensure reliability, maintainability, and correctness of the application through a comprehensive testing approach.

## Guiding Principles

* **Test Pyramid**: We will adhere to the testing pyramid concept, emphasizing a large base of unit tests, a smaller layer of integration tests, and an even smaller layer of end-to-end (API) tests.
* **Isolation**: Unit tests should test components in isolation, mocking external dependencies.
* **Readability and Maintainability**: Tests should be clear, concise, and easy to understand and maintain.
* **Coverage**: Aim for high test coverage of critical business logic. A concrete target of >90% line and branch coverage for all new and refactored code should be enforced. While 100% coverage is not always practical or valuable, critical paths and complex logic must be thoroughly tested.
* **Automation**: All tests should be automated and runnable with a single command (e.g., `make test` or `pytest`).
* **CI/CD Integration**: Tests will be integrated into the CI/CD pipeline to ensure that no regressions are introduced.

## Types of Tests

### 1. Unit Tests

* **Scope**: Test individual functions, methods, classes, or modules in isolation.
* **Tools**: `pytest` framework, `unittest.mock` for mocking.
* **Location**: `tests/` directory, mirroring the structure of the `praxis/` directory (e.g., `praxis/backend/core/orchestrator.py` will have tests in `tests/core/test_orchestrator.py`).
* **Focus**:
  * Verify the logic within a single unit.
  * Test different inputs, including valid, invalid, and edge cases.
  * Ensure correct state changes and outputs.
  * Mock all external dependencies (database interactions via service layer mocks, Redis, other services, hardware interfaces).

### 2. Integration Tests

* **Scope**: Test the interaction between two or more components or services.
* **Tools**: `pytest`, potentially `docker-compose` for setting up test instances of databases (PostgreSQL) and caches (Redis).
* **Location**: `tests/integration/`.
* **Focus**:
  * Verify that components work together as expected.
  * Test data flow and communication paths between services.
  * Example: Test the `ProtocolExecutionService` calling the `Orchestrator`, which in turn interacts with a mocked `AssetManager` and `WorkcellRuntime`.
  * For database interactions, a separate, ephemeral test database should be used. This database should be automatically migrated to the latest schema (e.g., using `alembic upgrade head`) before the test suite runs, and all data should be cleaned up after each test or test session.

### 3. API (End-to-End) Tests

* **Scope**: Test the full application stack from the API endpoints.
* **Tools**: `pytest`, FastAPI's `TestClient`.
* **Location**: `tests/api/`. (Some existing tests might be here already)
* **Focus**:
  * Verify that API endpoints behave correctly according to their contracts.
  * Test request validation, authentication/authorization (if applicable and mockable), response codes, and response payloads.
  * These tests will cover the interaction of many backend components.
  * May require a running application instance or a carefully managed test environment.

### 4. Property-Based Testing

* **Scope**: Enhance unit and integration tests by testing a wide range of auto-generated data, uncovering edge cases that might be missed with example-based testing.
* **Tools**: `Hypothesis` library, integrated with `pytest`.
* **Location**: Within existing unit and integration test files.
* **Focus**:
  * Testing parsing logic, data validation, and state machines.
  * Generating a broad spectrum of inputs to ensure robustness.
  * Identifying unexpected failures in pure functions and components.

## Test Implementation Details

### Mocking

* External services (like PyLabRobot hardware backends, Keycloak) will be mocked.
* Database interactions in unit tests will be mocked at the service layer. For example, if a component uses `praxis.backend.services.protocols.get_protocol_definition()`, that service function will be mocked. Direct mocking of SQLAlchemy sessions or ORM methods within component tests should be avoided; instead, mock the service that encapsulates that logic.
* Pydantic models from `praxis.backend.models` (e.g., `praxis.backend.models.machine_pydantic_models.MachineDefinition`) will be used directly for creating test data or asserting types.
* Redis interactions will be mocked for unit tests. For integration tests, a test Redis instance might be used.

### Fixtures

* `pytest` fixtures will be used extensively to set up test data, mock objects, and instances of classes under test.
* Fixtures should be defined in `conftest.py` files at appropriate levels (root `tests/` directory, or specific subdirectories like `tests/core/conftest.py`).

### Shared Fixtures and UUIDs in `conftest.py`

* Shared fixtures for test data, mocks, and static UUIDs should be defined in `conftest.py` files at the appropriate directory level (e.g., `tests/core/conftest.py`).
* For UUIDs, use static UUIDv7 values to ensure deterministic and collision-free test data. Structure them as follows:

```python
TEST_PROTOCOL_RUN_ID = uuid.UUID("018f4a3b-3c48-7c87-8c4c-35e6a172c74d", version=7)
TEST_MACHINE_ID = uuid.UUID("018f4a3c-b034-7548-b4e8-87d464cb3f92", version=7)
TEST_RESOURCE_ID = uuid.UUID("018f4a3d-3b4f-7b1e-913a-a1c1d858348c", version=7)
TEST_DECK_RESOURCE_ID = uuid.UUID("018f4a3d-a3e1-75f2-9831-27f329d443e2", version=7)
```

* These static UUIDs should be used in test factories and fixtures to create ORM or Pydantic model instances, ensuring consistency and traceability across tests.
* Refer to the provided `conftest.py` for examples of how to structure and use these fixtures.

### Test Data

* Clear and representative test data should be used.
* For complex Pydantic models, use their constructors to create instances for test inputs or expected outputs.
* All test UUIDs should use [UUID version 7](https://datatracker.ietf.org/doc/html/draft-peabody-dispatch-new-uuid-format-04) for consistency with production data and to avoid collisions. Static UUIDv7 values should be defined in test fixtures (see `conftest.py` for examples).
* When creating test data that requires unique identifiers, prefer using these static UUIDs or generating new UUIDv7 values as appropriate.

### Naming Conventions

* Test files: `test_*.py` (e.g., `test_orchestrator.py`).
* Test functions/methods: `test_*` (e.g., `test_orchestrator_happy_path`).

### Async Test Helpers

To support our async architecture and SQLAlchemy 2.0 patterns (specifically `MappedAsDataclass` with `init=False` relationships), we use custom async helper functions located in `tests/helpers.py`.

**Why not Factory Boy?**
Factory Boy is designed for synchronous ORMs and struggles with our async session handling and complex relationship initialization requirements.

**Usage Patterns**
Helpers are designed to be used within async tests. They handle:
1.  Creating valid ORM instances with generated UUIDs.
2.  Correctly handling `MappedAsDataclass` constraints (resolving foreign keys vs object relationships).
3.  Persisting objects to the test database using the provided `db_session`.

**Example:**
```python
from tests.helpers import create_protocol_run, create_function_data_output

async def test_something(db_session):
    # Create valid parent objects automatically
    run = await create_protocol_run(db_session, name="my_run")

    # helper handles complex relationship wiring
    output = await create_function_data_output(
        db_session,
        protocol_run=run,
        data_value_json={"foo": "bar"}
    )

    assert output.protocol_run_accession_id == run.accession_id
```

**Key Helper Functions:**
* `create_workcell`
* `create_machine`
* `create_resource`, `create_resource_definition`
* `create_deck`, `create_deck_definition`
* `create_protocol_run`, `create_protocol_definition`
* `create_function_data_output`

### Patching and Isolation

* All unit tests must be well isolated. Use `unittest.mock.patch`, `patch.object`, or `pytest`'s `monkeypatch` to replace external dependencies, I/O, or service calls with mocks or fakes.
* Avoid relying on real database, Redis, or hardware connections in unit tests. All such dependencies should be mocked at the service or interface layer.
* Each test should be independent and not rely on shared state. Use fixtures to set up and tear down any required context.
* When patching, always use the most specific scope possible (e.g., patch only the method or class needed, not entire modules) to avoid unintended side effects.

## Backend Components to Test

The following is a non-exhaustive list of key backend components and areas to focus on:

**Core Components (`praxis/backend/core/`)**

* **`AssetLockManager`**: Locking/unlocking logic, Redis interactions. (Initial tests implemented)
* **`Orchestrator`**: Protocol execution flow, state management, interaction with `AssetManager`, `ProtocolCodeManager`, `WorkcellRuntime`.
* **`ProtocolExecutionService`**: Entry point for protocol execution, interaction with `Orchestrator`, `ProtocolScheduler`.
* **`ProtocolScheduler`**: Scheduling logic, asset reservation, Celery task queuing.
* **`AssetManager`**: Asset acquisition/release, interaction with `WorkcellRuntime`, database updates (via services).
* **`WorkcellRuntime`**: Management of PyLabRobot objects, setup/teardown, state backup/restore. Imports Pydantic models from `praxis.backend.models.*_pydantic_models`.
* **`Workcell`**: In-memory representation of workcell configuration.
* **`ProtocolCodeManager`**: Fetching and loading protocol code.
* **`PraxisRunContext`**: Ensure it correctly carries and provides access to run-specific data.
* **`Protocol Decorators`**: Test through protocol discovery and execution tests.

**Database Interaction Services (`praxis/backend/services/`)**

* Each service module (e.g., `praxis.backend.services.protocols`, `praxis.backend.services.machine`) needs unit tests for its CRUD operations and specialized queries.
* Mock the SQLAlchemy session and ORM model interactions within these service tests.

**API Layer (`praxis/backend/api/`)**

* Each router/endpoint group (e.g., `/protocols`, `/assets`) needs API tests.
* Test request validation, responses, and side effects (e.g., database changes via services, task queuing).

**State Management (`praxis.backend.services.state.PraxisState`)**

* Test `PraxisState` for storing and retrieving run-specific data, interaction with Redis.

## Running Tests

### Environment Setup

**Local Development**:
Tests require a PostgreSQL database.
- **Default Port:** The test configuration in `praxis/backend/utils/db.py` defaults to `localhost:5433` if `TEST_DATABASE_URL` is not set.
- **Recommended:** Run a dedicated test database container on port **5433** to avoid conflicts with local development instances running on the default port 5432.

**CI Environment**:
The CI workflow (`.github/workflows/ci.yml`) runs PostgreSQL on port **5432**.

### Execution

To run tests locally against a specific database (e.g., port 5433):
```bash
export TEST_DATABASE_URL="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
uv run pytest
```

To run the test suite and generate a coverage report:

```bash
uv run pytest --cov=praxis/backend --cov-report=term-missing --cov-report=xml
```

This command will:
- Run `pytest` using the `uv` tool.
- Generate a coverage report for the `praxis/backend` directory.
- output the report to the terminal and an XML file.

## Advanced Testing Practices

### Mutation Testing

High code coverage doesn't always mean the tests are effective. Mutation testing helps ensure that your tests are actually testing the logic correctly. A tool like `mutmut` can be used to periodically assess the quality of the test suite by making small changes (mutations) to the code and verifying that the tests fail.

## Security Testing

Security is a critical aspect of any modern application. The following practices should be integrated into the development lifecycle.

*   **Static Application Security Testing (SAST)**: Integrate a tool like `Bandit` into the CI pipeline to scan for common security vulnerabilities in the code.
*   **Dependency Scanning**: Use a tool like `pip-audit` or GitHub's Dependabot to automatically check for vulnerabilities in third-party packages.
*   **Dynamic Application Security Testing (DAST)**: For more mature applications, consider using a DAST scanner to probe the running application for vulnerabilities.

## Performance and Load Testing

As the application grows, performance will become a critical concern. It's best to plan for this early.

*   **Load Testing**: We will simulate a high number of concurrent users to test the performance of key API endpoints under stress. Tools like `locust` are excellent for this.
*   **Benchmarking**: We will create benchmarks for critical business logic to track performance regressions over time. The `pytest-benchmark` plugin is a great option here.

## Phased Implementation Plan

Based on our learnings from initial test infrastructure setup, follow this order to build a robust test suite:

### Phase 0: Test Infrastructure (✅ COMPLETE)
- ✅ PostgreSQL test database setup
- ✅ Async session fixtures with proper transaction isolation
- ✅ FastAPI TestClient with dependency overrides
- ✅ Async test helper functions (replacing Factory Boy)
- ✅ Transaction visibility between test fixtures and API endpoints

### Phase 1: Model Layer Tests (CURRENT PRIORITY)
**Why First:** Model configuration issues (Pydantic serialization, ORM relationships) must be resolved before testing higher layers. Attempting API tests first leads to confusing errors that mask underlying model problems.

- **Pydantic Model Tests** (`tests/models/test_pydantic/`)
  - Test serialization/deserialization for each model
  - Test model validation rules
  - Test nested model relationships
  - Identify and fix circular dependency issues
  - Target: WorkcellResponse, MachineResponse, ResourceResponse, DeckResponse

- **ORM Model Tests** (`tests/models/test_orm/`)
  - Test model creation with required fields
  - Test relationship loading (lazy vs eager)
  - Test inheritance conditions (e.g., DeckOrm → ResourceOrm)
  - Verify SQLAlchemy configurations work correctly
  - Target: WorkcellOrm, MachineOrm, ResourceOrm, DeckOrm

### Phase 2: Service Layer Tests
Once models work correctly in isolation, test business logic:

- **Database Service Tests** (`tests/services/`)
  - Test CRUD operations for each service
  - Test query filtering and pagination
  - Test relationship loading strategies
  - Mock external dependencies (Redis, Celery)
  - Target: WorkcellService, MachineService, DeckService, ResourceService

### Phase 3: API Layer Tests
With working models and services, test the full stack:

- **API Endpoint Tests** (`tests/api/`)
  - Test request/response cycles
  - Test validation errors
  - Test authentication/authorization
  - Test complete CRUD workflows
  - Target: All API routers

### Phase 4: Core Component Tests
Test protocol execution and orchestration:

- **AssetManager, Orchestrator, WorkcellRuntime**
- **Protocol execution flows**
- **State management and recovery**

### Phase 5: Integration Tests
Test multi-component workflows end-to-end.

## Test Suite Performance Optimizations

Our test suite follows best practices from [awesome-pytest-speedup](https://github.com/zupo/awesome-pytest-speedup) to ensure fast execution times. This section covers the specific optimizations implemented and how to use them effectively.

### Quick Performance Commands

```bash
# Set environment variable to skip bytecode generation (recommended for all dev work)
export PYTHONDONTWRITEBYTECODE=1

# Run tests in parallel across all CPU cores
uv run pytest -n auto

# Run only fast tests (skip tests marked as slow)
uv run pytest -m "not slow"

# Find the 10 slowest tests
uv run pytest --durations=10

# Run tests that failed in the last run (faster iteration)
uv run pytest --lf

# Profile import time to find slow imports
uv run python -X importtime -m pytest --collect-only 2>&1 | python -c "import sys; print('\n'.join(sorted(sys.stdin, key=lambda x: x.split(':')[0] if ':' in x else '0')))"
```

### 1. Fast Collection

**Problem**: Test collection (finding all tests) was slow, especially with 100+ test files.

**Solutions Implemented**:
- **`testpaths`**: Explicitly set to `tests/` to avoid scanning the entire codebase
- **`norecursedirs`**: Configured to skip `node_modules`, `alembic`, `docs`, `.venv`, and other non-test directories
- **Disabled built-in plugins**: Unnecessary plugins (`pastebin`, `nose`, `doctest`) are disabled for faster startup
- **`PYTHONDONTWRITEBYTECODE=1`**: Skips `.pyc` file generation (add to `~/.profile` or `.envrc`)

**Expected Result**: Collection should take ~1-2 seconds for the entire suite.

**Verify**: Run `uv run pytest --collect-only` to check collection speed.

### 2. Network Access Control

**Problem**: Tests accidentally making network requests slow down the suite and can cause flaky failures.

**Solution**: [`pytest-socket`](https://pypi.org/project/pytest-socket/) prevents inadvertent network access.

**Configuration**:
- Only localhost connections are allowed by default (`--allow-hosts=127.0.0.1,::1,localhost,test_db`)
- Tests requiring external network must be marked with `@pytest.mark.network`
- HTTP requests should be mocked using the `responses` library

**Example**:
```python
import pytest
import responses

@pytest.mark.network  # Allows network access
def test_real_api_call():
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200

@responses.activate  # Mock HTTP responses (no network marker needed)
def test_mocked_api_call():
    responses.add(responses.GET, "https://api.example.com/data",
                  json={"key": "value"}, status=200)
    response = requests.get("https://api.example.com/data")
    assert response.json() == {"key": "value"}
```

### 3. Optimized Database Access

**Problem**: Recreating the database schema for each test is extremely slow (100-1000ms per test).

**Solution**: Session-scoped database creation with function-scoped transaction rollback.

**How It Works**:
1. **`db_engine` (session scope)**: Creates database schema **once** for the entire test session
2. **`db_session` (function scope)**: Each test runs in a transaction that's rolled back afterward
3. **No table recreation**: Tests reuse the same schema, only rolling back data changes

**Performance Impact**: **10-100x faster** than recreating tables per test.

**Important Rules**:
```python
# ✅ DO: Use flush() to write to DB within the transaction
async def test_create_entity(db_session):
    entity = MyModel(name="test")
    db_session.add(entity)
    await db_session.flush()  # Makes entity visible in this transaction

    # Query and assert
    result = await db_session.execute(select(MyModel))
    assert result.scalar_one().name == "test"
    # Transaction automatically rolled back after test

# ❌ DON'T: Never commit in tests
async def test_bad_example(db_session):
    entity = MyModel(name="test")
    db_session.add(entity)
    await db_session.commit()  # ⚠️ Breaks transaction rollback!
```

### 4. Parallel Test Execution

**Problem**: Tests run sequentially by default, wasting CPU cores.

**Solution**: [`pytest-xdist`](https://pypi.org/project/pytest-xdist/) runs tests across multiple workers.

**Usage**:
```bash
# Auto-detect CPU cores
uv run pytest -n auto

# Use specific number of workers
uv run pytest -n 4

# Distribute by file (better for test files with many tests)
uv run pytest -n 4 --dist loadfile

# Distribute by test (default, better for files with few tests)
uv run pytest -n 4 --dist load
```

**Docker Compatibility**: The `docker_db` fixture is xdist-aware:
- Master process: Starts/stops the Docker test database
- Worker processes: Connect to the existing database

**Randomization with xdist**:
```bash
# Fix random seed for reproducible parallel runs
uv run pytest -n auto --randomly-seed=12345
```

### 5. Selective Test Running

**Problem**: Running all tests during development wastes time when only some are relevant.

**Solutions**:

**a) Mark-based Selection**:
```bash
# Run only unit tests (fast, no database)
uv run pytest -m unit

# Skip slow tests
uv run pytest -m "not slow"

# Run integration tests only
uv run pytest -m integration
```

**b) Failed/Changed Test Selection**:
```bash
# Run only tests that failed last time
uv run pytest --lf

# Run failed tests first, then the rest
uv run pytest --ff

# Consider using pytest-incremental (future addition)
# Only runs tests affected by code changes
```

**c) Mark Tests Appropriately**:
```python
@pytest.mark.unit
def test_pure_calculation():
    # No DB, no external services
    assert calculate_value(10) == 20

@pytest.mark.integration
@pytest.mark.slow
async def test_full_workflow(db_session):
    # Integration test taking >1s
    pass

@pytest.mark.e2e
async def test_api_endpoint(client):
    # Full stack test
    pass
```

### 6. Filesystem Access Optimization

**Problem**: Real filesystem I/O is slow and can cause conflicts between tests.

**Solution**: [`pyfakefs`](https://github.com/pytest-dev/pyfakefs) provides an in-memory filesystem.

**Example**:
```python
def test_file_operations(fs):  # fs fixture from pyfakefs
    # All file operations use in-memory filesystem
    fs.create_file("/tmp/test.txt", contents="test data")

    with open("/tmp/test.txt") as f:
        assert f.read() == "test data"

    # File exists only in this test's memory
    assert os.path.exists("/tmp/test.txt")
```

### 7. Performance Monitoring

**Track Performance Over Time**:
```bash
# Enable pytest-monitor to track test performance
uv run pytest --monitor

# Generates .pymon SQLite database with performance metrics
# Query with: sqlite3 .pymon "SELECT * FROM TEST_METRICS ORDER BY TOTAL_TIME DESC LIMIT 10"
```

**Find Slow Tests**:
```bash
# Show 20 slowest tests
uv run pytest --durations=20

# Show all test durations
uv run pytest --durations=0
```

**Profile Individual Tests**:
```bash
# Install pytest-profiling (optional)
pip install pytest-profiling

# Profile specific test
uv run pytest --profile tests/slow_test.py

# Generates .prof files viewable with snakeviz
```

### 8. Test Randomization

**Why**: Catches hidden test dependencies and ordering issues.

**How**: [`pytest-randomly`](https://pypi.org/project/pytest-randomly/) randomizes test order automatically.

**Usage**:
```bash
# Tests run in random order by default
uv run pytest

# Use specific seed for reproducibility
uv run pytest --randomly-seed=12345

# Disable randomization if needed
uv run pytest -p no:randomly
```

### 9. CI Optimization

**Recommended CI Configuration**:

```yaml
# .github/workflows/test.yml
env:
  PYTHONDONTWRITEBYTECODE: 1

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # Run fast tests first
      - name: Fast tests
        run: uv run pytest -n auto -m "not slow" --cov=praxis

      # Run slow tests separately
      - name: Slow tests
        run: uv run pytest -n auto -m slow

      # Generate coverage report
      - name: Coverage
        run: uv run pytest --cov=praxis --cov-report=xml --cov-report=term
```

### Performance Checklist

For maximum test suite performance, ensure:

- [ ] `PYTHONDONTWRITEBYTECODE=1` is set in environment
- [ ] Collection takes <3 seconds (`uv run pytest --collect-only`)
- [ ] Tests run in parallel (`uv run pytest -n auto`)
- [ ] Network access is disabled except where needed
- [ ] Database uses session-scoped schema with transaction rollback
- [ ] Slow tests are marked with `@pytest.mark.slow`
- [ ] File I/O uses `pyfakefs` where appropriate
- [ ] Tests are independent (randomization doesn't cause failures)

### Writing Performance-Friendly Tests

**DO**:
- ✅ Mark slow tests with `@pytest.mark.slow`
- ✅ Use `db_session.flush()` instead of `commit()`
- ✅ Mock external APIs with `responses`
- ✅ Use `pyfakefs` for file operations in unit tests
- ✅ Keep unit tests isolated (no DB, no network)
- ✅ Use factory fixtures for test data

**DON'T**:
- ❌ Commit transactions in tests (breaks rollback optimization)
- ❌ Make real network requests without mocking
- ❌ Write to real filesystem in unit tests
- ❌ Create complex fixture dependencies
- ❌ Share mutable state between tests
- ❌ Leave slow tests unmarked

### Troubleshooting Performance Issues

**Collection is slow (>3s)**:
1. Check import time: `uv run python -X importtime -m pytest --collect-only`
2. Move expensive imports inside functions
3. Verify `norecursedirs` excludes large directories
4. Check for code execution in `conftest.py` during import

**Tests are slow individually**:
1. Find culprits: `uv run pytest --durations=20`
2. Mark slow tests: `@pytest.mark.slow`
3. Profile: `uv run pytest --profile tests/slow_test.py`
4. Check for:
   - Network requests (should be mocked)
   - Real filesystem I/O (use pyfakefs)
   - Unnecessary database commits
   - Complex fixture setup

**Parallel tests fail but sequential works**:
1. Tests might share state (global variables, database, files)
2. Check for hardcoded IDs or paths
3. Ensure fixtures are function-scoped where needed
4. Verify Docker database handles multiple connections

**Database tests are slow**:
1. Verify `db_engine` is session-scoped (not function-scoped)
2. Ensure tests use `flush()` not `commit()`
3. Check that transactions are being rolled back
4. Consider using in-memory SQLite for pure unit tests

## Continuous Improvement

This testing strategy is a living document and will be updated as the project evolves. Regular review of test coverage, effectiveness, and performance is encouraged.

## Known Issues & Troubleshooting

The following configuration issues have been identified during initial testing and are documented here for reference.

### 1. Pydantic `use_enum_values=True` Behavior

*   **Description**: `PraxisBaseModel` uses `use_enum_values=True`. This causes enum fields to be stored as their string values rather than enum instances on the Pydantic model.
*   **Impact**: When comparing Pydantic model fields in tests, compare against `Enum.VALUE.value` or the expected string, not the Enum member itself (e.g., `assert model.status == "active"` or `assert model.status == WorkcellStatusEnum.ACTIVE.value`, NOT `assert model.status == WorkcellStatusEnum.ACTIVE`).

### 2. SQLAlchemy Relationship Overlap

*   **Description**: `WorkcellOrm` has overlapping relationships between `resources` and `decks`.
*   **Status**: Resolved by adding `overlaps="decks"` to the relationship definition. If new relationships are added, similar configuration might be needed.

### 3. ResourceOrm Persistence Issue

*   **Description**: `ResourceOrm` has a known issue where `resource_definition_accession_id` (a mandatory foreign key) may not persist correctly to the database in certain test scenarios due to complex inheritance and `MappedAsDataclass` behavior.
*   **Workaround**: For now, unit tests involving `ResourceOrm` persistence might be limited or require careful setup. This is a known limitation of the current ORM architecture for this specific model.

### 4. SQLAlchemy Inheritance Warning

*   **Description**: `SAWarning: Implicitly combining column assets.accession_id with column decks.accession_id under attribute 'accession_id'`.
*   **Impact**: Low. This is an ORM inheritance warning.
*   **Action**: Should be addressed but doesn't affect test functionality.
*   **Location**: `praxis/backend/models/orm/deck.py:58`.
