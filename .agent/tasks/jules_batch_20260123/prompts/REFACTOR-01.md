# REFACTOR-01: Convert relative imports → @core aliases in core/

## Context

**Repository**: praxis/web-client
**Target Directory**: `src/app/core/` (excluding `api-generated/`)
**Path Aliases** (from `tsconfig.json`):

- `@core/*` → `src/app/core/*`
- `@features/*` → `src/app/features/*`
- `@shared/*` → `src/app/shared/*`
- `@env/*` → `src/environments/*`

## Requirements

1. Find all TypeScript files in `src/app/core/` (except `api-generated/`)
2. Convert relative imports like `from '../services/...'` or `from '../../shared/...'` to absolute path aliases:
   - `../services/foo` → `@core/services/foo`
   - `../../features/bar` → `@features/bar`
   - `../../shared/baz` → `@shared/baz`
   - `../../../environments/` → `@env/`
3. Preserve imports that stay within the same folder (e.g., `./sibling-file`)
4. Run `npm run build` to verify no compilation errors
5. Run existing tests to confirm no regressions

## Acceptance Criteria

- [ ] All relative imports traversing up (`../`) converted to aliases
- [ ] `npm run build` completes without errors
- [ ] No changes to `api-generated/` folder
- [ ] Commit with message: `refactor(core): convert relative imports to path aliases`

## Anti-Requirements

- Do NOT modify `src/app/core/api-generated/` (auto-generated code)
- Do NOT change the logic or functionality of any file
- Do NOT refactor unrelated code
