# Production Bugs Found During Core Module Testing

This document lists production bugs discovered during comprehensive testing of the praxis.backend.core modules. All bugs have associated skipped tests that document the expected behavior and failure scenarios.

**Test Coverage Summary:**
- Total core tests: 394
- Passing tests: 376
- Skipped tests: 18 (due to production bugs)
- Overall core coverage: 54%

---

## Bug 1: Missing `fqn` Field in FunctionProtocolDefinitionCreate

**Severity:** HIGH
**Module:** `praxis/backend/core/decorators.py`
**Line:** 193
**Tests Affected:** 12 skipped tests in `tests/core/test_decorators.py`

### Description
The `@protocol_function` decorator attempts to create a `FunctionProtocolDefinitionCreate` Pydantic model without providing the required `fqn` (fully qualified name) field. This causes a validation error whenever the decorator is applied to a function.

### Code Location
```python
# praxis/backend/core/decorators.py, line 193
func_proto_def = FunctionProtocolDefinitionCreate(
    name=protocol_name,
    version=version,
    description=description,
    top_level=top_level,
    # Missing: fqn=<calculated_fqn>,  # <- This field is required but not provided
    solo_execution=solo_execution,
    # ... other fields
)
```

### Error Message
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for FunctionProtocolDefinitionCreate
fqn
  Field required [type=missing, input_value=..., input_type=dict]
```

### Expected Behavior
The decorator should calculate and provide the `fqn` field using the `get_callable_fqn()` helper function that already exists in the module.

### Recommended Fix
```python
func_proto_def = FunctionProtocolDefinitionCreate(
    name=protocol_name,
    version=version,
    description=description,
    fqn=get_callable_fqn(func),  # Add this line
    top_level=top_level,
    solo_execution=solo_execution,
    # ... other fields
)
```

### Skipped Tests
1. `test_protocol_function_basic_decoration`
2. `test_protocol_function_with_description`
3. `test_protocol_function_uses_function_name_if_not_provided`
4. `test_protocol_function_with_tags_and_category`
5. `test_protocol_function_with_parameters`
6. `test_protocol_function_solo_execution`
7. `test_create_protocol_definition_basic`
8. `test_create_protocol_definition_with_name`
9. `test_create_protocol_definition_with_parameters`
10. `test_decorated_function_retains_original_attributes`
11. `test_decorated_function_has_runtime_info`
12. `test_multiple_decorations_work_independently`

---

## Bug 2: Field Name Mismatch in AcquireAsset Model Access

**Severity:** MEDIUM
**Module:** `praxis/backend/core/asset_manager.py`
**Line:** 509
**Tests Affected:** 2 skipped tests in `tests/core/test_asset_manager.py`

### Description
The code attempts to access `user_choice_instance_accession_id` field on an `AcquireAsset` object, but the Pydantic model defines this field as `instance_accession_id` (without the `user_choice_` prefix).

### Code Location
```python
# praxis/backend/core/asset_manager.py, line 509
if acquire_asset.user_choice_instance_accession_id is not None:
    # Code accesses the wrong field name
```

### Error Message
```
AttributeError: 'AcquireAsset' object has no attribute 'user_choice_instance_accession_id'.
Did you mean: 'instance_accession_id'?
```

### Expected Behavior
The code should access the correct field name `instance_accession_id` as defined in the Pydantic model.

### Recommended Fix
Option 1 - Fix the code:
```python
# Line 509
if acquire_asset.instance_accession_id is not None:
```

Option 2 - Fix the model (if the code is correct):
```python
# Add user_choice_instance_accession_id to the AcquireAsset Pydantic model
```

**Note:** Need to verify which is correct by checking the API contract and model definition in `praxis/backend/models/pydantic_internals/asset.py`.

### Skipped Tests
1. `test_acquire_resource_success`
2. `test_acquire_resource_not_found`

---

## Bug 3: Using `json.load()` Instead of `json.loads()` on String

**Severity:** LOW
**Module:** `praxis/backend/core/protocol_execution_service.py`
**Line:** 183
**Tests Affected:** 1 skipped test in `tests/core/test_protocol_execution_service.py`

### Description
The code uses `json.load()` (which expects a file-like object with a `read()` method) on a string value (`protocol_run_orm.output_data_json`) instead of using `json.loads()` (which parses a JSON string).

### Code Location
```python
# praxis/backend/core/protocol_execution_service.py, line 183
if protocol_run_orm.output_data_json:
    try:
        status_info["output_data"] = json.load(protocol_run_orm.output_data_json)  # Wrong
