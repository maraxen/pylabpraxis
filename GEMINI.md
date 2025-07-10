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

## WORK IN PROGRESS

**Date:** July 9, 2025

**Development Plan:**

*   **Phase 1: Refactor and Enhance the Service Layer** (Completed)
    1.  **Enhance `plr_type_base.py`**: Added a new `DiscoverableTypeServiceBase` abstract class to `praxis/backend/services/plr_type_base.py`.
    2.  **Refactor `ResourceTypeDefinitionService`**: Refactored this service to inherit from `DiscoverableTypeServiceBase` and moved the resource discovery logic from `asset_manager.py` into this service's `discover_and_synchronize_type_definitions` method, ensuring comprehensive metadata extraction.
    3.  **Implement `MachineTypeDefinitionService` and `DeckTypeDefinitionService`**: Created `machine_type_definition.py` and `deck_type_definition.py` to inherit from `DiscoverableTypeServiceBase` and implement the `discover_and_synchronize_type_definitions` methods.
    4.  **Refactor `DiscoveryService`**: Updated `discovery_service.py` to orchestrate all discovery, including triggering the `discover_and_synchronize_type_definitions` method on the type definition services.

*   **Phase 2: Implement the Discovery Trigger Mechanism** (Completed)
    1.  **Create API Endpoint**: (To be implemented in the next step, but the service is ready).
    2.  **Implement Startup Event**: Modified `main.py` to call `DiscoveryService.discover_and_sync_all_definitions` during the FastAPI startup event.

*   **Phase 3: Update Documentation (`GEMINI.md`)** (In Progress)
    1.  After the discovery framework is in place, write a comprehensive summary of the new, clarified architecture and add it to `GEMINI.md`.

*   **Phase 4: Pydantic Model Refactoring** (In Progress)
    1.  Refactor `FunctionInfo` to `FunctionProtocolDefinitionCreate` within `protocol.py`.
    2.  Convert `RuntimeAssetRequirement` to a proper Pydantic model.

*   **Phase 5: API Layer Refactoring** (In Progress)
    1.  Implement `crud_router_factory` for generic CRUD operations.
    2.  Refactor existing API endpoints to use `crud_router_factory`.

*   **Phase 6: Service Layer Refactoring** (In Progress)
    1.  Refactor services to inherit from `CRUDBase`.

*   **Phase 7: Pyright and Ruff Error Resolution** (In Progress)
    1.  Resolve remaining `pyright` errors.
    2.  Resolve remaining `ruff` errors.

## LAST SESSION

**Date:** July 9, 2025

