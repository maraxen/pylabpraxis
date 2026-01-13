# Agent Prompt: Migrate ProtocolSource (Repository + FileSystem) to SQLModel

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 3.3 — Model Migration: Protocol Source
**Parallelizable:** ⚠️ Can run in parallel with P2_07/P2_08 after Phase 2

---

## 1. The Task

Unify `ProtocolSourceRepository` and `FileSystemProtocolSource` models from separate ORM and Pydantic definitions into SQLModel domain models. These use polymorphic inheritance to support different protocol storage backends.

**User Value:** Single source of truth for protocol storage configuration with automatic API type generation.

---

## 2. Technical Implementation Strategy

### Current Architecture

**ORM** (`praxis/backend/models/orm/protocol.py`):
- `ProtocolSourceRepositoryOrm` — Base model for protocol sources (polymorphic)
- `FileSystemProtocolSourceOrm(ProtocolSourceRepositoryOrm)` — File system storage

**Polymorphic Pattern:**
```python
class ProtocolSourceRepositoryOrm(Base):
    __tablename__ = "protocol_source_repositories"
    source_type: Mapped[str] = mapped_column(String, index=True)
    
    __mapper_args__ = {
        "polymorphic_on": source_type,
        "polymorphic_identity": "repository",
    }

class FileSystemProtocolSourceOrm(ProtocolSourceRepositoryOrm):
    # Single-table inheritance - no separate tablename
    source_path: Mapped[str] = mapped_column(String)
    
    __mapper_args__ = {
        "polymorphic_identity": "filesystem",
    }
```

**Pydantic:** (May be minimal or combined with protocol.py models)

---

## 3. Context & References

**Primary Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/protocol_source.py` | Unified ProtocolSource models |

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/__init__.py` | Export ProtocolSource models |

**Files to Deprecate (parts of):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/orm/protocol.py` | Contains ProtocolSourceRepositoryOrm, FileSystemProtocolSourceOrm |

**Reference Files (Read-Only):**

| Path | Pattern Source |
|:-----|:---------------|
| `praxis/backend/models/orm/protocol.py` | ORM with polymorphic source types |
| `tests/models/test_orm/test_protocol_source_repository_orm.py` | Repository tests |
| `tests/models/test_orm/test_file_system_protocol_source_orm.py` | FileSystem tests |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands.
- **Backend Path**: `praxis/backend`
- **Polymorphic inheritance**: Use string discriminator (`source_type`)
- **Single-table inheritance**: All source types in `protocol_source_repositories` table

### Sharp Bits / Technical Debt

1. **Polymorphic pattern**: Similar to Asset but with string discriminator
2. **Extensibility**: Design should allow adding new source types (git, S3, etc.)
3. **Path handling**: FileSystem source has file path validation needs

---

## 5. Verification Plan

**Definition of Done:**

1. Models import successfully:
   ```bash
   uv run python -c "
   from praxis.backend.models.domain.protocol_source import (
       ProtocolSourceRepository, FileSystemProtocolSource,
       ProtocolSourceCreate, FileSystemProtocolSourceCreate
   )
   print('OK')
   "
   ```

2. Polymorphic creation works:
   ```bash
   uv run python -c "
   from sqlmodel import SQLModel, create_engine, Session
   from praxis.backend.models.domain.protocol_source import (
       ProtocolSourceRepository, FileSystemProtocolSource
   )
   
   engine = create_engine('sqlite:///:memory:')
   SQLModel.metadata.create_all(engine)
   
   with Session(engine) as s:
       fs = FileSystemProtocolSource(
           name='local_protocols',
           source_path='/protocols',
       )
       s.add(fs)
       s.commit()
       assert fs.source_type == 'filesystem'
       print(f'FileSystemProtocolSource: type={fs.source_type}, path={fs.source_path}')
   "
   ```

3. Existing tests still pass:
   ```bash
   uv run pytest tests/models/test_orm/test_protocol_source_repository_orm.py tests/models/test_orm/test_file_system_protocol_source_orm.py -x -q
   ```

4. New domain tests pass:
   ```bash
   uv run pytest tests/models/test_domain/test_protocol_source_sqlmodel.py -v
   ```

---

## 6. Implementation Steps

1. **Audit ORM models**:
   - ProtocolSourceRepositoryOrm base fields
   - FileSystemProtocolSourceOrm additional fields
   - Polymorphic setup

2. **Create domain/protocol_source.py**:
   - Import base classes

3. **Implement ProtocolSourceRepositoryBase**:
   - Shared fields for all source types
   - `source_type` discriminator

4. **Implement ProtocolSourceRepository(table=True)**:
   - `__tablename__ = "protocol_source_repositories"`
   - Polymorphic base identity

5. **Implement FileSystemProtocolSource(ProtocolSourceRepository)**:
   - `source_path` field
   - Polymorphic identity "filesystem"

6. **Implement CRUD schemas**

7. **Export from domain/__init__.py**

8. **Create test file**:
    - `tests/models/test_domain/test_protocol_source_sqlmodel.py`

---

## On Completion

- [ ] Commit changes with message: `feat(models): migrate ProtocolSource entities to SQLModel`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 3.3 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
