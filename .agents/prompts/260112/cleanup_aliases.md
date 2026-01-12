# Agent Prompt: Cleanup Model Aliases & Directories

Examine `.agents/README.md` for development context.

**Status:** 🔴 Not Started
**Priority:** P2
**Batch:** 260112
**Sequence:** Run AFTER P1-P5 test migration prompts complete
**Backlog Reference:** Refactor Backlog

---

## Prerequisites

This prompt should only be executed after all test migration prompts (P1-P5) are complete:
- P1: tests/models/test_orm migration
- P2: tests/models/test_pydantic migration
- P3: tests/services migration
- P4: tests/core migration
- P5: conftest and misc migration

Verify with:
```bash
uv run pytest --collect-only 2>&1 | grep -c "ERROR"
# Should be 0 or very few errors
```

---

## 1. The Task

Refactor the backend to remove temporary backward-compatibility aliases created during the Unified Model migration. Specifically, eliminate the `praxis/backend/models/orm/` and `praxis/backend/models/pydantic_internals/` directories and update all import paths to point directly to `praxis/backend/models/domain/`.

**Value:** Reduces technical debt, simplifies the codebase, and prevents confusion between "ORM" and "Domain" models.

## 2. Technical Implementation Strategy

**Objective:**
Systematically replace all imports of `praxis.backend.models.orm.*` and `praxis.backend.models.pydantic_internals.*` with their counterparts in `praxis.backend.models.domain.*` (or `enums.*`).

**Steps:**

1. **Analyze Aliases:** Map every alias in `orm/__init__.py` and the stub files (`orm/asset.py`, `orm/resolution.py`, etc.) to its true Domain target.
2. **Search & Replace:** Use `grep` or `ripgrep` to find usages of the `orm` paths.
    - Example: Replace `from praxis.backend.models.orm import MachineOrm` with `from praxis.backend.models.domain import Machine`.
    - Example: Replace `from praxis.backend.models.orm.resolution import StateResolutionLogOrm` with `from praxis.backend.models.domain.resolution import StateResolutionLog`.
3. **Delete Directories:** Once all references are removed, delete the `orm/` and `pydantic_internals/` directories entirely.
4. **Fix Init:** Update `praxis/backend/models/__init__.py` to remove any remaining legacy exports.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/orm/*` | Directory to be deleted. |
| `praxis/backend/models/pydantic_internals/*` | Directory to be deleted. |
| `praxis/backend/**/*.py` | All backend files potentially importing these models. |

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python.
- **Verification**: Changes must be purely refactors. Logic must remain identical.

## 5. Verification Plan

**Definition of Done:**

1. The `praxis/backend/models/orm/` directory does not exist.
2. The `praxis/backend/models/pydantic_internals/` directory does not exist.
3. The code compiles without `ImportError`.
4. The full test suite passes:

    ```bash
    uv run pytest tests/
    ```

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete
