# Agent Prompt: 13_frontend_type_safety

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
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
// Current (with any cast):
const blob = new Blob([data as any], { type: 'application/octet-stream' });

// Fix: Verify sql.js types and use proper typing
import type { Database } from 'sql.js';
const data: Uint8Array = this.db.export();
const blob = new Blob([data.buffer], { type: 'application/octet-stream' });
```

### 2. SettingsComponent Window Mocking

**Location**: `praxis/web-client/src/app/features/settings/settings.component.spec.ts`

**Issue**: `window.location` mocking requires `any` cast.

```typescript
// Current (with any cast):
(window as any).location = { reload: jest.fn() };

// Fix: Use DI token or proper mocking strategy
// Option 1: WINDOW injection token
// Option 2: Location service abstraction
```

---

## Implementation Steps

### 1. Fix SqliteService Types

- Review `sql.js` type definitions
- Update `exportDatabase` to use `Uint8Array.buffer`
- Ensure `importDatabase` accepts proper Blob types

### 2. Create Window Service (if needed)

```typescript
// window.service.ts
@Injectable({ providedIn: 'root' })
export class WindowService {
  get location(): Location { return window.location; }
  reload(): void { window.location.reload(); }
}
```

### 3. Update SettingsComponent Tests

Use the service or proper DI mocking instead of direct window mutation.

### 4. Run Type Checker

```bash
cd praxis/web-client && npm run lint
```

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

- [ ] Commit changes with message: `fix(frontend): resolve type safety issues in SqliteService and Settings`
- [ ] Update [quality_assurance.md](../../backlog/quality_assurance.md) - mark Frontend Type Safety complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
