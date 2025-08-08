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

## Code Review Instructions

You are an expert senior software engineer and an automated code review tool.
Your task is to review the following code written in ${language}.
Analyze the code for the following:
1.  Potential bugs and errors.
2.  Adherence to best practices and language conventions.
3.  Performance bottlenecks.
4.  Security vulnerabilities.
5.  Code style and readability.
6.  Suggests improvements for clarity and efficiency.

Provide your feedback as a JSON array of objects. Each object should represent a single review comment and must have the following structure:
{
  "lineNumber": number,
  "severity": "Critical" | "Major" | "Minor" | "Info",
  "comment": "string"
}

## Type Definition Management

A key feature of PyLabPraxis is its ability to understand the capabilities of the laboratory hardware. This is achieved through a "discover and sync" process that introspects the `pylabrobot` library to identify available resources, machines, and decks. This information is then stored in the database as "type definitions."

This process is managed by a set of specialized services that inherit from a common `TypeDefinitionServiceBase`. Each service is responsible for a specific type of asset:

*   **`ResourceTypeDefinitionService`**: Discovers all available `pylabrobot.resources` and syncs them with the database.
*   **`MachineTypeDefinitionService`**: Discovers all available `pylabrobot.machines` and syncs them with the database.
*   **`DeckTypeDefinitionService`**: Discovers all available `pylabrobot.resources.Deck` subclasses and syncs them with the database.

The `DiscoveryService` is responsible for orchestrating this process, triggering the `sync_with_source()` method on each of the type definition services.

This architecture ensures that the system always has an up-to-date understanding of the available hardware, which is then used by the `AssetManager` to create and manage live asset instances.

## Current Architecture Overview

The `DiscoveryService` now acts as the central orchestrator for discovering and synchronizing both protocol definitions and PyLabRobot type definitions (resources, machines, and decks). It leverages specialized services for each type:

*   **`ResourceTypeDefinitionService`**: Responsible for introspecting `pylabrobot.resources` to discover and synchronize resource type definitions, including comprehensive metadata such as category, ordering, and physical dimensions.
*   **`MachineTypeDefinitionService`**: Responsible for introspecting `pylabrobot.machines` to discover and synchronize machine type definitions.
*   **`DeckTypeDefinitionService`**: Responsible for introspecting `pylabrobot.resources.Deck` subclasses to discover and synchronize deck type definitions.

These type definition services inherit from `DiscoverableTypeServiceBase`, which provides a common interface for discovery and synchronization with the database. The `DiscoveryService` triggers these synchronization processes during application startup, ensuring the database is populated with the latest PLR type information.

This clear separation of concerns allows for modular and extensible type discovery, ensuring that the system accurately reflects the capabilities of the connected laboratory hardware.

## Testing Strategy

For backend components (core, services, api, models, utils - excluding `commons`):
1.  **Ensure Test Presence**: Verify that each component file has a corresponding test file.
2.  **Consistency and Completeness**: Ensure tests are consistent with the current state of the component and provide comprehensive coverage.
3.  **Ruff Linting**:
    *   Initially, address only critical Ruff issues (e.g., `F`, `E`, `B` categories).
    *   Once critical issues are resolved, evaluate and address more stylistic or code sanitation principle-based issues.
4.  **Pyright Type Checking**: Utilize `pyright` for comprehensive static type analysis to ensure type soundness and catch potential type-related bugs. When running `pyright`, we should be targeted until we are at a stage where the codebase as a whole has less than 40 `pyright` issues.

## Service Layer Transaction Management

To reduce boilerplate and ensure consistent transaction handling across the service layer, a `@handle_db_transaction` decorator has been introduced. This decorator, located in `praxis/backend/utils/db_decorator.py`, wraps database write operations to provide the following features:

1.  **Automatic Commits**: On successful execution of the decorated method, the database transaction is automatically committed.
2.  **Automatic Rollbacks**: If any exception occurs, the transaction is automatically rolled back.
3.  **Consistent Exception Handling**:
    -   `sqlalchemy.exc.IntegrityError` is caught and re-raised as a `ValueError` with a user-friendly message, indicating a potential duplicate resource.
    -   Other `ValueError` exceptions are allowed to pass through, preserving custom validation messages from the service layer.
    -   All other exceptions are caught and wrapped in a generic `ValueError` to prevent leaking implementation details.

This approach ensures that the service layer remains decoupled from the web (HTTP) layer, as it does not raise `HTTPException` directly.

## Pydantic Model Management

Pydantic models used for API requests/responses or within core/service layers should be defined in the `praxis/backend/models/pydantic` directory. This promotes consistency and avoids duplicating model definitions across the codebase.

## ISSUES TO PAY ATTENTION TO

- When an issue is repeatedly raised, it should be documented here to prevent recurrence.
- Pydantic models should be defined in the `models/pydantic` directory, not inline in other modules.

## WORK IN PROGRESS

**Date:** July 17, 2025

**Development Plan:**

*   **Phase 1: Refactor and Enhance the Service Layer** (Completed)
    1.  **Implement `@handle_db_transaction` Decorator**: Created a decorator to standardize database transaction management (`commit`, `rollback`, and exception handling) across the service layer.
    2.  **Refactor Services to Use Decorator**: Applied the decorator to all applicable services, including `CRUDBase`, to ensure atomic transactions and reduce boilerplate.
    3.  **Resolve Pyright and Ruff Errors**: Resolved all resulting type and linting errors in the service and API layers.

*   **Phase 2: Pydantic Model Refactoring** (In Progress)
    1.  Convert `RuntimeAssetRequirement` to a proper Pydantic model.

*   **Phase 3: API Layer Refactoring** (In Progress)
    1.  Refactor existing API endpoints to use `crud_router_factory`.
        -   [x] `praxis/backend/api/scheduler.py`
        -   [ ] Refactor remaining APIs.

*   **Phase 4: Core Module Refactoring** (In Progress)
    1.  Analyze and refactor `praxis/backend/core` modules for clarity, efficiency, and type safety.
        -   [ ] `praxis/backend/core/asset_manager.py` - Resolve Pyright issues.

## LAST SESSION

**Date:** July 17, 2025

**Accomplished Milestones:**
*   Updated `GEMINI.md` to reflect the completion of the service layer refactoring.

