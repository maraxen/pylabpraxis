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

For a detailed breakdown of the architecture, refer to `prerelease_dev_docs/ARCHITECTURE.md`.

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

A robust testing strategy is critical to our project's success. The complete strategy is documented in `prerelease_dev_docs/TESTING_STRATEGY.md`.

### 4.1. Running the Test Suite
-   **Command**: To run the entire test suite, use:
    ```bash
    uv run pytest
    ```
-   **Coverage**: To run tests and generate a coverage report, use:
    ```bash
    uv run pytest --cov=praxis/backend --cov-report=term-missing
    ```
-   **Target**: We aim for **>90% line and branch coverage** for all new and refactored code.

### 4.2. Test Database
-   **Technology**: We use a PostgreSQL database for testing.
-   **Setup**: The test database is managed via Docker. The necessary Docker environment is already configured for agent development environments. To start it manually, use:
    ```bash
    sudo docker compose -f docker-compose.test.yml up -d
    ```
-   **Isolation**: The test database is ephemeral. The schema is automatically migrated to the latest version before each test run, and each test runs in an isolated transaction that is rolled back upon completion.

### 4.3. Scoping Tests
The `tests/` directory mirrors the application's structure. When adding or modifying code, ensure corresponding tests are added or updated in the matching location.

-   **Unit Tests**: Test individual functions or classes in isolation. Place them in `tests/` mirroring the component's path (e.g., tests for `praxis/backend/services/deck_service.py` go in `tests/services/test_deck_service.py`).
-   **API Tests**: Test API endpoints from an end-to-end perspective. Place them in `tests/api/`.
-   **Smoke Tests**: A small subset of critical tests are marked with `@pytest.mark.smoke`. These are run in a `smoke-test` job in the CI pipeline to provide a quick health check.

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
