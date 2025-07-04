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

## Testing Strategy

For backend components (core, services, api, models, utils - excluding `commons`):
1.  **Ensure Test Presence**: Verify that each component file has a corresponding test file.
2.  **Consistency and Completeness**: Ensure tests are consistent with the current state of the component and provide comprehensive coverage.
3.  **Ruff Linting**:
    *   Initially, address only critical Ruff issues (e.g., `F`, `E`, `B` categories).
    *   Once critical issues are resolved, evaluate and address more stylistic or code sanitation principle-based issues.
4.  **Pyright Type Checking**: Utilize `pyright` for comprehensive static type analysis to ensure type soundness and catch potential type-related bugs.

## LAST SESSION

**Date:** July 2, 2025

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
