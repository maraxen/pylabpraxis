# Backend Test Debugging - Staged Plan

**Date:** 2026-01-06
**Status:** Ready for Agent Handoff

## Overview

This document outlines a staged approach to debugging and fixing all backend test failures. The test suite takes >90 seconds to run, so targeted debugging is recommended.

---

## Stage 1: Fix Test Factory Infrastructure (HIGHEST PRIORITY)

**Problem:** `FunctionDataOutputFactory` and related factories fail to correctly populate FK fields when creating ORM instances, causing `NOT NULL constraint failed` errors.

**Affected Tests:**

- `tests/services/test_well_outputs.py` (9 failures)
- `tests/api/test_function_data_outputs.py` (likely affected)
- Any test using `WellDataOutputFactory` or `FunctionDataOutputFactory`

**Root Cause:** SQLAlchemy dataclass-style ORM + Factory Boy `SubFactory` interaction doesn't properly flush dependencies before reading FK values.

**Fix Strategy:**

1. View `tests/services/test_well_outputs.py` and clean up duplicate/debug code
2. Modify `FunctionDataOutputFactory` in `tests/factories.py` to override `_create()`:
   - Manually create and flush `ProtocolRunOrm`, `FunctionCallLogOrm` dependencies
   - Instantiate `FunctionDataOutputOrm` with FK IDs from flushed objects
   - Add and flush `FunctionDataOutputOrm`
3. Apply same pattern to `WellDataOutputFactory`

**Debug Command:**

```bash
uv run pytest -v -s tests/services/test_well_outputs.py::test_create_well_data_output
```

**Key Files:**

- `tests/factories.py` - Factory definitions
- `tests/services/test_well_outputs.py` - Failing tests
- `praxis/backend/models/orm/outputs.py` - ORM models

---

## Stage 2: Pydantic Validation Errors

**Problem:** Some tests fail with `pydantic_core._pydantic_core.ValidationError` for missing required fields.

**Example Error:**

```
ValidationError: 2 validation errors for WellDataOutputCreate
  well_row: Field required
  well_column: Field required
```

**Fix Strategy:**

1. Identify all Pydantic models used in tests
2. Ensure test data includes all required fields
3. Check if model definitions were recently changed

**Key Files:**

- `praxis/backend/models/pydantic_internals/outputs.py` - Pydantic output models
- Tests using `*Create` or `*Update` models

---

## Stage 3: API Layer Tests

**Problem:** API tests may fail due to underlying service/factory issues from Stage 1.

**Affected Tests:**

- `tests/api/test_function_data_outputs.py`
- Other API tests depending on outputs

**Fix Strategy:**

1. Complete Stage 1 first (factory fixes)
2. Run API tests to see if fixes propagate
3. Fix any remaining API-specific issues

**Debug Command:**

```bash
uv run pytest -v -s tests/api/ --no-cov
```

---

## Stage 4: Core Module Tests

**Problem:** Core tests may have independent issues unrelated to factories.

**Affected Tests:**

- `tests/core/test_protocol_code_manager.py`
- Other core tests

**Fix Strategy:**

1. Run core tests in isolation after Stage 1-3
2. Debug any remaining failures

**Debug Command:**

```bash
uv run pytest -v -s tests/core/ --no-cov
```

---

## Stage 5: Full Suite Verification

**Goal:** Run complete backend test suite and verify all tests pass.

**Debug Command:**

```bash
uv run pytest tests/services tests/api tests/core -v --no-cov
```

---

## Quick Reference

### Files to Fix (Priority Order)

1. `tests/factories.py` - Fix factory FK handling
2. `tests/services/test_well_outputs.py` - Clean up debug code
3. `praxis/backend/models/orm/outputs.py` - Reference (don't modify unless necessary)

### Related Documentation

- `.agents/TECHNICAL_DEBT.md` - Documents the factory issue as high-priority debt
- `.agents/prompts/backend_test_debug_well_outputs.md` - Detailed debugging notes for Stage 1

### Test Run Tips

- Use `--no-cov` to skip coverage (faster)
- Use `-s` to see print output
- Use `::test_name` to run single test
- Use `timeout 60` prefix to prevent hangs
