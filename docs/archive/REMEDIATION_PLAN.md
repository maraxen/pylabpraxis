# Code Quality Remediation Plan

## Baseline Assessment

A baseline assessment was conducted on the codebase using `ruff` and `pyright`.

### Summary
- **Ruff (Linting)**: Initial check showed ~62,000 issues.
  - Reducing scope by excluding tests dropped this to ~5,800.
  - Remaining issues are primarily docstring missing (`D100`), import sorting (`I001`), and specific code style checks.
- **Pyright (Type Checking)**: 181 errors reported.
  - Key issues involve generic variance, abstract class instantiation, and attribute access.
- **Mypy (Legacy)**: Found and removed legacy configuration.

## Executed Remediation

### 1. Configuration Consolidation
-   Migrated `ruff` settings from `ruff.toml` to `pyproject.toml`.
-   Migrated `pyright` settings from `pyrightconfig.json` to `pyproject.toml`.
-   Deleted `ruff.toml`, `pyrightconfig.json`, and `mypy.ini`.
-   Removed `mypy` from `Makefile` and dependencies.
-   **Outcome**: Centralized configuration in `pyproject.toml`.

### 2. Ruff Auto-fixes
-   Ran `ruff format .` on the codebase.
-   Ran `ruff check --fix` on `praxis/backend` directories (`api`, `services`, `models`, `core`, `utils`) and root files.
-   **Excluded Tests**: Configured `ruff` to exclude `tests/` directory to focus on production code and reduce noise (e.g., assertions).

### 3. Verification
-   `pyright` runs successfully with configuration in `pyproject.toml`.
-   `ruff` clean check shows significant reduction in issues (from 62k to <6k).

### 4. High-Priority Type Safety Fixes (Phase 2)
Addressed key type safety issues that were blocking or high-risk.
-   **Generic Variance in `CRUDBase`**: Fixed in `praxis/backend/services/deck_type_definition.py` by correctly specifying the `UpdateSchemaType`.
-   **Abstract Class Instantiation**: Fixed in `praxis/backend/api/global_dependencies.py` and `praxis/backend/core/asset_lock_manager.py` by fully implementing `AssetLockManager` and correctly injecting dependencies.
-   **Attribute Access**: Fixed in `praxis/backend/configure.py` by adding `@property` decorator.
-   **Outcome**: Resolved critical type errors and instantiation bugs preventing proper application startup and testing.

### 5. Test Coverage & Stability Improvements (Phase 3)
Focused on fixing critical test failures and increasing coverage for core services.
- **Test Stability**: Fixed `UniqueViolationError` handling in `tests/services/test_user_service.py` and `tests/services/test_resource_service.py` by catching `asyncpg.exceptions.UniqueViolationError`. This resolved flaky failures caused by inconsistent exception wrapping.
- **ORM Constraints**: Addressed `CircularDependencyError` in `DeckOrm` by adding `ondelete="CASCADE"` and `passive_deletes=True`. Note: The associated test remains marked as `xfail` as a full fix requires architectural changes, but the configuration is now correct for cascade deletes.
- **Workcell Coverage**: Increased `WorkcellService` coverage to 100% by adding tests for exception handling in `read_workcell_state`.
- **Machine Service Fixes**:
    -   Fixed `sqlalchemy.exc.MissingGreenlet` errors by eagerly loading `resource_counterpart` during create and update.
    -   Fixed `MachineService.update` logic which previously failed to trigger resource counterpart creation/linking.
    -   Fixed `praxis/backend/services/entity_linking.py` to correctly generate unique `accession_id`s and suffixed names (e.g., `_resource`) for counterparts, preventing Primary Key and Unique Constraint violations in the `assets` table.
- **Outcome**: `test_user_service.py`, `test_resource_service.py`, `test_workcell_service.py`, and `test_machine_service.py` are fully passing.

## Remaining Strategy

### Category 2: Remaining Lint Issues
~5,800 issues remain.
-   **Docstrings**: Many `D100` (missing module docstring) and `D` series errors.
-   **Imports**: `PLC0415` (import outside top-level) requires manual refactoring if circular imports are the cause.
-   **Action**: Address these incrementally during feature development.

### Category 3: Type Safety Fixes
Remaining type errors (reduced from 181).
-   **Focus**: Remaining errors involve method overrides, optional parameter mismatches, and potential attribute access issues in other modules.
-   **Action**: Address remaining type errors incrementally.

### 6. Type Definition Services Coverage (Phase 4)
Addressed 0% coverage in Type Definition services and Discovery service.
- **DeckTypeDefinitionService**: Fixed bug where positions were not persisted due to missing `position_accession_id` mapping and Pydantic model mismatch. Added full CRUD tests (100% coverage).
- **ResourceTypeDefinitionService**: Added tests for CRUD and helper methods.
- **MachineTypeDefinitionService**: Fixed Pydantic/ORM mismatch (`nominal_volume_ul`, `has_deck` fields). Added sync tests.
- **ProtocolDefinitionService**: Added full CRUD tests.
- **DiscoveryService**: Fixed bug where inferred protocol definitions missed `fqn`. Added logic and integration tests.
- **StateService**: Added unit tests for Redis state management (100% coverage).

### 7. Type Safety Improvements (Phase 5)
Addressed ~33 high-priority type errors (errors reduced to ~67).
- **StateSyncMixin**: Added type hints for expected attributes to fix `reportAttributeAccessIssue`.
- **ResourceOrm**: Fixed `is_machine` property to use valid relationship attribute.
- **WellDataOutputCRUDService**: Fixed `rowcount` access on `Result` object using cast.
- **Redis Lock**: Fixed potential `AttributeError` and typing issues in `redis_lock.py`.
- **Accession Resolver**: Fixed invalid access to `id` attribute (changed to `accession_id`).
- **Update Models**: Refactored `FunctionProtocolDefinitionUpdate`, `FunctionDataOutputUpdate`, and `WellDataOutputUpdate` to inherit from `BaseModel` instead of `PraxisBaseModel`, resolving field override conflicts.
- **Pydantic Models**: Updated optional fields to use `default=None` for better static analysis compatibility.
