# Agent Prompt: API Client Import Fixes

Examine `.agents/README.md` for development context.

**Status:** 🟢 Complete
**Priority:** P1
**Batch:** [260113](./README.md)
**Backlog Reference:** [frontend_schema_sync.md](../../backlog/frontend_schema_sync.md)

---

## 1. The Task

Several services have incorrect import paths or import non-existent types from the API-generated client. These issues prevent the frontend from compiling.

**User Value:** Fix import errors to restore frontend compilation.

---

## 2. Technical Implementation Strategy

**Identified Issues:**

| File | Issue | Fix |
|:-----|:------|:----|
| `playground-runtime.service.ts` | Wrong import path for `ReplService` | Change `./api-generated/...` to `../api-generated/...` |
| `auth.service.ts` | Imports `UserResponse` which doesn't exist | Change to `UserRead` |

**Import Path Structure:**

- Services in `core/services/` need `../api-generated/...`  
- Services in `features/*/services/` need `../../../core/api-generated/...`

**Type Renames:**

- `UserResponse` → `UserRead` (renamed in OpenAPI spec)

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/services/playground-runtime.service.ts` | Fix ReplService import path |
| `praxis/web-client/src/app/features/auth/services/auth.service.ts` | Fix UserResponse → UserRead |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/api-generated/services/ReplService.ts` | Correct ReplService location |
| `praxis/web-client/src/app/core/api-generated/models/UserRead.ts` | Correct user model |
| `praxis/web-client/src/app/core/api-generated/services/AuthenticationService.ts` | Shows UserRead usage |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- Import paths are relative; ensure correct depth.
- Do not modify generated files in `api-generated/`.

---

## 5. Implementation Details

### Fix 1: playground-runtime.service.ts (Line 7)

**Before:**

```typescript
import { ReplService } from './api-generated/services/ReplService';
```

**After:**

```typescript
import { ReplService } from '../api-generated/services/ReplService';
```

### Fix 2: auth.service.ts (Line 9)

**Before:**

```typescript
import { UserResponse } from '../../../core/api-generated/models/UserResponse';
```

**After:**

```typescript
import { UserRead } from '../../../core/api-generated/models/UserRead';
```

Also update the return type on line 36:

**Before:**

```typescript
getCurrentUser(): Observable<UserResponse> {
```

**After:**

```typescript
getCurrentUser(): Observable<UserRead> {
```

---

## 6. Verification Plan

**Definition of Done:**

1. No import errors for `ReplService` or `UserResponse`:

   ```bash
   cd praxis/web-client && npm run build 2>&1 | grep -E "(Cannot find module|has no exported member)"
   ```

   Expected: No errors for ReplService or UserResponse.

2. Type check passes for these files:

   ```bash
   cd praxis/web-client && npx tsc --noEmit 2>&1 | grep -E "(playground-runtime|auth\.service)"
   ```

   Expected: No output (no errors).

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status (Phase 2/3 tasks)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- [ReplService.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/api-generated/services/ReplService.ts)
- [UserRead.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/api-generated/models/UserRead.ts)
