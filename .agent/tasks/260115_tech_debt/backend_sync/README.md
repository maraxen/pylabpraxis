# Task: Backend Test & File Sync

**ID**: TD-301
**Status**: ⚪ Not Started
**Priority**: P2
**Difficulty**: Medium

---

## 📋 Phase 1: Inspection (I)

**Objective**: Identify all backend tests/files affected by recent schema changes.

- [ ] Search for `_json` suffix usage in tests
- [ ] Search for `ProtocolRunRead` field references
- [ ] Identify repositories/services using old field names
- [ ] List all failing tests related to schema changes

**Findings**:
> [To be captured during inspection]

---

## 📐 Phase 2: Planning (P)

**Objective**: Define systematic update strategy.

- [ ] Catalog all field name changes (old → new)
- [ ] Map affected files
- [ ] Order updates to avoid cascade failures

**Implementation Plan**:

1. Update model imports/references
2. Update test fixtures and mocks
3. Update service layer calls
4. Update repository queries

**Definition of Done**:

1. All backend tests pass
2. No references to old field names remain
3. Consistent JSONB suffixing across codebase

---

## 🛠️ Phase 3: Execution (E)

**Objective**: Implement schema alignment updates.

- [ ] Update test fixtures
- [ ] Update repository methods
- [ ] Update service layer
- [ ] Fix any type mismatches

**Work Log**:

- [Pending]

---

## 🧪 Phase 4: Testing & Verification (T)

**Objective**: Full test suite verification.

- [ ] `uv run pytest tests/backend/`
- [ ] `uv run pytest tests/models/`
- [ ] Grep verification: No old field names in active code

**Results**:
> [To be captured]

---

## 📚 Tracking & Context

- **Matrix Reference**: [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- **Technical Debt ID**: 301
- **Files**:
  - `praxis/backend/` - Backend code
  - `tests/backend/` - Backend tests