**Accomplished Milestones:**
*   Addressed all `B` flag errors from Ruff.
*   Successfully configured Ruff to exclude the `praxis/backend/commons/` directory.
*   Refactored `acquire_asset_lock` in `praxis/backend/core/asset_lock_manager.py` to use a Pydantic model (`AcquireAssetLock`) for arguments.
*   Replaced magic values with constants in `asset_lock_manager.py`.
*   Refactored `cleanup_expired_locks` in `asset_lock_manager.py` by extracting `_cleanup_single_lock`.
*   Refactored `acquire_resource` in `praxis/backend/core/asset_manager.py` by extracting `_find_resource_to_acquire` and `_handle_location_constraints`.
*   Created a new Pydantic model `DecoratedFunctionInfo` in `praxis/backend/models/decorators_pydantic_models.py`.
*   Moved `CreateProtocolDefinitionData` from `asset_lock_manager_pydantic_models.py` to `decorators_pydantic_models.py`.
*   Updated `praxis/backend/core/decorators.py` to use `DecoratedFunctionInfo` and refactored `_create_protocol_definition` to accept a Pydantic model.
*   Refactored `protocol_function` in `praxis/backend/core/decorators.py` to use `_process_wrapper_arguments` helper function.
*   Extracted `_update_resource_acquisition_status` from `acquire_resource` in `praxis/backend/core/asset_manager.py`.
*   Extracted `_handle_resource_release_location` from `release_resource` in `praxis/backend/core/asset_manager.py`.
*   Extracted `_is_deck_resource` from `release_resource` in `praxis/backend/core/asset_manager.py`.
*   Extracted `_prepare_function_arguments` from `protocol_function` and `wrapper` in `praxis/backend/core/decorators.py`.
*   Refactored `_prepare_arguments` in `praxis/backend/core/orchestrator.py` by extracting `_process_input_parameters`, `_inject_praxis_state`, `_acquire_assets`, and `_handle_deck_preconfiguration`.
*   Fixed critical `F821` and `PLE1142` errors in `praxis/backend/core/orchestrator.py` by correcting variable scoping and code placement within `_handle_protocol_execution_error`.
*   Fixed Pyright errors in `praxis/backend/services/deck.py` by aligning method signatures with `CRUDBase` and correcting argument types.
*   Fixed Pyright errors in `praxis/backend/services/entity_linking.py` by aligning parameter names.
*   Fixed Pyright errors in `praxis/backend/services/function_output_data.py` by adjusting `SearchFilters` attribute access.
*   Fixed Pyright errors in `praxis/backend/services/machine.py` by correcting `machine_data_service_log` usage, aligning method signatures with `CRUDBase`, and correcting argument types.
*   Fixed Pyright errors in `praxis/backend/services/plate_viz.py` by ensuring `data_range` dictionary values are floats.
*   Fixed Pyright errors in `praxis/backend/services/protocols.py` by removing `json.loads` for dictionary inputs, correcting `ProtocolRunOrm` attribute access, and adjusting `apply_date_range_filters` argument types.
*   Fixed Pyright errors in `praxis/backend/services/resource.py` by aligning method signatures with `CRUDBase` and correcting argument types.
*   Fixed Pyright errors in `praxis/backend/services/scheduler.py` by modifying `list_schedule_entries` signature and updating sorting logic.
*   Fixed Pyright errors in `praxis/backend/services/workcell.py` by aligning method signatures with `CRUDBase`, addressing `initial_state` attribute access, and correcting argument types.
*   Created `pyrightconfig.json` to configure Pyright.
*   **Pydantic Model Refactoring:**
    *   Introduced `PLRTypeDefinition` in `praxis/backend/models/pydantic/plr_sync.py` as a base for PyLabRobot type definitions.
    *   Added/modified `FunctionProtocolDefinitionCreate`, `FunctionProtocolDefinitionUpdate`, and `FunctionProtocolDefinitionResponse` in `praxis/backend/models/pydantic/protocol.py`.
    *   Updated `DeckTypeDefinitionCreate`, `DeckTypeDefinitionUpdate`, `DeckTypeDefinitionResponse` in `praxis/backend/models/pydantic/deck.py` to inherit from `PLRTypeDefinition` models.
    *   Updated `ResourceTypeDefinitionCreate`, `ResourceTypeDefinitionUpdate`, `ResourceTypeDefinitionResponse` in `praxis/backend/models/pydantic/resource.py` to inherit from `PLRTypeDefinition` models.
    *   Refactored `DeckTypeDefinitionUpdate` in `praxis/backend/models/pydantic/deck.py` to make all fields optional, aligning with best practices for update models.
*   **API Layer Refactoring (using `crud_router_factory`):**
    *   Created `praxis/backend/api/utils/crud_router_factory.py` for generic CRUD operations.
    *   Refactored `praxis/backend/api/decks.py`, `praxis/backend/api/machines.py`, `praxis/backend/api/outputs.py`, `praxis/backend/api/protocols.py`, `praxis/backend/api/resources.py`, `praxis/backend/api/scheduler.py`, and `praxis/backend/api/workcell_api.py` to use `crud_router_factory`.
    *   Renamed `praxis/backend/api/function_data_outputs.py` to `praxis/backend/api/outputs.py`.
    *   Renamed `praxis/backend/api/scheduler_api.py` to `praxis/backend/api/scheduler.py`.
*   **Service Layer Refactoring (inheriting from `CRUDBase`):**
    *   Refactored `FunctionDataOutputService` (now `FunctionDataOutputCRUDService`), `WellDataOutputService` (now `WellDataOutputCRUDService`), `MachineService`, `ResourceService`, `ProtocolRunService`, and `WorkcellService` to inherit from `CRUDBase`.
    *   Created `ProtocolDefinitionCRUDService` and `ResourceTypeDefinitionCRUDService`.
    *   Refactored `DeckTypeDefinitionService` to `DeckTypeDefinitionCRUDService` and fixed a bug in its discovery logic.
*   **Pyright and Ruff Error Resolution:**
    *   Addressed `reportMissingImports` errors.
    *   Fixed many type mismatches and incorrect service calls related to `CRUDBase` and `DiscoverableTypeServiceBase` overrides.
    *   Corrected the type hint for `apply_date_range_filters` in `praxis/backend/services/utils/query_builder.py` to correctly use `InstrumentedAttribute`.

**Remaining Work (Pyright and Ruff errors):**
*   **Phase 1: Resolve Remaining Pyright Errors**
    *   Address `reportMissingImports` by installing project dependencies and ensuring `PYTHONPATH` is correctly configured.
    *   Address other Pyright errors in `praxis/backend/api`, `praxis/backend/commons`, `praxis/backend/core`, `praxis/backend/models`, `praxis/backend/services`, and `praxis/backend/utils`.
*   **Phase 4: Pydantic Model Refactoring**
    *   Convert `RuntimeAssetRequirement` to a proper Pydantic model.

**Remaining Work (PLR and C errors):**
*   `praxis/backend/core/asset_manager.py`:
    *   `acquire_resource`: Still has C901 (complexity), PLR0912 (too many branches), PLR0915 (too many statements).
    *   `release_resource`: No longer has PLR0913 (too many arguments).
