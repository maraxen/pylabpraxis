# REFACTOR-03: Convert relative imports → aliases in shared/

## Context

**Repository**: praxis/web-client
**Target Directory**: `src/app/shared/`
**Path Aliases**:

- `@core/*` → `src/app/core/*`
- `@features/*` → `src/app/features/*`
- `@shared/*` → `src/app/shared/*`
- `@env/*` → `src/environments/*`

## Requirements

1. Find all TypeScript files in `src/app/shared/`
2. Convert relative imports that go outside shared:
   - `../../core/` → `@core/`
   - `../../environments/` → `@env/`
3. Keep relative imports within shared (for component-local files)
4. Verify with `npm run build`

## Acceptance Criteria

- [ ] All external-pointing relative imports converted
- [ ] `npm run build` passes
- [ ] Commit: `refactor(shared): convert relative imports to path aliases`

## Anti-Requirements

- Do NOT modify component logic
- Do NOT change file structure
