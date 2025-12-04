# Next Steps

The work has been divided into parallel chunks to increase testing coverage and stability.

## Resolved Steps

### Chunk A: Missing Service Tests
*   `tests/services/test_entity_linking.py` (Created)
*   `tests/services/test_plate_parsing.py` (Created)
*   `tests/services/test_plate_viz.py` (Created)
*   Consolidated discovery service tests.

### Chunk B: Fix ORM Model Tests
*   Addressed initial issues in `test_asset_requirement_orm.py` through `test_schedule_entry_orm.py`.

### Chunk C: Fix API Tests
*   Addressed initial issues in `test_decks.py`, `test_resources.py`, etc.

### Chunk D: Fix Service Layer Regressions (Part 1)
*   `tests/services/test_entity_linking.py`

### Chunk E: Fix Service Layer Regressions (Part 2)
*   `tests/services/test_resource_service.py`

### Chunk F: Fix Service Layer Regressions (Part 3)
*   `tests/services/test_well_outputs.py`

### Chunk G: Fix ORM Layer Regressions (Part 1)
*   `tests/models/test_orm/test_deck_orm.py`

### Chunk H: Fix ORM Layer Regressions (Part 2)
*   `tests/models/test_orm/test_function_protocol_definition_orm.py`

### Chunk I: Fix ORM Layer Regressions (Part 3)
*   `tests/models/test_orm/test_machine_definition_orm.py`
*   `tests/models/test_orm/test_machine_orm.py`

### Chunk J: Fix ORM Layer Regressions (Enums)
*   `tests/models/test_enums/test_machine_enums.py`
*   `tests/models/test_enums/test_protocol_enums.py`

### Chunk K: Fix Core Layer Regressions (Decorators)
*   `tests/core/decorators/test_definition_builder.py`
*   `tests/core/decorators/test_parameter_processor.py`
*   `tests/core/decorators/test_protocol_decorator.py`

### Chunk L: Fix Core Layer Regressions (Scheduler)
*   `tests/core/test_scheduler.py`

### Chunk M: Resolve Linting Errors (Sanitation & Type Inspection)
*   `praxis/backend/utils/sanitation.py`
*   `praxis/backend/utils/type_inspection.py`

### Chunk N: Resolve Linting Errors (General)
*   Run `ruff check .` and address remaining issues.

## Next Steps

The following chunks target critical ORM failures, API regressions, and coverage gaps identified in the latest assessment (38% coverage, widespread ORM/API failures).

### Chunk 1: Fix ProtocolRun Factory & ORM (Critical)
**Goal**: Fix broken Factory/ORM logic causing 100% failure in `ProtocolRun` tests.
**Files to Fix**:
*   `tests/models/test_orm/test_protocol_run_orm.py`
*   `tests/factories.py` (ProtocolRunFactory)

### Chunk 2: Fix FunctionCallLog Factory & ORM
**Goal**: Fix broken Factory/ORM logic for Function Call Logs.
**Files to Fix**:
*   `tests/models/test_orm/test_function_call_log_orm.py`
*   `tests/factories.py` (FunctionCallLogFactory)

### Chunk 3: Fix Asset Requirement ORM
**Goal**: Fix errors in Asset Requirement ORM tests.
**Files to Fix**:
*   `tests/models/test_orm/test_asset_requirement_orm.py`

### Chunk 4: Fix Asset Reservation ORM
**Goal**: Fix errors in Asset Reservation ORM tests.
**Files to Fix**:
*   `tests/models/test_orm/test_asset_reservation_orm.py`

### Chunk 5: Fix Function/Well Data Output ORM
**Goal**: Fix errors in Data Output ORM tests.
**Files to Fix**:
*   `tests/models/test_orm/test_function_data_output_orm.py`
*   `tests/models/test_orm/test_well_data_output_orm.py` (if exists/failing)

### Chunk 6: Fix Deck API Tests
**Goal**: Fix `TypeError` failures in Deck API tests.
**Files to Fix**:
*   `tests/api/test_decks.py`

### Chunk 7: Fix Protocol Definition API Tests
**Goal**: Fix failures in Protocol Definition API tests.
**Files to Fix**:
*   `tests/api/test_protocol_definitions.py`

### Chunk 8: Fix Protocol Run API Tests
**Goal**: Fix failures in Protocol Run API tests (likely linked to Chunk 1).
**Files to Fix**:
*   `tests/api/test_protocol_runs.py`

### Chunk 9: Fix Well Data Output API Tests
**Goal**: Fix failures in Well Data Output API tests.
**Files to Fix**:
*   `tests/api/test_well_data_outputs.py`

### Chunk 10: Deck Service Coverage
**Goal**: Increase coverage for Deck Service from 26% to >80%.
**Files to Fix**:
*   `praxis/backend/services/deck.py`
*   `tests/services/test_deck_service.py` (add tests)

### Chunk 11: Protocol Definition Service Coverage
**Goal**: Increase coverage for Protocol Definition Service from 25% to >80%.
**Files to Fix**:
*   `praxis/backend/services/protocol_definition.py`
*   `tests/services/test_protocol_definition_service.py` (or existing test file)

### Chunk 12: Scheduler Service Coverage
**Goal**: Increase coverage for Scheduler Service from 0% (if accurate) to >80%.
**Files to Fix**:
*   `praxis/backend/services/scheduler.py`
*   `tests/core/test_scheduler.py` (Verify it covers service layer or add service tests)

### Chunk 13: Fix Pyright Errors (Models)
**Goal**: Resolve static type errors in Pydantic/ORM models.
**Files to Fix**:
*   `praxis/backend/models/` (as reported by Pyright)

### Chunk 14: Fix Pyright Errors (Services)
**Goal**: Resolve static type errors in Service layer.
**Files to Fix**:
*   `praxis/backend/services/` (as reported by Pyright)

### Chunk 15: Fix Ruff Linting
**Goal**: Resolve remaining 53 Ruff errors.
**Files to Fix**:
*   Run `ruff check .` and fix reported issues.
