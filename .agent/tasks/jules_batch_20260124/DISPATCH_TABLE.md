# Jules Dispatch Table - 2026-01-24 (Wave 7)

## Overview

| Category | Count | Priority Mix |
|:---------|:------|:-------------|
| **DOC** (documentation) | 3 | P2 |
| **FIX** (bug fixes) | 4 | P1-P2 |
| **TEST** (new tests) | 3 | P1-P2 |
| **STYLE** (theme cleanup) | 3 | P2 |
| **REFACTOR** (code quality) | 2 | P2 |
| **TOTAL** | **15** | |

---

## Complete Task List

| ID | Title | Priority | Target | Skills |
|:---|:------|:---------|:-------|:-------|
| **DOC-01** | Update CONTRIBUTING.md with uv commands | P2 | `CONTRIBUTING.md` | `fixer.md` |
| **DOC-02** | Fix Docker service names in docs | P2 | `docs/*.md` (5 files) | `fixer.md` |
| **DOC-03** | Create CHANGELOG.md | P2 | Root `CHANGELOG.md` | `fixer.md` |
| **FIX-01** | Implement machine editing TODO | P2 | `machine-list.component.ts` | `fixer.md` |
| **FIX-02** | Implement resource editing TODO | P2 | `resource-list.component.ts` | `fixer.md` |
| **FIX-03** | Add deck confirmation dialog | P2 | `deck-setup-wizard.component.ts` | `fixer.md` |
| **FIX-04** | Guard method.args undefined | P1 | `direct-control.component.ts` | `fixer.md` |
| **TEST-01** | Add unit tests for name-parser.ts | P2 | `shared/utils/name-parser.ts` | `fixer.md`, `vitest` |
| **TEST-02** | Add unit tests for linked-selector.service | P2 | `shared/services/linked-selector.service.ts` | `fixer.md`, `vitest` |
| **TEST-03** | Create workcell dashboard E2E | P2 | `workcell-dashboard.spec.ts` | `playwright-skill` |
| **STYLE-01** | Theme vars in protocol-summary | P2 | `protocol-summary.component.ts` | `fixer.md` |
| **STYLE-02** | Theme vars in live-dashboard | P2 | `live-dashboard.component.ts` | `fixer.md` |
| **STYLE-03** | Theme vars in settings | P2 | `settings.component.ts` | `fixer.md` |
| **REFACTOR-01** | Add user-friendly error toasts | P2 | `asset-wizard.ts` | `fixer.md` |
| **REFACTOR-02** | Document SharedArrayBuffer limitation | P3 | `docs/troubleshooting/` | `fixer.md` |

---

## Task Details

### DOC-01: Update CONTRIBUTING.md with uv commands

**Problem**: CONTRIBUTING.md uses deprecated `make` commands.

**Changes**:

- Replace `make test` with `uv run pytest`
- Replace `make lint` with `uv run ruff check`
- Replace `make typecheck` with `uv run mypy`
- Replace `make docs` with appropriate uv command

**Files**: `CONTRIBUTING.md`

---

### DOC-02: Fix Docker service names in docs

**Problem**: Documentation references incorrect Docker service name `db` instead of `praxis-db`.

**Files to update**:

1. `docs/getting-started/installation-production.md` (line 27)
2. `docs/reference/troubleshooting.md` (line 19)
3. `docs/reference/cli-commands.md` (line 7)
4. `docs/development/contributing.md` (line 23)
5. `docs/development/testing.md` (line 13)

**Change**: `db` → `praxis-db`

---

### DOC-03: Create CHANGELOG.md

**Problem**: No changelog exists at repository root.

**Create**: `CHANGELOG.md` following Keep a Changelog format with:

- Header with format links
- `[Unreleased]` section
- `[v0.1-alpha]` entry documenting initial features

---

### FIX-01: Implement machine editing TODO

**Location**: `src/app/features/assets/components/machine-list/machine-list.component.ts:529`

**Current**:

```typescript
// TODO: Implement machine editing
```

**Action**: Implement `editMachine(machine)` method that opens MachineDetailsDialog in edit mode or shows a snackbar indicating feature is in development.

---

### FIX-02: Implement resource editing TODO

**Location**: `src/app/features/assets/components/resource-list/resource-list.component.ts:249`

**Current**:

```typescript
// TODO: Implement resource editing
```

**Action**: Implement `editResource(resource)` method similar to machine editing approach.

---

### FIX-03: Add deck confirmation dialog

