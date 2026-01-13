# Agent Prompt: Merge test_pydantic into test_domain + Delete

**Status:** 🔴 Not Started
**Priority:** P1
**Batch:** 260112
**Parallel Group:** 2 of 5
**Depends On:** P1 (test_domain directory must exist)

---

## 1. The Task

Fix the 4 broken test files in `tests/models/test_pydantic/`, merge all pydantic tests into the corresponding `test_domain/` files, then delete `test_pydantic/`.

**Current State:**
- 3 files working (39 tests collected)
- 4 files broken with import errors

**Broken Files:**
```
tests/models/test_pydantic/test_resource_definition_pydantic.py
tests/models/test_pydantic/test_resource_pydantic.py
tests/models/test_pydantic/test_user_pydantic.py
tests/models/test_pydantic/test_workcell_pydantic.py
```

**Working Files:**
```
tests/models/test_pydantic/test_deck_pydantic.py
tests/models/test_pydantic/test_machine_definition_pydantic.py
tests/models/test_pydantic/test_machine_pydantic.py
```

## 2. Migration Strategy

### Option A: Append to Existing test_domain Files (Recommended)
Merge pydantic validation tests into the corresponding test_domain file:
- `test_machine_pydantic.py` → append tests to `test_domain/test_machine.py`
- `test_resource_pydantic.py` → append tests to `test_domain/test_resource.py`
- etc.

### Option B: Keep Separate Files with New Names
Rename and move:
- `test_machine_pydantic.py` → `test_domain/test_machine_schemas.py`

**Recommended: Option A** - SQLModel unifies ORM and Pydantic, so tests should be unified too.

## 3. Steps

### Step 1: Fix Broken Files First

```python
# BEFORE
from praxis.backend.models.pydantic_internals.user import (
    UserCreate,
    UserUpdate,
    UserBase,
)

# AFTER
from praxis.backend.models.domain.user import (
    UserCreate,
    UserUpdate,
    UserBase,
)
```

### Step 2: Merge Each Pydantic Test File

For each `test_*_pydantic.py`:
1. Open the corresponding `test_domain/test_*.py`
2. Copy the test classes/functions from pydantic file
3. Add them to the domain file under a clear section header
4. Update any duplicate fixture names if needed

Example merge pattern:
```python
# In test_domain/test_machine.py, add at the end:

# =============================================================================
# Schema Validation Tests (merged from test_machine_pydantic.py)
# =============================================================================

class TestMachineSchemas:
    """Tests for Machine Pydantic schemas."""

    def test_machine_base_minimal(self) -> None:
        # ... copied from test_machine_pydantic.py
```

### Step 3: Delete test_pydantic Directory

```bash
# After all tests pass
rm -rf tests/models/test_pydantic/
```

## 4. Merge Mapping

| Pydantic File | Target Domain File |
|---------------|-------------------|
| `test_machine_pydantic.py` | `test_domain/test_machine.py` |
| `test_machine_definition_pydantic.py` | `test_domain/test_machine_definition.py` |
| `test_deck_pydantic.py` | `test_domain/test_deck.py` |
| `test_resource_pydantic.py` | `test_domain/test_resource.py` |
| `test_resource_definition_pydantic.py` | `test_domain/test_resource_definition.py` |
| `test_user_pydantic.py` | `test_domain/test_user.py` |
| `test_workcell_pydantic.py` | `test_domain/test_workcell.py` |

## 5. Constraints

- Use `uv run` for all Python commands
- Preserve all test functionality
- Remove duplicate imports when merging
- Keep test isolation (each test should be independent)

## 6. Verification

```bash
# After merging (before delete)
uv run pytest tests/models/test_domain/ --collect-only
# Verify test count increased (63 + 39 = ~102 tests)

# After delete
uv run pytest tests/models/test_domain/ -v
# All tests pass
```

**Definition of Done:**
1. All 4 broken files fixed
2. All 7 pydantic test files merged into test_domain
3. `tests/models/test_pydantic/` directory deleted
4. All tests pass in `test_domain/`
5. Total test count preserved (~102 tests)

---

## On Completion

- [ ] Mark this prompt complete in README.md
- [ ] Update any imports in other files that referenced test_pydantic
