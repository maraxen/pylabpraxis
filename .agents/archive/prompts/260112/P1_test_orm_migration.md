# Agent Prompt: Fix test_orm + Rename to test_domain

**Status:** 🔴 Not Started
**Priority:** P1
**Batch:** 260112
**Parallel Group:** 1 of 5

---

## 1. The Task

Fix the 12 broken test files in `tests/models/test_orm/`, then rename the directory to `tests/models/test_domain/` to reflect the unified SQLModel architecture.

**Current State:**

- 7 files working (63 tests collected)
- 12 files broken with import errors

**Broken Files to Fix:**

```
tests/models/test_orm/test_asset_requirement_orm.py
tests/models/test_orm/test_asset_reservation_orm.py
tests/models/test_orm/test_deck_orm.py
tests/models/test_orm/test_file_system_protocol_source_orm.py
tests/models/test_orm/test_function_call_log_orm.py
tests/models/test_orm/test_function_data_output_orm.py
tests/models/test_orm/test_function_protocol_definition_orm.py
tests/models/test_orm/test_parameter_definition_orm.py
tests/models/test_orm/test_protocol_source_repository_orm.py
tests/models/test_orm/test_schedule_entry_orm.py
tests/models/test_orm/test_schedule_history_orm.py (has SyntaxError too)
tests/models/test_orm/test_well_data_output_orm.py
```

## 2. Migration Steps

### Step 1: Fix Import Errors

```python
# BEFORE
from praxis.backend.models.orm.protocol import (
    ProtocolRunOrm,
    FunctionProtocolDefinitionOrm,
    AssetRequirementOrm,
)
from praxis.backend.models.orm.asset import AssetOrm

# AFTER
from praxis.backend.models.domain.protocol import (
    ProtocolRun,
    FunctionProtocolDefinition,
    AssetRequirement,
)
from praxis.backend.models.domain.asset import Asset
```

### Step 2: Replace XOrm → X Throughout

| Old Name | New Name |
|----------|----------|
| `ProtocolRunOrm` | `ProtocolRun` |
| `FunctionProtocolDefinitionOrm` | `FunctionProtocolDefinition` |
| `AssetRequirementOrm` | `AssetRequirement` |
| `AssetReservationOrm` | `AssetReservation` |
| `DeckOrm` | `Deck` |
| `DeckDefinitionOrm` | `DeckDefinition` |
| `FileSystemProtocolSourceOrm` | `FileSystemProtocolSource` |
| `FunctionCallLogOrm` | `FunctionCallLog` |
| `FunctionDataOutputOrm` | `FunctionDataOutput` |
| `ParameterDefinitionOrm` | `ParameterDefinition` |
| `ProtocolSourceRepositoryOrm` | `ProtocolSourceRepository` |
| `ScheduleEntryOrm` | `ScheduleEntry` |
| `ScheduleHistoryOrm` | `ScheduleHistory` |
| `WellDataOutputOrm` | `WellDataOutput` |
| `MachineOrm` | `Machine` |
| `ResourceOrm` | `Resource` |
| `WorkcellOrm` | `Workcell` |
| `UserOrm` | `User` |

### Step 3: Fix Syntax Error in test_schedule_history_orm.py

Line 27 has a syntax error - missing newline before `from`:

```python
# BROKEN
)from praxis.backend.utils.uuid import uuid7

# FIXED
)
from praxis.backend.utils.uuid import uuid7
```

### Step 4: Rename Directory

```bash
# After all files are fixed and tests pass
git mv tests/models/test_orm tests/models/test_domain
```

### Step 5: Rename Test Files (Optional but Recommended)

Remove `_orm` suffix from filenames to match new structure:

```bash
# Example
git mv tests/models/test_domain/test_machine_orm.py tests/models/test_domain/test_machine.py
```

## 3. Reference

**Already working files (use as pattern):**

- `tests/models/test_orm/test_machine_orm.py` - Clean domain imports
- `tests/models/test_domain/test_asset_sqlmodel.py` - Unified SQLModel test pattern

**Domain exports:**

- `praxis/backend/models/domain/__init__.py`
- `praxis/backend/models/domain/protocol.py`

## 4. Constraints

- Use `uv run` for all Python commands
- Use `git mv` for renames to preserve history
- Changes must be purely mechanical - no logic changes

## 5. Verification

```bash
# After fixing imports (before rename)
uv run pytest tests/models/test_orm/ --collect-only
# Expected: 0 errors

# After rename
uv run pytest tests/models/test_domain/ -v
# Expected: All tests pass
```

**Definition of Done:**

1. All 12 broken files have fixed imports
2. All `Orm` suffixes removed from class references
3. Directory renamed to `test_domain`
4. `uv run pytest tests/models/test_domain/ --collect-only` shows 0 errors
5. All tests pass

---

## On Completion

- [ ] Mark this prompt complete in README.md
- [ ] Report any model names not found in domain (may need to be added)
