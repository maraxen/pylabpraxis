# Next Steps

The work has been divided into parallel chunks to increase testing coverage and stability.

## Chunk A: Missing Service Tests
**Goal**: Create service tests for untested services.
**Files to Create/Update**:
*   `tests/services/test_entity_linking.py` (for `praxis/backend/services/entity_linking.py`)
*   `tests/services/test_plate_parsing.py` (for `praxis/backend/services/plate_parsing.py`)
*   `tests/services/test_plate_viz.py` (for `praxis/backend/services/plate_viz.py`)
*   **Task**: Consolidate `praxis/backend/services/tests/test_discovery_service.py` into `tests/services/test_discovery_service.py`.

## Chunk B: Fix ORM Model Tests
**Goal**: Fix the currently failing/erroring ORM tests to establish a solid data layer foundation.
**Files to Fix**:
*   `tests/models/test_orm/test_asset_requirement_orm.py`
*   `tests/models/test_orm/test_function_call_log_orm.py`
*   `tests/models/test_orm/test_function_data_output_orm.py`
*   `tests/models/test_orm/test_parameter_definition_orm.py`
*   `tests/models/test_orm/test_protocol_run_orm.py`
*   `tests/models/test_orm/test_schedule_entry_orm.py`

## Chunk C: Fix API Tests
**Goal**: Fix the failing API tests.
**Files to Fix**:
*   `tests/api/test_decks.py`
*   `tests/api/test_resources.py`
*   `tests/api/test_workcells.py`
*   `tests/api/test_well_data_outputs.py`
