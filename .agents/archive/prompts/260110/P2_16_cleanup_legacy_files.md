# Agent Prompt: Remove Legacy Model Files and Update Documentation

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 7.1 — Cleanup: Remove Legacy Files
**Parallelizable:** ❌ Sequential — Requires all Phase 2-6 complete

---

## 1. The Task

Remove deprecated ORM and Pydantic model files that have been replaced by unified SQLModel domain models. Update documentation to reflect the new model architecture.

**User Value:** Clean codebase with single source of truth; up-to-date documentation for contributors.

---

## 2. Technical Implementation Strategy

### Files to Delete

**Legacy ORM** (`praxis/backend/models/orm/`):
- `asset.py` → replaced by `domain/asset.py`
- `machine.py` → replaced by `domain/machine.py`
- `resource.py` → replaced by `domain/resource.py`
- `deck.py` → replaced by `domain/deck.py`
- `protocol.py` → replaced by `domain/protocol.py` + `domain/protocol_source.py`
- `schedule.py` → replaced by `domain/schedule.py`
- `outputs.py` → replaced by `domain/outputs.py`
- `workcell.py` → replaced by `domain/workcell.py`
- `user.py` → replaced by `domain/user.py`

**Legacy Pydantic** (`praxis/backend/models/pydantic_internals/`):
- `asset.py`
- `machine.py`
- `resource.py`
- `deck.py`
- `protocol.py`
- `scheduler.py`
- `outputs.py`
- `workcell.py`
- `user.py`
- `pydantic_base.py` → base merged into `domain/sqlmodel_base.py`

**Keep** (not replaced):
- `praxis/backend/models/enums/` — Enums still needed
- `praxis/backend/models/pydantic_internals/filters.py` — Query parameter models
- `praxis/backend/models/pydantic_internals/runtime.py` — Runtime-only models
- `praxis/backend/models/orm/types.py` — Type helpers (if still used)

### Pre-Deletion Verification

Before deleting any file, verify no remaining imports:
```bash
grep -r "from praxis.backend.models.orm.asset import" .
grep -r "from praxis.backend.models.pydantic_internals.asset import" .
```

### Documentation Updates

1. **CONTRIBUTING.md** — Update model creation workflow
2. **docs/architecture/** — Update model architecture diagrams
3. **docs/development/** — Update development guides

---

## 3. Context & References

**Files to Delete:**

| Path | Replaced By |
|:-----|:------------|
| `praxis/backend/models/orm/asset.py` | `domain/asset.py` |
| `praxis/backend/models/orm/machine.py` | `domain/machine.py` |
| `praxis/backend/models/orm/resource.py` | `domain/resource.py` |
| `praxis/backend/models/orm/deck.py` | `domain/deck.py` |
| `praxis/backend/models/orm/protocol.py` | `domain/protocol.py`, `domain/protocol_source.py` |
| `praxis/backend/models/orm/schedule.py` | `domain/schedule.py` |
| `praxis/backend/models/orm/outputs.py` | `domain/outputs.py` |
| `praxis/backend/models/orm/workcell.py` | `domain/workcell.py` |
| `praxis/backend/models/orm/user.py` | `domain/user.py` |
| `praxis/backend/models/pydantic_internals/*.py` | Corresponding domain modules |

**Documentation to Update:**

| Path | Description |
|:-----|:------------|
| `CONTRIBUTING.md` | Model creation workflow |
| `docs/architecture/` | System architecture docs |
| `docs/development/` | Development guides |
| `.agents/backlog/sqlmodel_codegen_refactor.md` | Mark complete |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands.
- **Backup**: Consider git branch before deletion
- **Incremental deletion**: Delete one module at a time, verify tests pass

### Sharp Bits / Technical Debt

1. **Hidden imports**: Some files may have dynamic imports not caught by grep
2. **Type stubs**: Some .pyi files may reference old models
3. **IDE caching**: IDEs may cache old imports; restart after deletion

---

## 5. Verification Plan

**Definition of Done:**

1. No remaining imports of legacy files:
   ```bash
   grep -r "from praxis.backend.models.orm" praxis/
   grep -r "from praxis.backend.models.pydantic_internals" praxis/
   # Should only find imports from enums/, filters.py, runtime.py
   ```

2. Full test suite passes:
   ```bash
   uv run pytest tests/ -v
   ```

3. Application starts:
   ```bash
   uv run uvicorn praxis.backend.main:app --host 0.0.0.0 --port 8000
   # Should start without import errors
   ```

4. Documentation is updated:
   ```bash
   grep -r "ORM.*Pydantic.*separate" docs/
   # Should not find references to old dual-model pattern
   ```

---

## 6. Implementation Steps

1. **Create backup branch**:
   ```bash
   git checkout -b backup/pre-legacy-cleanup
   git checkout -
   ```

2. **Verify no imports** for each legacy file:
   ```bash
   # Example for asset
   grep -r "from praxis.backend.models.orm.asset" .
   grep -r "from praxis.backend.models.pydantic_internals.asset" .
   ```

3. **Delete legacy ORM files** one at a time:
   ```bash
   rm praxis/backend/models/orm/asset.py
   uv run pytest tests/ -x -q
   # If tests pass, continue to next file
   ```

4. **Update orm/__init__.py**:
   - Remove exports of deleted classes
   - Add re-exports from domain/ if needed for backward compatibility

5. **Delete legacy Pydantic files** one at a time:
   - Same pattern as ORM

6. **Update pydantic_internals/__init__.py**:
   - Remove exports of deleted classes

7. **Clean up empty directories** if any

8. **Update CONTRIBUTING.md**:
   - Document new model creation process with SQLModel
   - Remove references to separate ORM/Pydantic

9. **Update architecture docs**:
   - Update diagrams showing unified model structure
   - Document SQLModel patterns

10. **Run full verification**:
    ```bash
    uv run pytest tests/ -v
    uv run ruff check .
    uv run mypy praxis/backend/
    ```

---

## 7. Deletion Checklist

| File | Import Check | Deleted | Tests Pass |
|:-----|:-------------|:--------|:-----------|
| `orm/asset.py` | ⬜ | ⬜ | ⬜ |
| `orm/machine.py` | ⬜ | ⬜ | ⬜ |
| `orm/resource.py` | ⬜ | ⬜ | ⬜ |
| `orm/deck.py` | ⬜ | ⬜ | ⬜ |
| `orm/protocol.py` | ⬜ | ⬜ | ⬜ |
| `orm/schedule.py` | ⬜ | ⬜ | ⬜ |
| `orm/outputs.py` | ⬜ | ⬜ | ⬜ |
| `orm/workcell.py` | ⬜ | ⬜ | ⬜ |
| `orm/user.py` | ⬜ | ⬜ | ⬜ |
| `pydantic_internals/asset.py` | ⬜ | ⬜ | ⬜ |
| `pydantic_internals/machine.py` | ⬜ | ⬜ | ⬜ |
| `pydantic_internals/resource.py` | ⬜ | ⬜ | ⬜ |
| `pydantic_internals/deck.py` | ⬜ | ⬜ | ⬜ |
| `pydantic_internals/protocol.py` | ⬜ | ⬜ | ⬜ |
| `pydantic_internals/scheduler.py` | ⬜ | ⬜ | ⬜ |
| `pydantic_internals/outputs.py` | ⬜ | ⬜ | ⬜ |
| `pydantic_internals/workcell.py` | ⬜ | ⬜ | ⬜ |
| `pydantic_internals/user.py` | ⬜ | ⬜ | ⬜ |
| `pydantic_internals/pydantic_base.py` | ⬜ | ⬜ | ⬜ |

---

## On Completion

- [ ] Commit changes with message: `chore: remove legacy ORM and Pydantic model files`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 7.1 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
