# Quality Assurance

**Priority**: P2 (High)
**Owner**: Full Stack
**Created**: 2026-01-06 (consolidated from 3 files)
**Status**: Active

---

## Overview

This document consolidates all quality assurance work including linting, type checking, testing, and visual QA.

---

## 1. Linting & Type Checking

### Current State

| Tool | Errors | Notes |
|------|--------|-------|
| Ruff | ~65 | Python linting (circular imports deferred) |
| ty | 10+ | Type checking (preferred over bare pyright) |
| ESLint | Active | Angular linting (configured) |

### Priority Categories

1. **Critical (Fix First)**: `F` (Pyflakes), `E` (Errors), `B` (Bugbear)
2. **Style (Fix Later)**: `W` (Warnings), `C` (Complexity)

### Tasks

- [x] Run `uv run ruff check --fix praxis/backend` to auto-fix (✅ 12 fixed)
- [ ] Address remaining Ruff errors manually (circular imports deferred)
- [ ] Run `uv run ty praxis/backend` and fix type errors
- [x] Configure ESLint for frontend (✅ Active)

---

## 2. Test Coverage

### Backend Tests

| Area | Status | Command |
|------|--------|---------|
| Services | ⏳ Partial | `uv run pytest tests/services/` |
| API | ⏳ Partial | `uv run pytest tests/api/` |
| Core | ✅ Good (87 simulation tests) | `uv run pytest tests/core/` |

### Frontend Tests

| Area | Status | Notes |
|------|--------|-------|
| SqliteService | ✅ Good | Browser DB service tests complete |
| Components | ⏳ Partial | Angular unit tests |

### E2E Tests

| Flow | Status | Tool |
|------|--------|------|
| Asset Management | ✅ Complete | Playwright |
| Protocol Execution | ⏳ Todo | Playwright |
| Browser Mode | ⏳ Todo | Playwright |

### Commands

```bash
# Backend coverage
uv run pytest --cov=praxis/backend --cov-report=xml

# Frontend tests  
cd praxis/web-client && npm test

# E2E (when configured)
npx playwright test
```

### Tasks

- [ ] Investigate and resolve skipped tests (see [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md))
- [x] Implement E2E tests for Asset Management (5 UI tests passing, CRUD tests skipped - require seeded data)

---

## 3. Visual QA Checklist

### Critical Flows

- [ ] First-time user experience (welcome, tutorial)
- [ ] Asset CRUD (add/edit/delete resources and machines)
- [ ] Protocol selection and execution
- [ ] REPL interaction

### Theme Testing

- [ ] Light mode consistency
- [ ] Dark mode consistency
- [ ] Theme toggle works everywhere

### Responsive Design

- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (1024x768)

### Accessibility

- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] Color contrast ratios

---

## 4. Skipped Tests Investigation

**Priority**: Medium (from TECHNICAL_DEBT.md #6)
**Added**: 2026-01-07

Several unit tests are currently skipped to allow CI to pass. These need investigation.

### Known Skipped Tests

**Backend:**

- `tests/core/test_orchestrator.py`

**Frontend:**

- `welcome-dialog.component.spec.ts`
- `asset-selector.component.spec.ts`
- `wizard-state.service.spec.ts`

### Tasks

- [ ] Audit all skipped tests in `tests/` (Python)
- [ ] Audit all skipped tests in `src/**/*.spec.ts` (Angular)
- [ ] Identify root causes for skipping
- [ ] Fix or properly mock dependencies

---

## 5. Test Factory ORM Integration Issues

**Priority**: High (from TECHNICAL_DEBT.md)
**Added**: 2026-01-07
**Area**: Testing - Factory Boy / SQLAlchemy Integration

### Issue

`FunctionDataOutputFactory` and related factories fail to correctly populate foreign key fields, causing `NOT NULL constraint failed` errors in `tests/services/test_well_outputs.py`.

### Root Cause

SQLAlchemy's dataclass-style ORM mapping requires `kw_only=True` for non-default fields. Factories use `SubFactory` and `LazyAttribute` which don't properly flush before dependent ORM creation.

### Files Affected

- `tests/services/test_well_outputs.py`
- `tests/factories.py` (FunctionDataOutputFactory, FunctionCallLogFactory, WellDataOutputFactory)
- `praxis/backend/models/orm/outputs.py`

### Tasks

- [ ] Investigate factory flush timing
- [ ] Review ORM model field ordering
- [ ] Fix factory definitions or add manual flush calls

---

## Success Criteria

1. [ ] Ruff errors < 20
2. [ ] Pyright errors < 10
3. [ ] Backend test coverage > 70%
4. [ ] All critical E2E flows pass
5. [ ] Visual QA checklist complete

---

## Related Documents

- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Code quality issues
