# Agent Prompt: Migrate Workcell + User to SQLModel

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 4.2 — Model Migration: Workcell & User
**Parallelizable:** ✅ Can run in parallel with P2_10 after Phase 2

---

## 1. The Task

Unify `Workcell` and `User` models from separate ORM and Pydantic definitions into SQLModel domain models. These are supporting entities for grouping assets and authentication.

**User Value:** Single source of truth for lab organization and user management with automatic API type generation.

---

## 2. Technical Implementation Strategy

### Current Architecture

**ORM**:
- `WorkcellOrm` (`praxis/backend/models/orm/workcell.py`) — Logical grouping of machines
- `UserOrm` (`praxis/backend/models/orm/user.py`) — User authentication and profile

**Key Workcell Relationships:**
```
WorkcellOrm
    └── MachineOrm[] (machines in this workcell)
    └── ResourceOrm[] (resources in this workcell)
```

**Pydantic**:
- `WorkcellBase`, `WorkcellCreate`, `WorkcellResponse`, `WorkcellUpdate`
- `UserOrm` Pydantic schemas (if they exist)

---

## 3. Context & References

**Primary Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/workcell.py` | Unified Workcell SQLModel |
| `praxis/backend/models/domain/user.py` | Unified User SQLModel |

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/__init__.py` | Export Workcell and User models |

**Files to Deprecate (Do NOT delete yet):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/orm/workcell.py` | Legacy ORM |
| `praxis/backend/models/orm/user.py` | Legacy ORM |
| `praxis/backend/models/pydantic_internals/workcell.py` | Legacy Pydantic |
| `praxis/backend/models/pydantic_internals/user.py` | Legacy Pydantic |

**Reference Files (Read-Only):**

| Path | Pattern Source |
|:-----|:---------------|
| `praxis/backend/models/orm/workcell.py` | Full ORM definition |
| `praxis/backend/models/orm/user.py` | Full ORM definition |
| `praxis/backend/models/pydantic_internals/workcell.py` | Pydantic schemas |
| `praxis/backend/models/pydantic_internals/user.py` | Pydantic schemas |
| `praxis/backend/api/workcell.py` | API router |
| `tests/models/test_orm/test_workcell_orm.py` | ORM tests |
| `tests/models/test_orm/test_user_orm.py` | ORM tests |
| `tests/models/test_pydantic/test_workcell_pydantic.py` | Pydantic tests |
| `tests/models/test_pydantic/test_user_pydantic.py` | Pydantic tests |
| `tests/api/test_workcells.py` | API tests |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands.
- **Backend Path**: `praxis/backend`
- **User security**: Do NOT expose password hashes in response schemas
- **Relationships**: Workcell has one-to-many with Machine and Resource

### Sharp Bits / Technical Debt

1. **Password handling**: User model has password hash field - keep out of Read schemas
2. **Relationship direction**: Machine/Resource have FK to Workcell (not vice versa)
3. **Authentication**: User model integrates with Keycloak - may have external ID fields

---

## 5. Verification Plan

**Definition of Done:**

1. Models import successfully:
   ```bash
   uv run python -c "
   from praxis.backend.models.domain.workcell import Workcell, WorkcellCreate, WorkcellRead
   from praxis.backend.models.domain.user import User, UserCreate, UserRead
   print('OK')
   "
   ```

2. Workcell relationship works:
   ```bash
   uv run python -c "
   from sqlmodel import SQLModel, create_engine, Session
   from praxis.backend.models.domain.workcell import Workcell
   from praxis.backend.models.domain.machine import Machine
   
   engine = create_engine('sqlite:///:memory:')
   SQLModel.metadata.create_all(engine)
   
   with Session(engine) as s:
       wc = Workcell(name='Lab A')
       m = Machine(name='handler_1', fqn='handlers.Test', workcell=wc)
       s.add_all([wc, m])
       s.commit()
       print(f'Workcell {wc.name} with machines')
   "
   ```

3. Existing tests still pass:
   ```bash
   uv run pytest tests/models/test_orm/test_workcell_orm.py tests/models/test_orm/test_user_orm.py -x -q
   uv run pytest tests/models/test_pydantic/test_workcell_pydantic.py tests/models/test_pydantic/test_user_pydantic.py -x -q
   uv run pytest tests/api/test_workcells.py -x -q
   ```

4. New domain tests pass:
   ```bash
   uv run pytest tests/models/test_domain/test_workcell_sqlmodel.py tests/models/test_domain/test_user_sqlmodel.py -v
   ```

---

## 6. Implementation Steps

1. **Audit WorkcellOrm**:
   - Name, description, location fields
   - Relationships to Machine, Resource

2. **Audit UserOrm**:
   - Username, email, password hash
   - External auth fields (keycloak_id, etc.)
   - Profile fields

3. **Create domain/workcell.py**:
   - Import base classes
   - Implement Workcell models

4. **Create domain/user.py**:
   - Import base classes
   - Implement User models
   - Ensure password_hash NOT in UserRead

5. **Implement CRUD schemas for both**

6. **Export from domain/__init__.py**

7. **Create test files**:
   - `tests/models/test_domain/test_workcell_sqlmodel.py`
   - `tests/models/test_domain/test_user_sqlmodel.py`

---

## On Completion

- [ ] Commit changes with message: `feat(models): migrate Workcell + User to SQLModel`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 4.2 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
