# Code Quality Resolution Plan

**Priority**: P2 (High)
**Owner**: Full Stack
**Created**: 2026-01-02
**Status**: Planning

---

## Overview

Given the scale of the Praxis codebase (backend + Angular frontend), this document outlines a comprehensive code quality strategy covering linting, type checking, testing, and architectural consistency.

---

## 1. Current State Assessment

### Backend (Python)

- **Linter**: Ruff
- **Type Checker**: Pyright / ty
- **Test Framework**: pytest
- **Coverage**: Partial (see gaps below)

### Frontend (Angular/TypeScript)

- **Linter**: ESLint (Angular specific)
- **Type Checker**: TypeScript (strict mode?)
- **Test Framework**: Vitest (for unit tests), Playwright (for E2E)
- **Coverage**: Partial (many features lack tests)

---

## 2. Priority 1: Type Error Resolution

### 2.1 Backend Type Errors

- [ ] Run `uv run pyright praxis/backend` and capture current error count
- [ ] Triage errors by severity (Critical > Major > Minor)
- [ ] Create targeted fix PRs for each module:
  - [ ] `praxis/backend/core/` - Core business logic (highest priority)
  - [ ] `praxis/backend/services/` - Service layer
  - [ ] `praxis/backend/api/` - API routes
  - [ ] `praxis/backend/models/` - Pydantic/ORM models
  - [ ] `praxis/backend/utils/` - Utility functions
- [x] **Verify deletions during ty error resolution didn't break functionality**
- [ ] Target: < 40 pyright errors (per GEMINI.md guidance)

### 2.2 Frontend Type Errors

- [ ] Run `npm run typecheck` (or equivalent) and capture current state
- [ ] Enable stricter TypeScript options where feasible:
  - [ ] `strictNullChecks`
  - [ ] `noImplicitAny`
- [ ] Fix type errors in core services first:
  - [ ] `sqlite.service.ts`
  - [ ] `execution.service.ts`
  - [ ] `asset.service.ts`
  - [ ] `protocol.service.ts`

---

## 3. Priority 2: Linting Enforcement

### 3.1 Backend Linting (Ruff)

- [ ] Review current `.ruff.toml` / `pyproject.toml [tool.ruff]` configuration
- [ ] Enable critical rule categories if not already:
  - `F` - Pyflakes (errors)
  - `E` - pycodestyle errors
  - `B` - Bugbear (likely bugs)
- [ ] Run `uv run ruff check praxis/backend --statistics` to inventory issues
- [ ] Address critical issues first (F, E, B categories)
- [ ] Then address style/convention issues (I, UP, SIM, etc.)

### 3.2 Frontend Linting (ESLint)

- [ ] Review current ESLint configuration
- [ ] Enable Angular-specific plugins if not present
- [ ] Run `npm run lint` and inventory issues
- [ ] Create fix batches by rule category

---

## 4. Priority 3: Test Coverage

### 4.1 Backend Test Coverage Strategy

| Module | Current Coverage | Target | Priority |
|--------|-----------------|--------|----------|
| `praxis/backend/core/` | Unknown | 80% | High |
| `praxis/backend/services/` | Partial | 70% | High |
| `praxis/backend/api/` | Partial | 60% | Medium |
| `praxis/backend/models/` | Low | 50% | Medium |
| `praxis/backend/utils/` | Low | 70% | Medium |

- [ ] Run `uv run pytest --cov=praxis/backend --cov-report=html` for current baseline
- [ ] Identify modules with < 50% coverage
- [ ] Create test files for untested modules
- [ ] Focus on: execution flow, asset management, protocol parsing

### 4.2 Frontend Test Coverage Strategy

| Feature | Current Coverage | Target | Priority |
|---------|-----------------|--------|----------|
| Core Services | Partial | 80% | High |
| REPL Component | Partial | 70% | High |
| Asset Management | Low | 60% | High |
| Deck Visualizer | Low | 60% | Medium |
| Execution Monitor | Low | 60% | Medium |

- [ ] Run `npm run test -- --coverage` for Vitest coverage
- [ ] Identify components/services with no tests
- [ ] Create spec files for each component in `shared/components/`
- [ ] Create spec files for each service in `core/services/`

### 4.3 E2E Test Coverage

- [ ] Review current Playwright test suite
- [ ] Create E2E tests for critical user flows:
  - [ ] Protocol selection and execution
  - [ ] Asset management CRUD
  - [ ] REPL session (type, execute, see output)
  - [ ] Execution monitor (view runs, filter, detail view)
  - [ ] Deck setup wizard
- [ ] Create browser-mode-specific E2E tests
- [ ] Target: All P1 features have E2E coverage

---

## 5. Priority 4: Architectural Consistency

### 5.1 Backend Architecture Audit

- [ ] Verify all services use `@handle_db_transaction` decorator
- [ ] Verify Pydantic models are in `models/pydantic/` directory (not inline)
- [ ] Verify API routes follow CRUD router factory pattern
- [ ] Remove any deprecated code paths

### 5.2 Frontend Architecture Audit

- [ ] Verify all components use signals (not legacy `@Input/@Output` where possible)
- [ ] Verify services follow consistent patterns
- [ ] Verify lazy loading for feature modules
- [ ] Remove unused imports and dead code

---

## 6. Automation & CI/CD

### 6.1 Pre-Commit Hooks

- [ ] Verify pre-commit config includes:
  - Ruff (lint + format)
  - Pyright (type check)
  - ESLint (frontend lint)
  - Prettier (frontend format)

### 6.2 CI Pipeline

- [ ] Backend: lint → typecheck → test → coverage
- [ ] Frontend: lint → typecheck → test → build
- [ ] E2E: Run Playwright suite on PR

---

## 7. Execution Plan

### Week 1: Assessment

- Run all type checkers and linters
- Generate coverage reports
- Inventory all issues by severity

### Week 2-3: Critical Fixes

- Fix P1 type errors (core modules)
- Fix P1 lint errors (F, E, B categories)
- Verify ty error resolution deletions

### Week 4-5: Test Coverage

- Add tests for untested core services
- Add E2E tests for critical flows
- Reach coverage targets

### Week 6: Polish

- Address remaining lint issues
- Architectural consistency audit
- Documentation updates

---

## Related Documents

- [GEMINI.md](../GEMINI.md) - Pyright target (<40 errors), testing strategy
- [linting_and_type_checking.md](./linting_and_type_checking.md) - Detailed linting backlog
- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Known debt items
