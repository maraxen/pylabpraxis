# Prompt Batch 260112 - SQLModel Test Migration

**Created**: 2026-01-12
**Status**: 🟡 In Progress
**Total Prompts**: 6

---

## Overview

Complete the SQLModel migration by:
1. **Consolidating test_orm + test_pydantic** into unified `test_domain/` (P1-P2)
2. **Fixing remaining import errors** in services, core, and conftest (P3-P5)

This eliminates the artificial split between ORM and Pydantic tests, reflecting the unified SQLModel architecture.

---

## Current Status

| Layer | Status |
|-------|--------|
| `tests/models/test_orm/` | 12 broken, 7 working (63 tests collected) |
| `tests/models/test_pydantic/` | 4 broken, 3 working (39 tests collected) |
| `tests/services/` | 10 files with import errors |
| `tests/core/` | 12 files with import errors |
| `tests/conftest.py` & misc | 4 files with import errors |
| **Total Error Collection** | 42 files, ~102 tests collected |

---

## Migration Pattern

### Import Transformations
```python
# OLD: pydantic_internals
from praxis.backend.models.pydantic_internals.X import XCreate, XUpdate
# NEW: domain
from praxis.backend.models.domain.X import XCreate, XUpdate

# OLD: orm module
from praxis.backend.models.orm.X import XOrm
# NEW: domain (drop Orm suffix)
from praxis.backend.models.domain.X import X
```

### Code Transformations
- Replace all `XOrm` class references with `X` throughout file
- Update type hints: `XOrm` → `X`

---

## Prompts

| # | File | Task | Status |
|---|------|------|--------|
| 1 | [P1_test_orm_migration.md](./P1_test_orm_migration.md) | Fix 12 broken test_orm files, rename dir to test_domain | 🔴 Not Started |
| 2 | [P2_test_pydantic_migration.md](./P2_test_pydantic_migration.md) | Fix 4 broken test_pydantic files, merge into test_domain, delete dir | 🔴 Not Started |
| 3 | [P3_test_services_migration.md](./P3_test_services_migration.md) | Fix 10 test_services files | 🔴 Not Started |
| 4 | [P4_test_core_migration.md](./P4_test_core_migration.md) | Fix 12 test_core files | 🔴 Not Started |
| 5 | [P5_conftest_migration.md](./P5_conftest_migration.md) | Fix 4 conftest/misc files | 🔴 Not Started |
| 6 | [cleanup_aliases.md](./cleanup_aliases.md) | Delete legacy orm/ and pydantic_internals/ dirs | 🔴 Not Started |

---

## Execution Strategy

### Parallel Groups

**Phase 1 (Parallel):**
- P1 & P2 can run in parallel (independent consolidation)

**Phase 2 (Parallel):**
- P3, P4, P5 can run in parallel (independent file groups)

**Phase 3 (Sequential):**
- P6 runs after all others complete (deletes legacy directories)

### Timeline

```
P1 + P2 (parallel) → P3 + P4 + P5 (parallel) → P6 (cleanup)
```

---

## Reference Files (Already Migrated)

- `tests/models/test_domain/test_asset_sqlmodel.py` - SQLModel pattern
- `tests/models/test_orm/test_machine_orm.py` - Already uses domain imports
- `tests/services/test_machine_service.py` - Clean domain imports

---

## Verification

After all prompts complete:
```bash
# Should show 0 errors
uv run pytest --collect-only 2>&1 | grep "ERROR\|error"

# All tests pass
uv run pytest tests/ -x
```

**Expected Results:**
- `tests/models/test_domain/` contains 100+ unified tests
- `tests/models/test_orm/` directory deleted
- `tests/models/test_pydantic/` directory deleted
- All 42 error collection issues resolved