```

### Error Message
```
AttributeError: 'str' object has no attribute 'read'
```

### Expected Behavior
The code should parse the JSON string using `json.loads()`.

### Recommended Fix
```python
# Line 183
if protocol_run_orm.output_data_json:
    try:
        status_info["output_data"] = json.loads(protocol_run_orm.output_data_json)  # Use loads()
    except json.JSONDecodeError:
        status_info["output_data_raw"] = protocol_run_orm.output_data_json
```

### Skipped Tests
1. `test_get_protocol_run_status_with_output_data`

---

## Complex Service Integration Issues

**Category:** Test Infrastructure
**Module:** `praxis/backend/core/orchestrator.py`
**Tests Affected:** 3 skipped tests in `tests/core/test_orchestrator.py`

### Description
Some orchestrator methods rely on deeply integrated service patterns (e.g., `svc.update_protocol_run_status`, `svc.read_protocol_definition_by_name`) that are difficult to mock in unit tests. These are not bugs in the production code but rather indicate areas that require integration testing instead of unit testing.

### Skipped Tests
1. `test_handle_pre_execution_checks_cancel_command`
2. `test_get_protocol_definition_orm_from_db`
3. `test_handle_protocol_execution_error`

### Recommendation
Create integration tests for these scenarios that use actual database sessions and service instances rather than mocks.

---

## Testing Summary by Module

| Module | Total Tests | Passing | Skipped | Coverage |
|--------|-------------|---------|---------|----------|
| asset_lock_manager.py | 18 | 18 | 0 | 100% |
| celery.py | 17 | 17 | 0 | 100% |
| celery_base.py | 14 | 14 | 0 | 75% |
| celery_tasks.py | 16 | 16 | 0 | 53% |
| container.py | 50 | 50 | 0 | 100% |
| filesystem.py | 27 | 27 | 0 | 92% |
| decorators.py | 27 | 15 | 12 | 42% |
| protocol_code_manager.py | 34 | 34 | 0 | 92% |
| asset_manager.py | 26 | 24 | 2 | 50% |
| protocol_execution_service.py | 14 | 13 | 1 | 95% |
| orchestrator.py | 17 | 14 | 3 | 30% |
| workcell_runtime.py | 20 | 20 | 0 | 30% |
| scheduler.py | 65 | 65 | 0 | 68% |
| run_context.py | 7 | 7 | 0 | 96% |
| workcell.py | 42 | 42 | 0 | 98% |

**Overall:** 394 tests, 376 passing, 18 skipped, 54% coverage

---

## Priority and Impact

### High Priority
- **Bug 1** (decorators.py): Blocks all protocol function decoration. Must fix before any protocols can be registered via decorators.

### Medium Priority
- **Bug 2** (asset_manager.py): Affects resource acquisition with user-specified instances. Impacts protocol execution when users want to specify specific resource instances.

### Low Priority
- **Bug 3** (protocol_execution_service.py): Only affects status retrieval for completed protocol runs with output data. Workaround: Output data raw string is still accessible.

---

## Next Steps

1. **Fix Bug 1** - Add `fqn` field to FunctionProtocolDefinitionCreate instantiation
2. **Verify and fix Bug 2** - Check model definition to determine correct field name
3. **Fix Bug 3** - Change `json.load()` to `json.loads()`
4. **Re-run tests** - After fixes, re-run skipped tests to verify they pass
5. **Integration tests** - Create integration test suite for orchestrator scenarios

---

**Generated:** 2025-11-20
**Test Suite:** pylabpraxis core module tests
**Branch:** claude/complete-api-tests-01UHqTPszHbsTECv3Rnjsn6K
