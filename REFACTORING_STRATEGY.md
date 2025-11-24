# Core Module Refactoring Strategy

## Overview

Several core modules have grown too large (>700 lines) and would benefit from being split into submodules for better maintainability, testability, and code organization.

## Current State

| Module | Lines | Classes | Status | Priority |
|--------|-------|---------|--------|----------|
| workcell_runtime.py | 1274 | 1 | NEEDS REFACTORING | HIGH |
| orchestrator.py | 963 | 1 | NEEDS REFACTORING | HIGH |
| asset_manager.py | 919 | 1 | COMPLETED | HIGH |
| decorators.py | 735 | 2 | NEEDS REFACTORING | MEDIUM |
| protocol_code_manager.py | 521 | 1 | CONSIDER REFACTORING | LOW |
| scheduler.py | 407 | 1 | OK FOR NOW | - |

---

## 1. workcell_runtime.py (1274 lines) → workcell_runtime/

**Current Structure:**
- Single `WorkcellRuntime` class with 25+ methods
- Helper function: `_get_class_from_fqn()`

**Proposed Structure:**
```
praxis/backend/core/workcell_runtime/
├── __init__.py                    # Re-export WorkcellRuntime
├── core.py                        # Main WorkcellRuntime class skeleton
├── state_sync.py                  # State synchronization methods
├── machine_manager.py             # Machine lifecycle management
├── resource_manager.py            # Resource lifecycle management
├── deck_manager.py                # Deck state and positioning
└── utils.py                       # Helper functions (_get_class_from_fqn)
```

**Method Distribution:**

### core.py (Base class)
- `__init__()` - Initialization and dependency injection
- Class attributes and properties
- `get_main_workcell()` - Main accessor

### state_sync.py
- `_link_workcell_to_db()` - Database linking
- `_continuous_state_sync_loop()` - Background sync loop
- `start_workcell_state_sync()` - Start sync task
- `stop_workcell_state_sync()` - Stop sync task
- `get_state_snapshot()` - Get current state
- `apply_state_snapshot()` - Apply saved state

### machine_manager.py
- `initialize_machine()` - Create and register machine
- `get_active_machine()` - Get machine by ID
- `get_active_machine_accession_id()` - Get ID for machine
- `shutdown_machine()` - Shutdown single machine
- `shutdown_all_machines()` - Shutdown all machines
- `execute_machine_action()` - Execute machine commands

### resource_manager.py
- `create_or_get_resource()` - Resource creation/retrieval
- `get_active_resource()` - Get resource by ID
- `get_active_resource_accession_id()` - Get ID for resource
- `clear_resource()` - Remove resource

### deck_manager.py
- `get_active_deck()` - Get deck by ID
- `get_active_deck_accession_id()` - Get ID for deck
- `get_last_initialized_deck_object()` - Get last deck
- `get_deck_state_representation()` - Get deck state
- `assign_resource_to_deck()` - Place resource on deck
- `clear_deck_position()` - Remove resource from position
- `_get_calculated_location()` - Calculate position

**Benefits:**
- Each file ~200-250 lines
- Clear separation of concerns
- Easier to test individual managers
- Can use mixins for composition

---

## 2. orchestrator.py (963 lines) → orchestrator/

**Current Structure:**
- Single `Orchestrator` class with 15 methods

**Proposed Structure:**
```
praxis/backend/core/orchestrator/
├── __init__.py                    # Re-export Orchestrator
├── core.py                        # Main Orchestrator class
├── protocol_preparation.py        # Protocol code/definition loading
├── asset_acquisition.py           # Asset acquisition logic
├── execution.py                   # Main execution flow
└── error_handling.py              # Error handling and finalization
```

**Method Distribution:**

### core.py
- `__init__()` - Initialization
- Main class structure

### protocol_preparation.py
- `_get_protocol_definition_orm_from_db()` - Load protocol from DB
- `_prepare_protocol_code()` - Load protocol code from git/filesystem
- `_initialize_run_context()` - Create PraxisRunContext
- `_process_input_parameters()` - Validate and process inputs
- `_inject_praxis_state()` - Inject state parameter
- `_prepare_arguments()` - Build final argument dict

### asset_acquisition.py
- `_acquire_assets()` - Acquire all required assets
- `_handle_deck_preconfiguration()` - Deck construction if needed

