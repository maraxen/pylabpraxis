# PyLabPraxis Testing Strategy

This document outlines the testing strategy for the PyLabPraxis backend components. Our goal is to ensure reliability, maintainability, and correctness of the application through a comprehensive testing approach.

## Guiding Principles

* **Test Pyramid**: We will adhere to the testing pyramid concept, emphasizing a large base of unit tests, a smaller layer of integration tests, and an even smaller layer of end-to-end (API) tests.
* **Isolation**: Unit tests should test components in isolation, mocking external dependencies.
* **Readability and Maintainability**: Tests should be clear, concise, and easy to understand and maintain.
* **Coverage**: Aim for high test coverage of critical business logic. While 100% coverage is not always practical or valuable, critical paths and complex logic must be thoroughly tested.
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
  * For database interactions, a separate test database should be used, and tests should clean up after themselves.

### 3. API (End-to-End) Tests

* **Scope**: Test the full application stack from the API endpoints.
* **Tools**: `pytest`, FastAPI's `TestClient`.
* **Location**: `tests/api/`. (Some existing tests might be here already)
* **Focus**:
  * Verify that API endpoints behave correctly according to their contracts.
  * Test request validation, authentication/authorization (if applicable and mockable), response codes, and response payloads.
  * These tests will cover the interaction of many backend components.
  * May require a running application instance or a carefully managed test environment.

## Test Implementation Details

### Mocking

* External services (like PyLabRobot hardware backends, Keycloak) will be mocked.
* Database interactions in unit tests will be mocked at the service layer. For example, if a component uses `praxis.backend.services.protocols.get_protocol_definition()`, that service function will be mocked. Direct mocking of SQLAlchemy sessions or ORM methods within component tests should be avoided; instead, mock the service that encapsulates that logic.
* Pydantic models from `praxis.backend.models` (e.g., `praxis.backend.models.machine_pydantic_models.MachineDefinition`) will be used directly for creating test data or asserting types.
* Redis interactions will be mocked for unit tests. For integration tests, a test Redis instance might be used.

### Fixtures

* `pytest` fixtures will be used extensively to set up test data, mock objects, and instances of classes under test.
* Fixtures should be defined in `conftest.py` files at appropriate levels (root `tests/` directory, or specific subdirectories like `tests/core/conftest.py`).

### Test Data

* Clear and representative test data should be used.
* For complex Pydantic models, use their constructors to create instances for test inputs or expected outputs.

### Naming Conventions

* Test files: `test_*.py` (e.g., `test_orchestrator.py`).
* Test functions/methods: `test_*` (e.g., `test_orchestrator_happy_path`).

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

Tests can be run using:

```bash
make test
# or directly with pytest
pytest
```

## Continuous Improvement

This testing strategy is a living document and will be updated as the project evolves. Regular review of test coverage and effectiveness is encouraged.
