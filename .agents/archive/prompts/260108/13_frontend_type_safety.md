# Agent Prompt: 13_frontend_type_safety

Examine `.agents/README.md` for development context.

**Status:** ✅ Completed  
**Batch:** [260108](./README.md)  
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)  
**Priority:** P3

---

## Task

Resolve TypeScript type safety issues in `SqliteService` and `SettingsComponent` tests, specifically fixing Blob casting and Window mocking.

---

## Issues to Fix

### 1. SqliteService Blob Casting

**Location**: `praxis/web-client/src/app/core/services/sqlite.service.ts`

**Issue**: `Uint8Array` to `BlobPart[]` casting in `exportDatabase` method.

```typescript
// Fixed:
const data = this.dbInstance.export();
const blob = new Blob([data.buffer as ArrayBuffer], { type: 'application/x-sqlite3' });
```

### 2. SettingsComponent Window Mocking

**Location**: `praxis/web-client/src/app/features/settings/settings.component.spec.ts`

**Issue**: `window.location` mocking requires `any` cast.

```typescript
// Fixed: Using BrowserService abstraction
this.browserService.reload();
```

---

## Implementation Steps

### 1. Fix SqliteService Types

- [x] Review `sql.js` type definitions
- [x] Update `exportDatabase` to use `Uint8Array.buffer`
- [x] Ensure `importDatabase` accepts proper Blob types

### 2. Create Window Service (if needed)

- [x] Created `BrowserService` (DI-based abstraction)

### 3. Update SettingsComponent Tests

- [x] Refactored to use `BrowserService`
- [x] Updated tests to mock `BrowserService`

### 4. Run Type Checker

- [x] Ran ESLint and Vitest

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Backlog tracking |
| [sqlite.service.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/services/sqlite.service.ts) | SQLite service |
| [settings.component.spec.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/settings/settings.component.spec.ts) | Settings tests |

---

## Project Conventions

- **Frontend Lint**: `cd praxis/web-client && npm run lint`
- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for conventions.

---

## On Completion

- [x] Commit changes with message: `fix(frontend): resolve type safety issues in SqliteService and Settings`
- [x] Update [quality_assurance.md](../../backlog/quality_assurance.md) - mark Frontend Type Safety complete
- [x] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [x] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
