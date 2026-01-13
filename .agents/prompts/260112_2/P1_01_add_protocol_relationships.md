# Agent Prompt: Add Relationship Fields to Protocol Models

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260112_2](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md) (Phase 7.1)

---

## 1. The Task

Add missing `Relationship()` navigation fields to `FunctionProtocolDefinition` model to resolve 16 test setup errors that block 92+ test failures.

**User Value**: Enables SQLModel relationship navigation patterns, allowing tests and application code to use `protocol.source_repository` instead of only FK-based queries. This completes the SQLModel migration for protocol models.

**Root Cause**: The `FunctionProtocolDefinition` model has foreign key columns (`source_repository_accession_id`, `file_system_source_accession_id`) but lacks the corresponding `Relationship()` fields for ORM navigation.

**Error Pattern**:

```python
protocol.source_repository = source_repository
# ValidationError: Object has no attribute 'source_repository'
```

---

## 2. Technical Implementation Strategy

**Architecture**: Add bidirectional ORM relationships following SQLModel + SQLAlchemy Core pattern established in `deck.py`.

**Models to Modify:**

1. **`FunctionProtocolDefinition`** in `praxis/backend/models/domain/protocol.py` (lines 270-291)
   - Add `source_repository: Relationship[ProtocolSourceRepository]`
   - Add `file_system_source: Relationship[FileSystemProtocolSource]`
   - Use `Optional[]` type hints since FK fields are nullable
   - Use `sa_relationship=relationship()` pattern from deck.py

2. **`ProtocolSourceRepository`** in `praxis/backend/models/domain/protocol_source.py` (line 32)
   - Add `protocols: list[FunctionProtocolDefinition]` back-reference
   - Use `back_populates="source_repository"`

3. **`FileSystemProtocolSource`** in `praxis/backend/models/domain/protocol_source.py` (line 76)
   - Add `protocols: list[FunctionProtocolDefinition]` back-reference
   - Use `back_populates="file_system_source"`

**Data Flow:**

1. Import required types under `TYPE_CHECKING` to avoid circular imports
2. Add Relationship fields with proper `sa_relationship()` wrappers
3. Configure `back_populates` for bidirectional navigation
4. Tests can now use `protocol.source_repository = repo` pattern

**Reference Pattern** (from `deck.py` lines 233-245):

```python
from typing import TYPE_CHECKING, Optional
from sqlmodel import Relationship
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from praxis.backend.models.domain.protocol_source import (
        ProtocolSourceRepository,
        FileSystemProtocolSource,
    )

# In FunctionProtocolDefinition:
source_repository: Optional["ProtocolSourceRepository"] = Relationship(
    sa_relationship=relationship("ProtocolSourceRepository", back_populates="protocols")
)
file_system_source: Optional["FileSystemProtocolSource"] = Relationship(
    sa_relationship=relationship("FileSystemProtocolSource", back_populates="protocols")
)
```

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/protocol.py` | Add Relationship fields to `FunctionProtocolDefinition` (lines 270-291) |
| `praxis/backend/models/domain/protocol_source.py` | Add back-references to `ProtocolSourceRepository` and `FileSystemProtocolSource` |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/deck.py` | Working example of Relationship pattern (lines 233-256) |
| `tests/models/test_domain/test_asset_reservation.py` | Test fixture that reveals the issue (lines 50-67) |
| `praxis/backend/models/domain/machine.py` | Another example of relationship patterns |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands
- **Backend Path**: `praxis/backend`
- **Import Pattern**: Use `TYPE_CHECKING` for circular imports
- **Relationship Pattern**: Always pair `Relationship()` with `sa_relationship=relationship()`
- **Bidirectional**: Use `back_populates` parameter for two-way navigation
- **Type Hints**: Use `Optional["ClassName"]` for nullable FKs, `list["ClassName"]` for collections
- **Testing**: Run collection before full test to catch import errors early

---

## 5. Verification Plan

**Definition of Done:**

1. Code compiles without import errors
2. Test collection succeeds (no setup errors):

   ```bash
   uv run pytest tests/models/test_domain/test_asset_reservation.py --collect-only --quiet
   ```

3. Fixture-dependent tests pass:

   ```bash
   uv run pytest tests/models/test_domain/test_asset_reservation.py -v
   ```

4. Full domain model test collection succeeds:

   ```bash
   uv run pytest tests/models/test_domain/ --collect-only --quiet
   ```

5. Type checking passes (if applicable):

   ```bash
   uv run mypy praxis/backend/models/domain/protocol.py
   ```

---

## On Completion

- [ ] Commit changes with message: "fix(models): add missing Relationship fields to FunctionProtocolDefinition"
- [ ] Update [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md) Phase 7.1 progress
- [ ] Mark this prompt complete in [batch README](./README.md)
- [ ] Set status to 🟢 Completed in this file

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - SQLModel migration context
- `praxis/backend/models/domain/deck.py` - Reference implementation
- [SQLModel Relationships Docs](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/)
- [SQLAlchemy Relationship Patterns](https://docs.sqlalchemy.org/en/20/orm/relationships.html)
