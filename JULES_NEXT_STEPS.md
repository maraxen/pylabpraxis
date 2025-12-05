# Jules Next Steps

This file contains tasks for future agents to complete.

1.  **Fix Pyright Errors in `deck_manager.py`**
    *   File: `praxis/backend/core/asset_manager/deck_manager.py`
    *   Issue: `Arguments missing for parameters "name", "fqn", "location", "plr_state", "plr_definition", "properties_json"` in constructor calls.
    *   Action: Investigate the class instantiation (likely `Deck` or similar) and ensure all required arguments are provided.

2.  **Fix Pyright Errors in `resource_manager.py`**
    *   File: `praxis/backend/core/asset_manager/resource_manager.py`
    *   Issue: `Arguments missing for parameters "name", "fqn", "location", "plr_state", "plr_definition", "properties_json"` in multiple locations.
    *   Action: Similar to `deck_manager.py`, correct the instantiation of resource objects.

3.  **Fix Pyright Errors in `filesystem.py`**
    *   File: `praxis/backend/core/filesystem.py`
    *   Issue: `open` is marked as overload but missing implementations, and `PathLike` type incompatibility in `__new__`.
    *   Action: Fix the type hints and overloads to satisfy Pyright.

4.  **Fix Pyright Service Import Errors in Orchestrator**
    *   File: `praxis/backend/core/orchestrator/execution.py` (and others in `orchestrator/`)
    *   Issue: `reportAttributeAccessIssue` claiming methods like `update_run_status` are not in `praxis.backend.services`.
    *   Action: Check imports (circular dependency workarounds?) and ensure the services module exposes these functions correctly for static analysis.

5.  **Fix Pyright Errors in `protocol_preparation.py`**
    *   File: `praxis/backend/core/orchestrator/protocol_preparation.py`
    *   Issue: `None` is not awaitable (likely a missing return value or incorrect await) and `actual_type_str` attribute access issues.
    *   Action: Correct the async logic and property access on `ParameterMetadataModel`.

6.  **Fix Pyright Errors in `protocol_code_manager.py`**
    *   File: `praxis/backend/core/protocol_code_manager.py`
    *   Issue: Accessing `accession_id` on `FunctionProtocolDefinitionCreate` (Pydantic model).
    *   Action: Determine if the code should be using a Response model or an ORM object, or if the field should be added/accessed differently.

7.  **Fix Pyright Errors in `workcell_runtime/machine_manager.py`**
    *   File: `praxis/backend/core/workcell_runtime/machine_manager.py`
    *   Issue: Accessing unknown attribute `machine_counterpart_accession_id` on `ResourceOrm`/`MachineOrm`.
    *   Action: Verify the ORM model definitions and update the code to use the correct relationship or field name.

8.  **Fix Pyright Errors in Utilities**
    *   File: `praxis/backend/utils/db.py` and `praxis/backend/utils/accession_resolver.py`
    *   Issue: Type mismatch (`None` passed to `str.replace`) and attribute access on `object`.
    *   Action: Add type guards or assertions to ensure safety.

9.  **Fix Test Failures in `test_function_data_outputs.py`**
    *   File: `tests/api/test_function_data_outputs.py`
    *   Issue: Multiple failures (sFFFF).
    *   Action: Debug and fix the tests. Likely related to data setup or API changes.

10. **Fix Test Failures in `test_well_data_outputs.py`**
    *   File: `tests/api/test_well_data_outputs.py`
    *   Issue: Multiple failures (sFFFF).
    *   Action: Debug and fix the tests.

11. **Fix Test Failures in `test_function_data_output_orm.py`**
    *   File: `tests/models/test_orm/test_function_data_output_orm.py`
    *   Issue: Errors (E) during execution.
    *   Action: Investigate if this is related to the API failures (shared model/logic issues).

12. **Fix Test Failures in `test_parameter_definition_orm.py`**
    *   File: `tests/models/test_orm/test_parameter_definition_orm.py`
    *   Issue: Errors (E) during execution.
    *   Action: Fix the ORM test errors.

13. **Fix Test Failures in `test_protocol_code_manager.py`**
    *   File: `tests/core/test_protocol_code_manager.py`
    *   Issue: Failures (F) in protocol code management logic.
    *   Action: Address the logic errors causing these tests to fail.

14. **Fix Test Failure in `test_e2e_flow.py`**
    *   File: `tests/api/test_e2e_flow.py`
    *   Issue: Single failure (F).
    *   Action: This is a critical E2E test. Prioritize fixing this to ensure the main flow works.

15. **Investigate and Resolve Test Suite Timeouts**
    *   Scope: Full Test Suite
    *   Issue: `uv run pytest` times out.
    *   Action: Identify slow-running tests (possibly using `--durations=10`) and optimize them. Ensure no tests are hanging indefinitely (e.g., waiting on a lock or event that never happens).
