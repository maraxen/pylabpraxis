# PyLabPraxis Test Coverage Summary

**Status as of:** Latest Assessment

## Overview

The test environment is functional with PostgreSQL 18. The test suite is collecting and running, but there is a significant number of failures in ORM models and API tests that need to be addressed.

**To run tests:**
```bash
# Verify database is running (should be pre-provisioned in CI/Jules env)
sudo docker ps

# Run all tests
uv run pytest
```

---

## Test Coverage Assessment

### 1. Commons (`praxis/backend/commons/`)
**Coverage: Excluded**
-   These modules are explicitly excluded from testing requirements per `pyproject.toml` configuration.

### 2. Services (`praxis/backend/services/`)
**Coverage: Partial**
-   **Tested**: `User`, `ProtocolRun`, `Scheduler`, `Deck` (Partial).
-   **Untested / Low Coverage**:
    -   `entity_linking.py`: No tests.
    -   `plate_parsing.py`: No tests.
    -   `plate_viz.py`: No tests.
    -   `discovery_service.py`: Has tests in `praxis/backend/services/tests/` (misplaced) and `tests/services/`. Needs consolidation.

### 3. ORM Models (`tests/models/test_orm/`)
**Coverage: High (Files exist) but Failing**
-   Tests exist for most models, but many are failing or erroring out.
-   **Failing/Erroring**:
    -   `test_asset_requirement_orm.py`
    -   `test_function_call_log_orm.py`
    -   `test_function_data_output_orm.py`
    -   `test_parameter_definition_orm.py`
    -   `test_protocol_run_orm.py`
    -   `test_schedule_entry_orm.py`

### 4. API (`tests/api/`)
**Coverage: Moderate but Failing**
-   Basic CRUD tests exist but are failing.
-   **Failing**: `test_decks.py`, `test_resources.py`, `test_workcells.py`, `test_well_data_outputs.py`.
-   **Passing**: `test_smoke.py`, `test_e2e_flow.py` (Partial).

---

## Action Plan

See `JULES_NEXT_STEPS.md` for specific work chunks to address these gaps.
