# Next Steps

## 1. Verify Broader Test Suite
*   **Run Service Tests**: Execute `uv run pytest tests/services/` to identify any failures in the service layer. Now that ORM models are stable, service tests should be verifiable.
*   **Run Core Tests**: Execute `uv run pytest tests/core/` to verify core logic.

## 2. Refactoring Tasks (High Priority)
*   **Refactor `workcell_runtime.py`**: The module `praxis/backend/core/workcell_runtime/core.py` (or related files) is identified as a large module needing refactoring into submodules.
*   **Refactor `asset_manager.py`**: The module `praxis/backend/core/asset_manager.py` (or package) is also identified for refactoring.

## 3. API Testing
*   **Run API Tests**: Execute `uv run pytest tests/api/` to ensure the REST API endpoints are functioning correctly with the fixed ORM layer.
