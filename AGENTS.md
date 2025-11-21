# Agent and Developer Guide for PyLabPraxis

Welcome to the PyLabPraxis repository. This guide provides essential information for agents and developers to contribute effectively and consistently to the project.

## 1. Core Project Objective

Our current primary objective is to achieve **full test coverage of the backend services** to create a stable foundation for frontend development.

## 2. System Architecture Overview

PyLabPraxis is a Python-based platform for lab automation. It features a FastAPI backend, PostgreSQL and Redis for data persistence, and a service-oriented architecture.

The backend is organized into three main layers:
1.  **API Layer** (`praxis/backend/api/`): Handles HTTP requests, validation, and serialization.
2.  **Service Layer** (`praxis/backend/services/`): Contains the core business logic.
3.  **Data Model Layer** (`praxis/backend/models/`): Defines Pydantic models for data structures and ORM models for database interaction.

For a detailed breakdown of the architecture, refer to `docs/architecture.md`.

## 3. Development Environment and Tooling

### 3.1. Dependency Management
-   **Tool**: We use `uv` for all Python dependency management.
-   **Installation**: Install development dependencies with:
    ```bash
    uv pip install --system -e '.[dev]'
    ```

### 3.2. Running Tools
All development tools (`pytest`, `ruff`, etc.) should be executed via `uv run`. This ensures that the correct versions of the tools and dependencies are used.

**Example**:
```bash
uv run pytest
uv run ruff check .
```

## 4. Testing Strategy

A robust testing strategy is critical to our project's success. Comprehensive documentation:
- **Strategy Overview**: `docs/testing.md`
- **Setup Guide**: `tests/README.md`
- **Pattern Examples**: `tests/TESTING_PATTERNS.md`

### 4.1. Running the Test Suite
-   **Command**: To run the entire test suite, use:
    ```bash
    uv run pytest
    ```
-   **Coverage**: To run tests and generate a coverage report, use:
    ```bash
    uv run pytest --cov=praxis/backend --cov-report=html --cov-report=term-missing
    ```
-   **Target**: We aim for **>90% line and branch coverage** for all new and refactored code.

### 4.2. Test Database

⚠️ **CRITICAL**: The application uses PostgreSQL-specific features (JSONB, UUID extensions). **SQLite is NOT supported** for testing. Tests must run against a real PostgreSQL database to ensure production parity.

-   **Technology**: PostgreSQL 18 (Debian Trixie)

#### Environment-Specific Setup

**For Jules (Pre-configured in your environment)**:
-   **Setup**: ✅ **Database is already running and ready to use!**
    - Host: localhost, Port: 5433
    - Database: test_db, User: test_user
    - All tables created and initialized
-   **No setup needed**: Just run your tests with `pytest`
-   **Verification**: If you want to check the database:
    ```bash
    psql -h localhost -p 5433 -U test_user -d test_db -c "SELECT version();"
    ```

**For Claude Code (Manual PostgreSQL)**:
-   **Setup**: Install and configure PostgreSQL directly:
    ```bash
    # Install PostgreSQL 18
    apt-get update && apt-get install -y postgresql-18 postgresql-contrib-18

    # Start PostgreSQL service
    service postgresql start

    # Create test database and user
    sudo -u postgres psql -c "CREATE DATABASE test_db;"
    sudo -u postgres psql -c "CREATE USER test_user WITH PASSWORD 'test_password';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE test_db TO test_user;"
    sudo -u postgres psql -d test_db -c "GRANT ALL ON SCHEMA public TO test_user;"

    # Set environment variable
    export TEST_DATABASE_URL="postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"
    ```

-   **Isolation**: Each test runs in an isolated transaction that is rolled back upon completion, ensuring tests are fully independent.

### 4.3. Test Organization

The `tests/` directory mirrors the backend structure:
```
tests/
├── api/              # API endpoint tests (E2E)
├── services/         # Service layer tests (business logic)
├── core/             # Core component tests (protocol execution)
└── integration/      # Multi-component integration tests
```

**Testing Patterns by Layer**:
-   **API Tests** (`tests/api/`): Test full HTTP request/response cycle using FastAPI TestClient
-   **Service Tests** (`tests/services/`): Test business logic with real database, mock external dependencies
-   **Core Tests** (`tests/core/`): Test components in isolation with heavy mocking
-   **Integration Tests** (`tests/integration/`): Test component interactions with minimal mocking

**Detailed examples and patterns**: See `tests/TESTING_PATTERNS.md`

### 4.4. Test Data Creation

Use async helper functions (defined in `tests/helpers.py`) to create test data:
```python
from tests.helpers import create_workcell, create_machine, create_deck

# Create test data with default values
workcell = await create_workcell(db_session)
machine = await create_machine(db_session, workcell=workcell)

# Create with custom attributes
deck = await create_deck(db_session, name="custom_deck")
```

**Note**: We use async helpers instead of Factory Boy because PyLabPraxis uses AsyncSession, which is incompatible with Factory Boy's synchronous SQLAlchemyModelFactory.

## 5. Linting and Code Style

### 5.1. Tooling
-   **Linter**: We use `ruff` for linting and code formatting.
-   **Type Checking**: We use `pyright` for static type analysis.

### 5.2. Workflow
-   **Continuous Linting**: Run `ruff check .` periodically to identify issues.
-   **End-of-Cycle Resolution**: While you should aim to write clean code, perform **lint resolution and auto-fixing at the end of a development cycle**, just before submitting your work. This avoids unnecessary churn and focuses effort.
    ```bash
    # Check for issues
    uv run ruff check .

    # Apply safe fixes
    uv run ruff check . --fix
    ```

## 6. Output Styles and Patterns

To maintain clarity and consistency, agents should adhere to the following output patterns.

### Plan Output
Plans must be formatted as a numbered list using Markdown.

**Example**:
```markdown
1.  ***Add a new service function `get_deck_by_id` in `praxis/backend/services/deck_service.py`.***
    *   The function will accept a `deck_id` and return the corresponding deck ORM object.
2.  ***Add a unit test for the new service function in `tests/services/test_deck_service.py`.***
    *   The test will verify that the function correctly retrieves a deck and handles cases where the deck is not found.
3.  ***Complete pre-commit steps.***
    *   Ensure proper testing, verification, review, and reflection are done.
4.  ***Submit the change.***
    *   Once all checks pass, I will submit the change with a descriptive commit message.
```

### Verification Output
After every action that modifies a file (`create_file_with_block`, `replace_with_git_merge_diff`, etc.), you **must** verify the change using a read-only tool like `read_file` or `grep`.

## 7. Project History and Context

To maintain a searchable and structured log of agent and developer contributions, we use an append-only JSON Lines file: `agent_history.jsonl`.

-   **Purpose**: This file serves as the official log of significant decisions, milestones, and completed tasks.
-   **Interaction Pattern**: Do **not** load the entire file into context. Instead, append a new JSON object to the end of the file to record your work.
-   **Format**: Each entry must be a single-line JSON object with the following structure:

    ```json
    {"date": "YYYY-MM-DD", "agent": "YourName", "task": "A brief description of the overall task.", "summary_of_actions": ["Action 1.", "Action 2."], "key_decisions": ["Decision 1.", "Decision 2."]}
    ```