### execution.py
- `execute_protocol()` - Main execution entry point
- `execute_existing_protocol_run()` - Resume existing run
- `_execute_protocol_main_logic()` - Core execution logic
- `_handle_pre_execution_checks()` - Pre-execution validation

### error_handling.py
- `_handle_protocol_execution_error()` - Error handling
- `_finalize_protocol_run()` - Cleanup and finalization

**Benefits:**
- Each file ~150-200 lines
- Execution flow is clearer
- Easier to add new preparation steps
- Better unit test isolation

---

## 3. asset_manager.py (919 lines) → asset_manager/

**Current Structure:**
- Single `AssetManager` class with 16 methods

**Proposed Structure:**
```
praxis/backend/core/asset_manager/
├── __init__.py                    # Re-export AssetManager
├── core.py                        # Main AssetManager class
├── machine_manager.py             # Machine acquisition/release
├── resource_manager.py            # Resource acquisition/release
├── deck_manager.py                # Deck application
└── location_handler.py            # Location constraint handling
```

**Method Distribution:**

### core.py
- `__init__()` - Initialization
- `acquire_asset()` - Main entry point (routes to machine/resource)
- `lock_asset()` - Asset locking
- `unlock_asset()` - Asset unlocking

### machine_manager.py
- `acquire_machine()` - Machine acquisition
- `release_machine()` - Machine release

### resource_manager.py
- `acquire_resource()` - Resource acquisition
- `_find_resource_to_acquire()` - Find suitable resource
- `_update_resource_acquisition_status()` - Update status
- `release_resource()` - Resource release
- `_is_deck_resource()` - Check if resource is deck type
- `_handle_resource_release_location()` - Handle location on release

### deck_manager.py
- `apply_deck()` - Apply deck configuration
- `_get_and_validate_deck_orms()` - Validate deck setup
- `_process_deck_resource_item()` - Process deck item

### location_handler.py
- `_handle_location_constraints()` - Handle location constraints

**Benefits:**
- Each file ~150-200 lines
- Clear separation between machines and resources
- Deck logic isolated
- Easier to extend with new asset types

---

## 4. decorators.py (735 lines) → decorators/

**Current Structure:**
- 2 dataclasses: `CreateProtocolDefinitionData`, `ProtocolRuntimeInfo`
- Main decorator: `protocol_function()`
- Helper functions: `get_callable_fqn()`, `_create_protocol_definition()`, `_process_parameter()`

**Proposed Structure:**
```
praxis/backend/core/decorators/
├── __init__.py                    # Re-export @protocol_function
├── protocol_decorator.py          # Main @protocol_function decorator
├── definition_builder.py          # _create_protocol_definition logic
├── parameter_processor.py         # Parameter processing
└── models.py                      # Data models and utilities
```

**Distribution:**

### protocol_decorator.py
- `protocol_function()` - Main decorator function
- High-level decorator logic

### definition_builder.py
- `_create_protocol_definition()` - Build protocol definition
- Validation logic

### parameter_processor.py
- `_process_parameter()` - Process individual parameter
- Parameter type handling
- Asset requirement extraction

### models.py
- `CreateProtocolDefinitionData` - Dataclass
- `ProtocolRuntimeInfo` - Dataclass
- `get_callable_fqn()` - Utility function
- Context variable definitions

**Benefits:**
- Each file ~150-200 lines
- Decorator logic separated from parameter processing
- Models isolated for easier testing
- Can extend parameter processing without touching decorator

---

## 5. protocol_code_manager.py (521 lines) - LOW PRIORITY

**Current Structure:**
- Single `ProtocolCodeManager` class
- Context manager: `temporary_sys_path`

**Recommendation:** Consider refactoring if grows beyond 700 lines. Current structure is reasonable.

Potential future structure:
```
praxis/backend/core/protocol_code_manager/
├── __init__.py
├── core.py                        # Main class
├── git_operations.py              # Git-related methods
├── module_loading.py              # Python module loading
└── utils.py                       # Helper functions
```

---

## Implementation Strategy

### Phase 1: High Priority Modules (1-2 weeks)
1. **workcell_runtime** - Highest complexity, most methods
2. **orchestrator** - Core execution logic
3. **asset_manager** - Asset management critical path

### Phase 2: Medium Priority (1 week)
4. **decorators** - Protocol definition system

