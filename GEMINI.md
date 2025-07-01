This file contains instructions for the Gemini agent.

## Project Structure

The project is organized as follows:

- `praxis/backend`: Contains the backend code.
  - `praxis/backend/api`: Contains the FastAPI routers.
  - `praxis/backend/core`: Contains the core business logic.
  - `praxis/backend/models`: Contains the Pydantic and ORM models.
  - `praxis/backend/services`: Contains the service layer.
  - `praxis/backend/utils`: Contains utility functions.
- `praxis/frontend`: Contains the frontend code.
- `tests`: Contains the tests.

## Instructions

- Do not edit files in the `praxis/backend/commons` directory.
- When providing filepaths that contain spaces, ensure they are enclosed in quotes.
- When running shell commands, ensure paths are wrapped in quotes.

## Testing Strategy

For backend components (core, services, api, models, utils - excluding `commons`):
1.  **Ensure Test Presence**: Verify that each component file has a corresponding test file.
2.  **Consistency and Completeness**: Ensure tests are consistent with the current state of the component and provide comprehensive coverage.
3.  **Ruff Linting**:
    *   Initially, address only critical Ruff issues (e.g., `F`, `E`, `B` categories).
    *   Once critical issues are resolved, evaluate and address more stylistic or code sanitation principle-based issues.