*   `praxis/backend/core/decorators.py`:
    *   `protocol_function`: No longer has C901 (complexity), PLR0913 (too many arguments), PLR0915 (too many statements).
    *   `decorator`: Still has C901 (complexity), PLR0915 (too many statements).
    *   `wrapper`: No longer has C901 (complexity), PLR0912 (too many branches), PLR0915 (too many statements).
*   `praxis/backend/core/orchestrator.py`:
    *   `_execute_protocol_main_logic`: PLR0913 (too many arguments).
    *   `_load_callable_from_fqn`: SLF001 (Private member accessed).
    *   `_acquire_assets`: PERF203 (`try`-`except` within a loop).
    *   `_prepare_arguments`: TRY003, EM101 (exception messages).
    *   `_handle_deck_preconfiguration`: TRY003, EM101 (exception messages).
    *   `_handle_protocol_execution_error`: PERF203 (`try`-`except` within a loop), G201 (logging.exception).
    *   `execute_protocol`: PLR0913 (too many arguments).
    *   `execute_existing_protocol_run`: G201 (logging.exception).
*   `praxis/backend/core/protocol_execution_service.py`:
    *   `execute_protocol_immediately`: PLR0913 (too many arguments).
    *   `schedule_protocol_execution`: PLR0913 (too many arguments).
*   `praxis/backend/core/workcell_runtime.py`:
    *   `_get_calculated_location`: C901 (complexity), PLR0912 (too many branches).
    *   `initialize_machine`: C901 (complexity), PLR0912 (too many branches), PLR0915 (too many statements).
    *   `create_or_get_resource`: C901 (complexity), PLR0912 (too many branches).
    *   `assign_resource_to_deck`: C901 (complexity), PLR0912 (too many branches).
    *   `PLR2004` magic value in `_get_calculated_location`.
*   `praxis/backend/services/deck_position.py`:
    *   `_process_position_definitions`: C901 (complexity).
    *   `create_deck_position_definitions`: C901 (complexity).
    *   `update_deck_position_definition`: C901 (complexity), PLR0913 (too many arguments), PLR0912 (too many branches), PLR0915 (too many statements).
*   `praxis/backend/services/deck_type_definition.py`:
    *   `_process_position_definitions`: C901 (complexity).
    *   `create_deck_type_definition`: PLR0913 (too many arguments).
    *   `update_deck_type_definition`: C901 (complexity), PLR0913 (too many arguments), PLR0912 (too many branches), PLR0915 (too many statements).
*   `praxis/backend/services/discovery_service.py`:
    *   `_extract_protocol_definitions_from_paths`: C901 (complexity), PLR0912 (too many branches), PLR0915 (too many statements).
    *   `discover_and_upsert_protocols`: C901 (complexity).
*   `praxis/backend/services/entity_linking.py`:
    *   `_create_or_link_resource_counterpart_for_machine`: C901 (complexity), PLR0913 (too many arguments).
    *   `_create_or_link_machine_counterpart_for_resource`: PLR0913 (too many arguments).
*   `praxis/backend/services/plate_parsing.py`:
    *   `read_plate_dimensions`: C901 (complexity), PLR0911 (too many return statements), PLR0912 (too many branches).
    *   `PLR2004` magic value.
*   `praxis/backend/services/protocols.py`:
    *   `update_protocol_run_status`: PLR0913 (too many arguments).
*   `praxis/backend/services/resource_type_definition.py`:
    *   `create_resource_definition`: PLR0913 (too many arguments).
    *   `update_resource_definition`: C901 (complexity), PLR0913 (too many arguments).
*   `praxis/backend/services/scheduler.py`:
    *   `create_schedule_entry`: PLR0913 (too many arguments).
    *   `list_schedule_entries`: C901 (complexity), PLR0913 (too many arguments), PLR0912 (too many branches).
    *   `update_schedule_entry_status`: PLR0913 (too many arguments).
    *   `create_asset_reservation`: PLR0913 (too many arguments).
    *   `list_asset_reservations`: PLR0913 (too many arguments).
    *   `log_schedule_event`: PLR0913 (too many arguments).
*   `praxis/backend/services/well_outputs.py`:
    *   `read_well_data_outputs`: PLR0913 (too many arguments).
*   `praxis/backend/utils/logging.py`:
    *   `_process_exception`: PLR0913 (too many arguments).
    *   `log_async_runtime_errors`: PLR0913 (too many arguments).
    *   `log_runtime_errors`: PLR0913 (too many arguments).
*   `praxis/backend/utils/plr_inspection.py`:
    *   `_get_accepted_categories_for_resource_holder`: C901 (complexity).
*   `praxis/backend/utils/sanitation.py`:
    *   `tip_mapping`: C901 (complexity), PLR0913 (too many arguments).
