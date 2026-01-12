# Agent Prompt: Migrate Conftest and Misc Files

**Status:** 🔴 Not Started
**Priority:** P1
**Batch:** 260112
**Parallel Group:** 5 of 5

---

## 1. The Task

Migrate 4 conftest and miscellaneous test files to use unified SQLModel domain imports.

**Files to Modify:**
```
tests/conftest.py
tests/api/conftest.py
tests/backend/core/test_consumable_assignment.py
tests/test_deck_serialization.py
```

## 2. Migration Pattern

### tests/conftest.py

```python
# BEFORE (around line 287 and 312)
from praxis.backend.models.pydantic_internals.user import UserCreate

# AFTER
from praxis.backend.models.domain.user import UserCreate
```

### tests/api/conftest.py

Check for any `MachineOrm` or other Orm class references causing NameError.

### tests/backend/core/test_consumable_assignment.py

```python
# BEFORE
from praxis.backend.models.pydantic_internals.protocol import (
    # various protocol models
)

# AFTER
from praxis.backend.models.domain.protocol import (
    # various protocol models
)
```

### tests/test_deck_serialization.py

```python
# BEFORE
from praxis.backend.models.pydantic_internals.deck import DeckResponse

# AFTER
from praxis.backend.models.domain.deck import DeckResponse
# OR if DeckResponse is now DeckRead:
from praxis.backend.models.domain.deck import DeckRead
```

## 3. Special Considerations

### Conftest Files Are Critical
- `tests/conftest.py` provides fixtures used by ALL tests
- `tests/api/conftest.py` provides API-specific fixtures
- Errors here cascade to many test files

### Check DeckResponse Naming
The response schema may have been renamed to `DeckRead` following the Create/Update/Read convention. Verify:
```bash
grep -r "DeckResponse\|DeckRead" praxis/backend/models/domain/deck.py
```

### API Conftest MachineOrm Issue
The error `NameError: name 'MachineOrm' is not defined` suggests the import exists but wasn't properly aliased or the usage wasn't updated.

## 4. Constraints

- Use `uv run` for all Python commands
- Changes must be purely mechanical refactors - no logic changes
- These files affect many tests - verify thoroughly

## 5. Verification

```bash
# Test collection for all tests (these files affect everything)
uv run pytest --collect-only 2>&1 | head -50

# Specific file verification
uv run pytest tests/conftest.py tests/api/conftest.py --collect-only
uv run pytest tests/backend/core/test_consumable_assignment.py --collect-only
uv run pytest tests/test_deck_serialization.py --collect-only
```

**Definition of Done:**
1. All 4 files import from `praxis.backend.models.domain`
2. No imports from `pydantic_internals` or `orm`
3. No `Orm` suffix in any class reference
4. `uv run pytest --collect-only` shows fewer than 10 errors (other prompts may not be complete)
5. The specific 4 files don't cause collection errors

---

## On Completion

- [ ] Mark this prompt complete in README.md
- [ ] Report any issues encountered
