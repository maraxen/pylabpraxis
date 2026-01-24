# REFACTOR-02: Convert relative imports → aliases in features/

## Context

**Repository**: praxis/web-client
**Target Directory**: `src/app/features/`
**Path Aliases** (from `tsconfig.json`):

- `@core/*` → `src/app/core/*`
- `@features/*` → `src/app/features/*`
- `@shared/*` → `src/app/shared/*`
- `@env/*` → `src/environments/*`
- `@api/*` → `src/app/core/api-generated/*`

## Requirements

1. Find all TypeScript files in `src/app/features/`
2. Convert relative imports that traverse up to other modules:
   - `../../core/services/x` → `@core/services/x`
   - `../../shared/components/y` → `@shared/components/y`
   - `../../../environments/` → `@env/`
   - Cross-feature imports `../../other-feature/` → `@features/other-feature/`
3. Keep intra-feature relative imports (same feature module)
4. Run `npm run build` to verify
5. Run `npm test` to confirm no regressions

## Acceptance Criteria

- [ ] All imports to @core, @shared, @env converted
- [ ] `npm run build` passes
- [ ] `npm test` passes (or documents pre-existing failures)
- [ ] Commit: `refactor(features): convert relative imports to path aliases`

## Anti-Requirements

- Do NOT change file structure or logic
- Do NOT modify exports or public API