### Phase 3: Future (As needed)
5. **protocol_code_manager** - Only if grows significantly

---

## Implementation Guidelines

### 1. Backward Compatibility
- Keep original module as re-export for backward compatibility
- Example for workcell_runtime:
```python
# praxis/backend/core/workcell_runtime/__init__.py
from .core import WorkcellRuntime

__all__ = ["WorkcellRuntime"]
```

### 2. Testing Strategy
- Run existing tests first to establish baseline
- Refactor incrementally (one submodule at a time)
- Run tests after each submodule split
- Add new tests for internal helpers if needed

### 3. Import Management
- Use relative imports within submodules
- Keep public API exports in `__init__.py`
- Update container.py if needed

### 4. Code Movement Pattern
```bash
# For each large module:
1. Create new directory: mkdir -p praxis/backend/core/{module_name}/
2. Create __init__.py with re-exports
3. Create submodule files
4. Move methods to appropriate submodules
5. Update imports
6. Run tests
7. Commit incrementally
```

### 5. Common Patterns

**For methods that need to be shared:**
```python
# core.py - Base class with shared state
class WorkcellRuntime:
    def __init__(...):
        # Initialize shared state
        self._machines = {}
        self._resources = {}
```

**Use mixins for logical grouping:**
```python
# machine_manager.py
class MachineManagerMixin:
    async def initialize_machine(self, ...):
        pass

# core.py
from .machine_manager import MachineManagerMixin
from .resource_manager import ResourceManagerMixin

class WorkcellRuntime(MachineManagerMixin, ResourceManagerMixin):
    pass
```

### 6. Detailed Step-by-Step Instructions (Example: asset_manager)

1.  **Preparation**:
    *   Run existing tests to ensure a clean state: `uv run pytest tests/core/test_asset_manager.py`.
    *   Identify dependencies and imports in the original file.

2.  **Structure Creation**:
    *   Create the directory: `mkdir -p praxis/backend/core/asset_manager/`.
    *   Create empty files for the submodules (e.g., `machine_manager.py`, `resource_manager.py`).

3.  **Code Migration (Iterative)**:
    *   **Step 3a**: Move self-contained logic first. For `asset_manager`, `LocationHandlerMixin` was moved to `location_handler.py`.
    *   **Step 3b**: Move larger chunks of logic into Mixins. Ensure to add `TYPE_CHECKING` imports to avoid circular dependencies and provide type hints for the expected `self` attributes (e.g., `self.db`, `self.svc`).
    *   **Step 3c**: Create `core.py` that defines the main class inheriting from these Mixins.

4.  **Re-exporting**:
    *   Create `__init__.py` to export the main class and any other public symbols (exceptions, loggers) that were previously available at the module level.

5.  **Verification**:
    *   Rename the original file (e.g., `asset_manager_OLD.py`) to avoid import conflicts.
    *   Run tests again: `uv run pytest tests/core/test_asset_manager.py`.
    *   If tests pass, delete the old file.

---

## Testing Checklist

After each refactoring:
- [ ] All existing tests pass
- [ ] No import errors
- [ ] Coverage remains the same or improves
- [ ] Linting passes (ruff, mypy)
- [ ] Documentation updated if needed

---

## Benefits of Refactoring

1. **Maintainability**: Easier to find and fix bugs
2. **Testability**: Can test submodules independently
3. **Readability**: Smaller files are easier to understand
4. **Extensibility**: Can add features without bloating single file
5. **Code Review**: Smaller files = easier reviews
6. **Team Collaboration**: Less merge conflicts

---

## Risk Mitigation

1. **Risk**: Breaking existing code
   - **Mitigation**: Incremental refactoring with tests at each step

2. **Risk**: Import errors
   - **Mitigation**: Keep backward-compatible re-exports

3. **Risk**: Performance regression
   - **Mitigation**: Profile before/after if concerned

4. **Risk**: Increased complexity
   - **Mitigation**: Follow clear naming conventions, good documentation

---

## Next Steps

1. Review and approve this strategy
2. Start with **workcell_runtime** (highest priority)
3. Create feature branch for refactoring
4. Implement incrementally with tests
5. Review and merge
6. Repeat for orchestrator, asset_manager, decorators

---

**Estimated Total Effort:** 3-4 weeks for all high-priority modules
**Recommended Approach:** One module at a time, fully tested before moving to next
