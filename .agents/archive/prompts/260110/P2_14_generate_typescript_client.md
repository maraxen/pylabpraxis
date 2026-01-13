# Agent Prompt: Generate and Integrate TypeScript Client

Examine `.agents/README.md` for development context.

**Status:** 🟡 Partially Completed (Generation Done, Migration Deferred)
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 6.1 — Frontend Migration: Generate TypeScript Client
**Parallelizable:** ❌ Sequential — Requires Phase 5 (CRUD services updated)

---

## 1. The Task

Generate the TypeScript API client using the OpenAPI codegen pipeline (set up in Phase 1.2) and integrate it with the existing Angular frontend. Delete manual TypeScript interfaces that are now auto-generated.

**User Value:** Frontend types automatically match backend schemas, eliminating manual synchronization.

---

## 2. Technical Implementation Strategy

### Prerequisites

- Phase 1.2 complete (codegen pipeline set up)
- Phase 5 complete (all API routers using SQLModel)
- OpenAPI schema reflects unified models

### Generation Flow

```bash
# 1. Generate fresh OpenAPI schema from updated backend
cd /Users/mar/Projects/pylabpraxis
uv run python scripts/generate_openapi.py

# 2. Generate TypeScript client
cd praxis/web-client
npm run generate-api

# 3. Verify compilation
npx tsc --noEmit
```

### Generated Structure

```
praxis/web-client/src/app/core/api-generated/
├── index.ts                    # Barrel export
├── core/
│   ├── ApiError.ts
│   ├── ApiRequestOptions.ts
│   ├── ApiResult.ts
│   ├── CancelablePromise.ts
│   └── request.ts
├── models/
│   ├── AssetRead.ts           # Generated from AssetRead SQLModel
│   ├── AssetCreate.ts
│   ├── AssetUpdate.ts
│   ├── MachineRead.ts
│   ├── MachineCreate.ts
│   ├── ResourceRead.ts
│   └── ...                     # All response/request models
└── services/
    ├── DefaultService.ts       # Or grouped by API tags
    └── ...
```

### Manual Interfaces to Delete

These will be replaced by generated types:

| Manual File | Generated Replacement |
|:------------|:---------------------|
| `features/assets/models/asset.models.ts` | `api-generated/models/AssetRead.ts` |
| `features/protocols/models/protocol.models.ts` | `api-generated/models/ProtocolRunRead.ts` |
| `features/assets/models/machine.models.ts` | `api-generated/models/MachineRead.ts` |
| `features/assets/models/resource.models.ts` | `api-generated/models/ResourceRead.ts` |

### Import Path Configuration

Update `tsconfig.json` for clean imports:

```json
{
  "compilerOptions": {
    "paths": {
      "@api/*": ["src/app/core/api-generated/*"],
      "@api": ["src/app/core/api-generated/index.ts"]
    }
  }
}
```

Usage:

```typescript
import { AssetRead, MachineRead } from '@api';
// or
import { AssetRead } from '@api/models/AssetRead';
```

---

## 3. Context & References

**Primary Files to Create/Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/api-generated/` | Generated TypeScript client |
| `praxis/web-client/tsconfig.json` | Add @api path alias |

**Files to Delete (after verification):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/models/asset.models.ts` | Manual interfaces |
| `praxis/web-client/src/app/features/protocols/models/protocol.models.ts` | Manual interfaces |
| Other manual model files | As identified during audit |

**Files to Update (imports):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/` | Update imports to @api |
| `praxis/web-client/src/app/features/protocols/` | Update imports to @api |
| Other feature modules | As needed |

**Reference Files:**

| Path | Pattern Source |
|:-----|:---------------|
| `praxis/web-client/src/assets/api/openapi.json` | Generated OpenAPI schema |
| `praxis/web-client/package.json` | npm scripts |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular/Node operations.
- **Frontend Path**: `praxis/web-client`
- **Do NOT delete manual interfaces until imports are updated**
- **Verify build succeeds at each step**

### Sharp Bits / Technical Debt

1. **Enum handling**: Generated enums may differ from manual ones (string unions vs TS enums)
2. **Nullable types**: Verify `| null` vs `| undefined` handling
3. **Date types**: OpenAPI dates may become strings - may need transforms
4. **Circular imports**: Watch for generated index.ts causing issues

---

## 5. Verification Plan

**Definition of Done:**

1. OpenAPI schema is fresh:

   ```bash
   uv run python scripts/generate_openapi.py
   ls -la praxis/web-client/src/assets/api/openapi.json
   ```

2. TypeScript client generates:

   ```bash
   cd praxis/web-client
   npm run generate-api
   ls -la src/app/core/api-generated/
   ```

3. Generated code compiles:

   ```bash
   cd praxis/web-client
   npx tsc --noEmit
   ```

4. Angular build succeeds:

   ```bash
   cd praxis/web-client
   npm run build
   ```

5. Manual interfaces deleted and imports updated:

   ```bash
   # After updating all imports
   npm run build
   npm run lint
   ```

---

## 6. Implementation Steps

1. **Generate fresh OpenAPI schema**:

   ```bash
   cd /Users/mar/Projects/pylabpraxis
   uv run python scripts/generate_openapi.py
   ```

2. **Run TypeScript codegen**:

   ```bash
   cd praxis/web-client
   npm run generate-api
   ```

3. **Inspect generated models**:
   - Check `api-generated/models/` for expected types
   - Compare with manual interfaces
   - Note any naming differences

4. **Add @api path alias**:
   - Update `tsconfig.json` paths
   - Update `tsconfig.app.json` if needed

5. **Create migration plan for each feature**:
   - List files importing manual interfaces
   - Plan import replacement

6. **Update assets feature**:

   ```bash
   # Find files importing manual models
   grep -r "from.*asset.models" src/app/features/assets/
   ```

   - Update imports to `@api`
   - Verify types match

7. **Update protocols feature**:
   - Similar process

8. **Update remaining features**:
   - Similar process

9. **Delete manual interface files**:

   ```bash
   rm src/app/features/assets/models/asset.models.ts
   # etc.
   ```

10. **Final verification**:

    ```bash
    npm run build
    npm run lint
    npm test
    ```

---

## 7. Import Migration Example

**Before** (manual interface):

```typescript
// src/app/features/assets/components/asset-list.component.ts
import { Asset, Machine, Resource } from '../models/asset.models';
```

**After** (generated):

```typescript
// src/app/features/assets/components/asset-list.component.ts
import { AssetRead, MachineRead, ResourceRead } from '@api';
// Note: names may have changed (Asset → AssetRead)
```

---

## On Completion

- [ ] Commit changes with message: `feat(frontend): integrate generated TypeScript API client`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 6.1 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
- `P2_02_openapi_codegen_pipeline.md` - Codegen setup (prerequisite)
