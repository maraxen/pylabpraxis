# Agent Prompt: Audit All Domain Models for Relationship Completeness

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260112_2](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md) (Phase 7.1)

---

## 1. The Task

Perform comprehensive audit of all domain models in `praxis/backend/models/domain/` to identify foreign key columns missing corresponding `Relationship()` navigation fields.

**User Value**: Ensures consistent SQLModel patterns across the entire codebase, preventing future test failures and enabling proper ORM navigation throughout the application.

**Scope**: Audit 15 domain model files to document:

- FK columns without Relationship fields
- Relationship fields without FK columns (orphans)
- Mismatched `back_populates` configurations
- Circular import issues

---

## 2. Technical Implementation Strategy

**Architecture**: Systematic file-by-file audit using pattern matching from working examples (deck.py).

**Audit Methodology:**

1. **For Each Model File**:
   - List all `Field()` declarations with `foreign_key=` parameter
   - List all `Relationship()` field declarations
   - Cross-reference FK ↔ Relationship pairs
   - Check for `back_populates` consistency
   - Verify `TYPE_CHECKING` imports for circular references

2. **Document Findings**:
   - Create structured markdown report
   - Categorize issues by severity:
     - **Critical**: Missing Relationship for FK (blocks navigation)
     - **Warning**: Orphaned Relationship (no FK column)
     - **Info**: Missing back_populates (unidirectional by design)

3. **Generate Fix Plan**:
   - List specific models needing updates
   - Estimate complexity per fix
   - Identify dependencies between fixes

**Files to Audit** (priority order):

| File | Tables | Estimated FKs |
|------|--------|---------------|
| `protocol.py` | 4 models | ~8 FKs |
| `schedule.py` | 4 models | ~10 FKs |
| `asset.py` | 3 models | ~2 FKs |
| `machine.py` | 2 models | ~5 FKs |
| `resource.py` | 2 models | ~5 FKs |
| `deck.py` | 3 models | ~7 FKs (✅ reference) |
| `workcell.py` | 1 model | ~3 FKs |
| `outputs.py` | 2 models | ~4 FKs |
| `protocol_source.py` | 2 models | ~0 FKs |
| `user.py` | 1 model | ~0 FKs |

**Audit Script Pattern**:

```bash
# Find all FK columns:
uv run grep -n "foreign_key=" praxis/backend/models/domain/*.py

# Find all Relationship fields:
uv run grep -n "Relationship\[" praxis/backend/models/domain/*.py

# Check back_populates usage:
uv run grep -n "back_populates=" praxis/backend/models/domain/*.py
```

---

## 3. Context & References

**Primary Files to Audit:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/*.py` | All 15 domain model files |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/backend/models/domain/deck.py` | Gold standard example (complete relationships) |
| `praxis/backend/models/domain/protocol.py` | Known issue (P1 fixes this) |
| `tests/models/test_domain/*.py` | Test files that reveal relationship usage patterns |

**Output Location:**

| Path | Description |
|:-----|:------------|
| `.agents/prompts/260112_2/AUDIT_REPORT.md` | Create this file with findings |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run` for Python commands
- **Backend Path**: `praxis/backend`
- **Audit Format**: Structured markdown with severity levels
- **No Code Changes**: This is audit-only; do not modify code
- **Comprehensive**: Check every model file, even if it looks correct
- **Cross-Reference**: Verify both sides of bidirectional relationships

---

## 5. Verification Plan

**Definition of Done:**

1. Audit report created at `.agents/prompts/260112_2/AUDIT_REPORT.md`
2. Report includes:
   - Executive summary (counts by severity)
   - Per-file findings table
   - Recommended fix priority
   - Estimated complexity per fix
3. All 15 domain model files reviewed
4. Cross-referenced with test files for validation
5. Generated remediation plan with specific file/line targets

**Report Structure**:

```markdown
# Domain Model Relationship Audit Report

## Executive Summary
- Total Models Audited: 15
- Critical Issues: X (missing Relationships for FKs)
- Warnings: Y (orphaned Relationships)
- Info: Z (unidirectional by design)

## Findings by File

### praxis/backend/models/domain/protocol.py
**Status**: ⚠️ Critical Issues Found

| Model | Line | FK Column | Relationship Field | Severity | Notes |
|-------|------|-----------|-------------------|----------|-------|
| FunctionProtocolDefinition | 285 | source_repository_accession_id | ❌ Missing | Critical | P1 will fix |

[... detailed findings ...]

## Remediation Plan
[... prioritized fix plan ...]
```

---

## On Completion

- [x] Create `AUDIT_REPORT.md` in `.agents/prompts/260112_2/`
- [x] Update [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md) with audit findings
- [x] Mark this prompt complete in [batch README](./README.md)
- [x] Set status to 🟢 Completed in this file
- [ ] Generate follow-up prompts if additional P2 fixes needed

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Migration context
- [SQLModel Relationships](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/)
- [SQLAlchemy Foreign Keys](https://docs.sqlalchemy.org/en/20/core/constraints.html#foreign-keys)
