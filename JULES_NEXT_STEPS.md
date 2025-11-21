# Jules - Next Steps and Work Bundles

## 📋 Future Work Bundles (Based on Coverage Analysis)

Based on the verification of the test environment and initial coverage run (35% on services), the following work bundles are prioritized:

### Bundle A: Fix Critical Dependencies and User Service Tests
**Priority: CRITICAL**
- **Context**: `passlib` with `bcrypt` is throwing `ValueError: password cannot be longer than 72 bytes` and `AttributeError`. This blocks all authentication-related tests.
- **Files**: `pyproject.toml` (dependency management), `tests/services/test_user_service.py`.
- **Tasks**:
  1. Investigate `passlib` / `bcrypt` version incompatibility.
  2. Fix the dependency or implementation in `praxis/backend/services/user.py`.
  3. Verify all 18 failing tests in `test_user_service.py` pass.

### Bundle B: Fix Failing Integration Tests in Services
**Priority: HIGH**
- **Context**: Several service tests are failing due to logic or setup issues.
- **Files**:
  - `tests/services/test_deck_service.py` (1 failure)
  - `tests/services/test_protocol_run_service.py` (1 failure)
  - `tests/services/test_resource_service.py` (4 failures)
- **Tasks**:
  1. Debug and fix `test_create_deck_remaps_machine_id`.
  2. Debug and fix `test_log_function_call_with_parent`.
  3. Debug and fix `ResourceService` update and relationship tests.

### Bundle C: Increase Coverage for Core Domain Services
**Priority: MEDIUM**
- **Context**: Core domain services have low test coverage, leaving business logic exposed.
- **Files**:
  - `praxis/backend/services/workcell.py` (Current: 32%)
  - `praxis/backend/services/machine.py` (Current: 24%)
  - `praxis/backend/services/deck.py` (Current: 44%)
- **Tasks**:
  1. Create/Expand `tests/services/test_workcell_service.py` to cover `WorkcellService` methods.
  2. Create/Expand `tests/services/test_machine_service.py`.
  3. Expand `tests/services/test_deck_service.py`.
  4. Goal: Achieve >80% coverage for these files.
