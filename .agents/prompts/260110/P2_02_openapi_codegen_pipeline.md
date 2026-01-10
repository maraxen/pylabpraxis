# Agent Prompt: OpenAPI Codegen Pipeline Setup

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260110](./README.md)
**Backlog Reference:** [sqlmodel_codegen_refactor.md](../../backlog/sqlmodel_codegen_refactor.md)
**Phase:** 1.2 — Frontend OpenAPI Codegen Pipeline
**Parallelizable:** ✅ Can run in parallel with P2_01

---

## 1. The Task

Set up the frontend OpenAPI code generation pipeline that will automatically generate TypeScript API client code from the FastAPI backend's OpenAPI schema. This enables automatic frontend type safety based on backend models.

**User Value:** Eliminates manually maintained TypeScript interfaces that can drift out of sync with the backend. Changes to backend models automatically propagate to frontend types.

---

## 2. Technical Implementation Strategy

### Current State

- `scripts/generate_openapi.py` already generates `openapi.json` to `praxis/web-client/src/assets/api/openapi.json`
- Frontend has no codegen tooling configured
- TypeScript interfaces are manually maintained in feature modules

### Target Architecture

```
Backend (FastAPI)
       ↓
scripts/generate_openapi.py
       ↓
praxis/web-client/src/assets/api/openapi.json
       ↓
npm run generate-api
       ↓
praxis/web-client/src/app/core/api-generated/
   ├── index.ts
   ├── models/
   │   ├── AssetResponse.ts
   │   ├── MachineResponse.ts
   │   └── ...
   ├── services/
   │   ├── DefaultService.ts (or grouped by tag)
   │   └── ...
   └── core/
       ├── ApiError.ts
       ├── CancelablePromise.ts
       └── ...
```

### Tool Selection

Use `openapi-typescript-codegen` for initial setup (simpler, framework-agnostic):

```bash
npx openapi-typescript-codegen \
  --input ./src/assets/api/openapi.json \
  --output ./src/app/core/api-generated \
  --client fetch \
  --useUnionTypes
```

**Alternative for later:** `orval` if Angular-specific RxJS observables are needed.

### Package.json Script

```json
{
  "scripts": {
    "generate-api": "openapi-typescript-codegen --input ./src/assets/api/openapi.json --output ./src/app/core/api-generated --client fetch --useUnionTypes",
    "prebuild": "npm run generate-api"
  }
}
```

### Generator Ignore File

Create `.openapi-generator-ignore` to preserve custom overrides:

```
# Keep manual customizations
src/app/core/api-generated/custom/**
```

---

## 3. Context & References

**Primary Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/api-generated/` | Directory for generated code |
| `praxis/web-client/.openapi-generator-ignore` | Ignore patterns for codegen |

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/package.json` | Add codegen script and devDependency |
| `scripts/generate_openapi.py` | Ensure output path is correct |

**Reference Files (Read-Only):**

| Path | Pattern Source |
|:-----|:---------------|
| `praxis/web-client/src/assets/api/openapi.json` | Existing schema (if present) |
| `praxis/backend/main.py` | FastAPI app for schema generation |
| `praxis/web-client/tsconfig.json` | TypeScript config for path resolution |
| `praxis/web-client/src/app/features/assets/models/` | Existing manual interfaces (to replace later) |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular/Node operations.
- **Frontend Path**: `praxis/web-client`
- **Node Version**: Check `.nvmrc` or `package.json` engines if present
- **TypeScript**: Generated code must compile with existing `tsconfig.json`
- **Do NOT delete existing manual interfaces yet** — that's Phase 6

### Sharp Bits / Technical Debt

1. **OpenAPI schema freshness**: The generated TypeScript is only as fresh as the last `generate_openapi.py` run. Consider adding pre-commit hook.
2. **Enum handling**: OpenAPI codegen may generate string unions instead of TS enums. Verify enum representation.
3. **Nullable types**: Ensure `--useUnionTypes` generates proper `| null` unions.
4. **Import paths**: Generated code may need barrel exports configured in `tsconfig.json` paths.

---

## 5. Verification Plan

**Definition of Done:**

1. OpenAPI schema generates successfully:
   ```bash
   cd /Users/mar/Projects/pylabpraxis
   uv run python scripts/generate_openapi.py
   ```

2. TypeScript client generates without errors:
   ```bash
   cd praxis/web-client
   npm install
   npm run generate-api
   ```

3. Generated TypeScript compiles:
   ```bash
   cd praxis/web-client
   npx tsc --noEmit
   ```

4. Angular build succeeds:
   ```bash
   cd praxis/web-client
   npm run build
   ```

5. No lint errors in generated code (or generator is excluded from lint):
   ```bash
   cd praxis/web-client
   npm run lint -- --fix
   ```

---

## 6. Implementation Steps

1. **Generate fresh OpenAPI schema**:
   ```bash
   uv run python scripts/generate_openapi.py
   ```
   Verify `praxis/web-client/src/assets/api/openapi.json` exists and is valid JSON.

2. **Install codegen tool**:
   ```bash
   cd praxis/web-client
   npm install --save-dev openapi-typescript-codegen
   ```

3. **Add npm script** to `package.json`:
   - Add `"generate-api"` script with appropriate flags
   - Consider adding `"prebuild": "npm run generate-api"` for auto-generation

4. **Create output directory**:
   ```bash
   mkdir -p praxis/web-client/src/app/core/api-generated
   ```

5. **Run initial generation**:
   ```bash
   npm run generate-api
   ```

6. **Review generated output**:
   - Check `models/` for response types matching Pydantic models
   - Check `services/` for API methods matching FastAPI routes
   - Verify enum representations

7. **Configure ESLint exclusion** (if needed):
   - Add `src/app/core/api-generated/**` to `.eslintignore` or `eslint.config.js`

8. **Create `.openapi-generator-ignore`**:
   - Add patterns for any files that should not be overwritten

9. **Update `tsconfig.json` paths** (if needed):
   - Add `"@api/*": ["src/app/core/api-generated/*"]` for clean imports

10. **Verify full build**:
    ```bash
    npm run build
    ```

---

## On Completion

- [ ] Commit changes with message: `feat(frontend): add OpenAPI TypeScript codegen pipeline`
- [ ] Update backlog item status in `sqlmodel_codegen_refactor.md` (Phase 1.2 → Done)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- `.agents/backlog/sqlmodel_codegen_refactor.md` - Full migration plan
- [openapi-typescript-codegen](https://github.com/ferdikoomen/openapi-typescript-codegen)
- [orval (alternative)](https://orval.dev/) - For Angular/RxJS integration if needed later
