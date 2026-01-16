# Task: Database & Models Cleanup

**ID**: TD-101-102
**Status**: ⚪ Not Started
**Priority**: P2
**Difficulty**: Medium

---

## 📋 Phase 1: Inspection (I)

**Objective**: Verify PostgreSQL compatibility and audit SQLModel warnings.

- [ ] Set up PostgreSQL test environment (Docker)
- [ ] Run test suite against PostgreSQL, document failures
- [ ] Grep for SQLModel "Field shadowing" warnings
- [ ] Identify which field re-declarations are intentional

**Findings**:
> [To be captured during inspection]

---

## 📐 Phase 2: Planning (P)

**Objective**: Define fix strategy for compatibility issues and warning suppression.

- [ ] Document PostgreSQL-specific behaviors that differ from SQLite
- [ ] Plan migration/compatibility fixes if needed
- [ ] Design targeted warning filter (preserve other warnings)

**Implementation Plan**:

1. PostgreSQL compatibility fixes (if any)
2. Add `warnings.filterwarnings` in appropriate location
3. Document intentional shadowing in code comments

**Definition of Done**:

1. Full test suite passes against PostgreSQL
2. SQLModel shadowing warnings silenced without hiding other issues
3. Documentation updated

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement planned changes.

- [ ] Apply PostgreSQL compatibility fixes
- [ ] Implement warning suppression
- [ ] Add inline documentation for intentional patterns

**Work Log**:

- [Pending]

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Verify fixes don't introduce regressions.

- [ ] `uv run pytest` against SQLite
- [ ] `uv run pytest` against PostgreSQL (Docker)
- [ ] Verify warnings are silenced: `python -W error::UserWarning -c "from praxis.backend.models import *"`

**Results**:
> [To be captured]

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Technical Debt IDs**: 101, 102
- **Files**:
  - `praxis/backend/models/` - Model definitions
  - `praxis/backend/models/domain/` - Domain models with shadowing
