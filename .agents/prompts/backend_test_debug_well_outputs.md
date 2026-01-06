# Backend Test Debugging: `test_well_outputs.py`

**Date:** 2026-01-06
**Status:** In Progress - Paused for Agent Handoff

## Problem Summary

The `tests/services/test_well_outputs.py` test suite has 9 persistent failures related to `NOT NULL constraint failed: function_data_outputs.function_call_log_accession_id`. The root cause appears to be a complex interaction between SQLAlchemy's dataclass-style ORM mapping and how foreign key IDs are populated when creating `FunctionDataOutputOrm` instances.

## Key Findings

1. **Factory Issues:** `FunctionDataOutputFactory` in `tests/factories.py` uses `factory.SubFactory` and `factory.LazyAttribute` to create dependencies. However, these dependencies are not being correctly committed/flushed to the database before `FunctionDataOutputOrm` is created, causing foreign key violations.

2. **ORM Model Complexity:** `FunctionDataOutputOrm` in `praxis/backend/models/orm/outputs.py` uses `kw_only=True` on `function_call_log_accession_id` (line 74) to satisfy Python dataclass argument ordering rules. This is necessary because fields with defaults must come after fields without defaults. The relationship `function_call_log` has `default=None`.

3. **Relationship vs. Foreign Key Mismatch:** When creating `FunctionDataOutputOrm`, you can either:
    * Pass the `function_call_log_accession_id` directly (as UUID).
    * Pass the `function_call_log` relationship object and let SQLAlchemy infer the ID.
    The current test attempts to pass both, and the FK ID is passed as a string (line 48 of `test_well_outputs.py`), which causes a `ProgrammingError: Error binding parameter`.

4. **WellDataOutputFactory Dependency:** `WellDataOutputFactory` depends on `FunctionDataOutputFactory`, which propagates the issue to all tests that use `WellDataOutputFactory.create()`.

## Files Modified (This Session)

* `tests/services/test_well_outputs.py`: Multiple attempts to manually create `FunctionDataOutputOrm` and `FunctionCallLogOrm` to bypass factory issues. Current state has two `FunctionDataOutputOrm` instantiation blocks (a syntax error was introduced).
* `praxis/backend/models/orm/outputs.py`: `kw_only=True` was temporarily removed and then re-added (no net change).
* `tests/factories.py`: `accession_id = factory.LazyFunction(uuid7)` was added to `FunctionCallLogFactory` and `FunctionDataOutputFactory`.
* `tests/services/test_debug_orm.py`: Created as an isolated test to reproduce ORM issues (can be deleted).

## Recommended Next Steps

1. **Clean up `test_well_outputs.py`:** View the file and remove duplicate/debug code. The test `test_create_well_data_output` currently has two `FunctionDataOutputOrm` instantiations.

2. **Fix `FunctionDataOutputFactory`:**
    * The factory should NOT use `kw_only=True` fields for direct assignment. Instead, override `_create` to:
        1. Create `ProtocolRunOrm` and `FunctionCallLogOrm` dependencies.
        2. Flush the session.
        3. Instantiate `FunctionDataOutputOrm` with FK IDs taken from the flushed dependencies.
        4. Add and flush `FunctionDataOutputOrm`.
    * Alternatively, pass relationship objects instead of IDs and ensure SQLAlchemy correctly infers FK values during flush.

3. **Test with Relationship Objects:** Modify `test_create_well_data_output` to pass `function_call_log=function_call_log` (the object) instead of `function_call_log_accession_id=...`. Verify if SQLAlchemy correctly populates the FK on flush. This was attempted but the test file now has syntax issues.

4. **Fix other tests:** Once the factory is fixed, all tests using `WellDataOutputFactory` and `FunctionDataOutputFactory` should work.

## Debug Commands

```bash
# Run only the well_outputs tests
uv run pytest -v -s tests/services/test_well_outputs.py

# Run a single test for faster iteration
uv run pytest -v -s tests/services/test_well_outputs.py::test_create_well_data_output

# Run the isolated debug test
uv run pytest -v -s tests/services/test_debug_orm.py
```

## Context Files

* `tests/services/test_well_outputs.py` - The failing test file.
* `tests/factories.py` - Factory definitions, especially `FunctionDataOutputFactory`, `FunctionCallLogFactory`, `WellDataOutputFactory`.
* `praxis/backend/models/orm/outputs.py` - ORM models for `FunctionDataOutputOrm` and `WellDataOutputOrm`.
* `praxis/backend/models/orm/protocol.py` - ORM models for `FunctionCallLogOrm` and `ProtocolRunOrm`.
* `tests/conftest.py` - Pytest fixtures, including `db_session` which assigns session to factories.
