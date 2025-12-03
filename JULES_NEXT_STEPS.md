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

## Next Steps (Regressions & Coverage)

The following chunks target failing tests identified in the latest run and areas needing coverage improvement.

### Chunk D: Fix Service Layer Regressions (Part 1)
**Goal**: Fix failing tests in `test_entity_linking.py`.
**Files to Fix**:
*   `tests/services/test_entity_linking.py`

### Chunk E: Fix Service Layer Regressions (Part 2)
**Goal**: Fix failing tests in `test_resource_service.py`.
**Files to Fix**:
*   `tests/services/test_resource_service.py`

### Chunk F: Fix Service Layer Regressions (Part 3)
**Goal**: Fix failing tests in `test_well_outputs.py`.
**Files to Fix**:
*   `tests/services/test_well_outputs.py`

### Chunk G: Fix ORM Layer Regressions (Part 1)
**Goal**: Fix failing tests in `test_deck_orm.py`.
**Files to Fix**:
*   `tests/models/test_orm/test_deck_orm.py`

### Chunk H: Fix ORM Layer Regressions (Part 2)
**Goal**: Fix failing tests in `test_function_protocol_definition_orm.py`.
**Files to Fix**:
*   `tests/models/test_orm/test_function_protocol_definition_orm.py`

### Chunk I: Fix ORM Layer Regressions (Part 3)
**Goal**: Fix failing tests in Machine ORMs.
**Files to Fix**:
*   `tests/models/test_orm/test_machine_definition_orm.py`
*   `tests/models/test_orm/test_machine_orm.py`

### Chunk J: Fix ORM Layer Regressions (Enums)
**Goal**: Fix failing Enum tests.
**Files to Fix**:
*   `tests/models/test_enums/test_machine_enums.py`
*   `tests/models/test_enums/test_protocol_enums.py`

### Chunk K: Fix Core Layer Regressions (Decorators)
**Goal**: Fix failing tests in Core Decorators.
**Files to Fix**:
*   `tests/core/decorators/test_definition_builder.py`
*   `tests/core/decorators/test_parameter_processor.py`
*   `tests/core/decorators/test_protocol_decorator.py`

### Chunk L: Fix Core Layer Regressions (Scheduler)
**Goal**: Fix failing tests in Scheduler.
**Files to Fix**:
*   `tests/core/test_scheduler.py`

### Chunk M: Resolve Linting Errors (Sanitation & Type Inspection)
**Goal**: Resolve linting errors in utility modules.
**Files to Fix**:
*   `praxis/backend/utils/sanitation.py`
*   `praxis/backend/utils/type_inspection.py`

### Chunk N: Resolve Linting Errors (General)
**Goal**: Continue resolving linting errors across the backend.
**Files to Fix**:
*   Run `ruff check .` and address remaining issues.
