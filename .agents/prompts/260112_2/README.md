# Agent Prompt Batch: 2026-01-12 (Part 2)

**Created:** 2026-01-12
**Focus Area:** SQLModel Domain Relationship Completeness
**Total Prompts:** 4
**Backlog:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md) (Phase 7.1)

---

## Problem Statement

During SQLModel migration, 16 test setup errors were discovered caused by missing `Relationship()` navigation fields on models that have foreign key columns. This blocks 92+ test failures across the domain model test suite.

**Root Cause**: Models have FK columns but no corresponding Relationship fields for ORM navigation.

**Example**:

```python
# Has FK column:
source_repository_accession_id: uuid.UUID | None = Field(foreign_key="...")

# Missing Relationship field:
# source_repository: Relationship[ProtocolSourceRepository]  # ❌ MISSING

# Tests fail:
protocol.source_repository = repo  # ValidationError: no such attribute
```

---

## Prompts

| # | Status | Priority | Filename | Description | Complexity | Key Files | Verification |
|---|--------|----------|----------|-------------|------------|-----------|--------------|
| 1 | 🟢 Not Started | **P1** | [P1_01_add_protocol_relationships.md](P1_01_add_protocol_relationships.md) | Add Relationship fields to FunctionProtocolDefinition | Medium | `protocol.py`, `protocol_source.py` | `pytest test_asset_reservation.py --collect-only` |
| 2 | ✅ Completed | **P2** | [P2_01_audit_all_domain_relationships.md](P2_01_audit_all_domain_relationships.md) | Audit all 15 domain models for FK/Relationship mismatches | Medium | All `domain/*.py` files | Create `AUDIT_REPORT.md` |
| 3 | 🟢 Not Started | **P2** | [P2_02_add_domain_relationships.md](P2_02_add_domain_relationships.md) | Add missing Relationship fields identified in audit | Medium | `machine.py`, `resource.py`, etc. | `pytest --collect-only` |
| 4 | 🟢 Not Started | **P3** | [P3_01_fix_remaining_test_failures.md](P3_01_fix_remaining_test_failures.md) | Fix 92 test failures after relationship additions | Medium | All `test_domain/*.py` files | `pytest tests/models/test_domain/ -v` |

---

## Execution Order

### Phase 1: Critical Fix (P1)

```
P1_01 (Add Protocol Relationships)
  │
  │  Fixes: 16 setup errors in test_asset_reservation.py
  │  Enables: Test fixture patterns for protocol models
  │
  ▼
Verify: uv run pytest tests/models/test_domain/test_asset_reservation.py --collect-only --quiet
```

### Phase 2: Comprehensive Audit (P2)

```
P2_01 (Audit All Relationships)
  │
  │  Output: AUDIT_REPORT.md with findings
  │  Identifies: Additional missing relationships in other models
  │
  ▼
Decision: Generate P2_XX prompts if audit reveals more critical issues
  │  (Triggered: P2_02 generated)
  │
  ▼
P2_02 (Add Missing Relationships)
  │  Fixes: Machine, Resource, Schedule, Output relationships
  │  Enables: Full ORM navigation
  ▼

### Phase 3: Test Stabilization (P3)

```

P3_01 (Fix Remaining Tests)
  │
  │  Resolves: 92 test failures
  │  Categories: Schema serialization, model creation, relationships
  │
  ▼
Success: All domain model tests pass (2,105+ tests collecting cleanly)

```

---

## Impact Analysis

**Before Fix:**

- ❌ 16 test setup errors (blocking)
- ❌ 92+ test failures
- ❌ 11% test coverage (failing)
- ❌ Cannot use `protocol.source_repository` navigation

**After P1:**

- ✅ 0 test setup errors
- ⚠️ 92 test failures (now debuggable)
- ⚠️ Tests can run but need fixes
- ✅ Relationship navigation works

**After P1 + P3:**

- ✅ 0 test setup errors
- ✅ 0 test failures
- ✅ 80%+ test coverage
- ✅ Full SQLModel relationship navigation
- ✅ Phase 7.1 complete

---

## Technical Context

**Reference Pattern** (from `deck.py`):

```python
from typing import TYPE_CHECKING, Optional
from sqlmodel import Relationship
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from praxis.backend.models.domain.other_model import OtherModel

class MyModel(MyBase, table=True):
    __tablename__ = "my_models"

    # FK column
    other_model_id: uuid.UUID = Field(foreign_key="other_models.accession_id")

    # Relationship field
    other_model: Optional["OtherModel"] = Relationship(
        sa_relationship=relationship("OtherModel", back_populates="my_models")
    )
```

**Key Principles:**

1. Every FK column should have a corresponding Relationship field
2. Use `TYPE_CHECKING` for circular imports
3. Use `sa_relationship=relationship()` wrapper for SQLModel compatibility
4. Use `back_populates` for bidirectional relationships
5. Use `Optional[]` for nullable FKs, `list[]` for collections

---

## Status Legend

| Status | Meaning |
|--------|---------|
| 🟢 Not Started | Ready for agent dispatch |
| 🟡 In Progress | Currently being worked on |
| 🔴 Blocked | Waiting on dependency or clarification |
| ✅ Completed | Work done and verified |

---

## Related Work

**Previous Migration Work:**

- `.agents/prompts/260112/` - Initial SQLModel consolidation (completed)
- `scripts/fix_orm_references.py` - Automated XOrm → X replacements (68 files)
- Test collection: Achieved 2,105 tests with 0 import errors

**Remaining SQLModel Work:**

- Phase 7.2: Final Alembic migration validation
- Frontend TypeScript client regeneration
- Documentation updates

---

## Notes

- All prompts target the `angular_refactor` branch
- P1 is the critical blocker - execute first
- P2 can run in parallel after P1 completes
- P3 depends on P1 completion but not P2
- Build verification: `uv run pytest tests/models/test_domain/ --collect-only --quiet`
- Full test run: `uv run pytest tests/models/test_domain/ -v`

---

## Completion Checklist

- [ ] P1_01 executed (critical fix)
- [ ] P2_01 executed (audit)
- [ ] P3_01 executed (test stabilization)
- [ ] All domain model tests passing
- [ ] Coverage >80% achieved
- [ ] [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md) Phase 7.1 marked complete
- [ ] [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) updated
- [ ] Changes committed with descriptive messages
- [ ] No regression in other test suites

---

## Output Summary

| Prompt | Backlog Item | Complexity | Key Implementation Targets | Verification Command |
|--------|--------------|------------|---------------------------|----------------------|
| P1_01 | Phase 7.1 Critical | Medium | `protocol.py:270-291`, `protocol_source.py:32,76` | `uv run pytest tests/models/test_domain/test_asset_reservation.py --collect-only --quiet` |
| P2_01 | Phase 7.1 Audit | Medium | All `domain/*.py` (15 files) | Create `AUDIT_REPORT.md` with findings |
| P3_01 | Phase 7.1 Testing | Medium | All `test_domain/*.py` (13 test files, 92+ tests) | `uv run pytest tests/models/test_domain/ -v` |
