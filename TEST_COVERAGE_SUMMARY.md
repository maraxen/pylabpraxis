# PyLabPraxis Test Coverage Summary

**Status as of:** Latest Assessment (Dec 4, 2024)

## Overview

The test environment is functional with PostgreSQL 18.
-   **Total Coverage**: ~38% (Goal: >80%)
-   **Test Status**: Significant failures in ORM and API layers. Core layer is mostly stable.
-   **Linting/Types**: 53 Ruff errors, 67 Pyright errors.

**To run tests:**
```bash
# Verify database is running (should be pre-provisioned in CI/Jules env)
sudo docker ps

# Run all tests (sequential recommended due to DB state handling)
uv run pytest --cov=praxis/backend --cov-report=term-missing
```

---

## Detailed Assessment

### 1. Failing Areas (High Priority)
#### ORM Models (`tests/models/test_orm/`)
Multiple models are erroring out, likely due to Factory configuration or Constructor mismatches in `MappedAsDataclass` models.
-   `test_asset_requirement_orm.py`: Error
-   `test_asset_reservation_orm.py`: Error
-   `test_function_call_log_orm.py`: Error
-   `test_function_data_output_orm.py`: Error
-   `test_parameter_definition_orm.py`: Error
-   `test_protocol_run_orm.py`: Error

#### API Endpoints (`tests/api/`)
Endpoints are failing with `TypeError`, suggesting instantiation issues in the underlying service/ORM layers.
-   `test_decks.py`: Failed (Init TypeError)
-   `test_protocol_definitions.py`: Failed
-   `test_protocol_runs.py`: Failed
-   `test_well_data_outputs.py`: Failed

### 2. Low Coverage Areas (Medium Priority)
#### Services (`praxis/backend/services/`)
-   `deck.py`: 26%
-   `protocol_definition.py`: 25%
-   `scheduler.py`: 0% (Needs verification if covered by core tests)
-   `user.py`: 0%
-   `entity_linking.py`: 17%
-   `plate_parsing.py`: 12%

### 3. Passing Areas (Stable)
-   **Core**: `test_scheduler.py`, `test_orchestrator.py`, `test_workcell_runtime.py`.
-   **ORM**: `test_deck_orm.py`, `test_machine_orm.py`, `test_function_protocol_definition_orm.py`.
-   **Enums**: Most enum tests are passing.

## Action Plan

See `JULES_NEXT_STEPS.md` for the prioritized work chunks (Chunks 1-15) to address these issues.
