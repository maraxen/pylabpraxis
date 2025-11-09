# PyLabPraxis Quick Reference Guide

This guide provides a concise summary of key development norms. For full details, see `AGENTS.md`.

## 1. Core Objective
-   **Current Focus**: Achieve >90% test coverage for all backend services.

## 2. Key Commands
-   **Install Dependencies**: `uv pip install --system -e '.[dev]'`
-   **Run Tests**: `uv run pytest`
-   **Run Tests with Coverage**: `uv run pytest --cov=praxis/backend --cov-report=term-missing`
-   **Run Linter**: `uv run ruff check .`
-   **Apply Lint Fixes**: `uv run ruff check . --fix`
-   **Run Type Checker**: `uv run pyright`

## 3. Development Workflow
1.  **Code**: Implement your feature or bug fix.
2.  **Test**: Write or update tests, ensuring they are correctly scoped in the `tests/` directory.
3.  **Verify**: Run the full test suite and aim for >90% coverage on your changes.
4.  **Lint**: At the **end of your development cycle**, run `ruff check . --fix` to resolve any linting issues.
5.  **Submit**: Follow the established process for code submission.

## 4. Testing Essentials
-   **Test Database**: A Dockerized PostgreSQL database is used for testing. It's automatically managed in the agent environment.
-   **Test Scoping**: The `tests/` directory mirrors the `praxis/` source directory. Place tests in the corresponding location.
-   **Smoke Tests**: Critical tests marked with `@pytest.mark.smoke` run in CI for a rapid check.

## 5. Architectural Principles
-   **Layers**: The backend follows a standard API -> Service -> Data Model architecture.
-   **Documentation**: For in-depth architectural details, consult `prerelease_dev_docs/ARCHITECTURE.md`.