**Location**: `src/app/features/run-protocol/components/deck-setup-wizard/deck-setup-wizard.component.ts:337`

**Current**:

```typescript
// TODO: Add confirmation dialog
```

**Action**: Add MatDialog confirmation before destructive deck operations.

---

### FIX-04: Guard method.args undefined

**Location**: `src/app/features/playground/components/direct-control/direct-control.component.ts:88`

**Problem**: Crashes when `method.args` is undefined.

**Fix**:

```typescript
// Line 88
(method.args || []).forEach(arg => {

// Line 108 (similar guard)
(method.args || []).forEach(arg => {
```

---

### TEST-01: Add unit tests for name-parser.ts

**File**: `src/app/shared/utils/name-parser.ts`

**Create**: `src/app/shared/utils/name-parser.spec.ts`

**Requirements**:

- Test all public functions
- Cover edge cases (empty strings, special characters)
- Use Vitest patterns matching existing spec files

---

### TEST-02: Add unit tests for linked-selector.service

**File**: `src/app/shared/services/linked-selector.service.ts`

**File exists**: `src/app/shared/services/linked-selector.service.spec.ts`

**Requirements**:

- Expand existing tests if sparse
- Add edge case coverage
- Test Observable behavior patterns

---

### TEST-03: Create workcell dashboard E2E

**File**: `e2e/specs/workcell-dashboard.spec.ts`

**Requirements**:

- Navigate to `/app/workcell`
- Verify workcell overview loads
- Take screenshots for visual reference
- Test basic interactions (card clicks, filters)

---

### STYLE-01: Theme vars in protocol-summary

**File**: `src/app/features/run-protocol/components/protocol-summary/protocol-summary.component.ts`

**Replace Tailwind colors**:

- `bg-green-500/10` → `var(--theme-status-success-muted)`
- `text-green-500` → `var(--theme-status-success)`
- `border-green-500/20` → `var(--theme-status-success-border)`
- `text-red-500` → `var(--status-error)`

---

### STYLE-02: Theme vars in live-dashboard

**File**: `src/app/features/run-protocol/components/live-dashboard/live-dashboard.component.ts`

**Replace Tailwind colors**:

- `text-green-600` → `var(--theme-status-success)`
- `text-gray-400` → `var(--theme-text-tertiary)`
- `bg-green-100` → `var(--theme-status-success-muted)`
- `bg-red-100` → `var(--theme-status-error-muted)`
- `bg-gray-900` → `var(--mat-sys-surface-container)`

---

### STYLE-03: Theme vars in settings

**File**: `src/app/features/settings/settings.component.ts`

**Replace Tailwind colors**:

- `text-green-600` → `var(--theme-status-success)`
- `dark:text-green-400` → (remove, theme handles dark mode)

---

### REFACTOR-01: Add user-friendly error toasts

**File**: `src/app/shared/components/asset-wizard/asset-wizard.ts`

**Add**:

1. Inject `MatSnackBar`
2. Catch UNIQUE constraint errors in `createAsset()`
3. Show friendly messages instead of console errors

---

### REFACTOR-02: Document SharedArrayBuffer limitation

**Create**: `docs/troubleshooting/shared-array-buffer.md`

**Document**:

- SharedArrayBuffer requires COOP/COEP headers
- Impact on Python worker
- Workaround instructions

---

## Server Configuration

All E2E and component tests should use:

```bash
npm run start:browser
```

---

## Review Strategy

### P1 Tasks (Review First)

- FIX-04: Crash fix for direct control

### P2 Tasks (Parallel Review)

- All DOC tasks (low risk)
- All STYLE tasks (low risk)
- TEST tasks (additive)
- FIX-01, FIX-02, FIX-03 (contained changes)

### P3 Tasks

- REFACTOR-02: Documentation only

---

## Session Tracking

| ID | Session ID | Status | Merged |
|:---|:-----------|:-------|:-------|
| DOC-01 | | pending | |
| DOC-02 | | pending | |
| DOC-03 | | pending | |
| FIX-01 | | pending | |
| FIX-02 | | pending | |
| FIX-03 | | pending | |
| FIX-04 | | pending | |
| TEST-01 | | pending | |
| TEST-02 | | pending | |
| TEST-03 | | pending | |
| STYLE-01 | | pending | |
| STYLE-02 | | pending | |
| STYLE-03 | | pending | |
| REFACTOR-01 | | pending | |
| REFACTOR-02 | | pending | |
