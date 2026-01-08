
# Skipped Tests Investigation

**Status:** Complete
**Batch:** 260107

## Summary

Audited and resolved skipped tests in both backend (Python) and frontend (Angular).

### Actions Taken

1. **Backend (`tests/core/test_orchestrator.py`)**:
    - Enabled `test_get_protocol_definition_orm_from_db`.
    - Enabled `test_handle_protocol_execution_error`.
    - **Fix**: Refactored tests to correctly mock dependency injection properties (`protocol_definition_service`, `protocol_run_service`) instead of attempting to patch module-level imports which are not used in the class implementation.
2. **Frontend (`asset-selector.component.spec.ts`)**:
    - Removed dead code (`it.skip` blocks) that referenced deleted component methods (`filteredAssets$`, `plrTypeFilter`, etc.).
3. **Frontend (`welcome-dialog` & `wizard-state`)**:
    - Verified these tests are currently active and passing (no skips found).

### Verification

- `uv run pytest tests/core/test_orchestrator.py` -> All Pass
- `npx vitest run ...` -> All Pass
