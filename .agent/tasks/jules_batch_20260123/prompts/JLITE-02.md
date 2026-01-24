# JLITE-02: Audit & Potential Fix for Path Doubling in Theme CSS

## Context

**Issue**: Theme CSS returns 404 with doubled paths
**Example**: `assets/jupyterlite/assets/jupyterlite/build/themes/...`
**Severity**: P3 (visual only, functionality works)

## Background

The error suggests paths are being resolved incorrectly, with the base path prepended twice. This may be:

1. A config issue in `jupyter-lite.gh-pages.json`
2. A bug in `config-utils.js` path resolution
3. Already fixed but not verified

## Requirements

### Phase 1: Investigate Current State

1. Read `praxis/web-client/src/assets/jupyterlite/jupyter-lite.json`
2. Read `praxis/web-client/src/assets/jupyterlite/jupyter-lite.gh-pages.json`
3. Find and read `config-utils.js` or similar path resolver
4. Check for `fixOneRelativeUrl` or similar functions

### Phase 2: Test in Simulation

1. Build with `npm run build:gh-pages`
2. Run simulation
3. Open browser devtools → Network tab
4. Navigate to `/praxis/app/playground`
5. Check CSS/theme requests:
   - Are paths doubled?
   - Do they return 404?

### Phase 3: Decision

**If Issue Exists:**

1. Identify the code causing double-prepending
2. Fix the path resolution logic
3. Test fix in simulation
4. Commit: `fix(jupyterlite): resolve theme CSS path doubling`

**If Issue is Fixed:**

1. Document that it's resolved
2. Note what fixed it
3. Close as verified

## Files to Check

- `src/assets/jupyterlite/*.json`
- Any `config-utils.js` or path resolution files
- `playground.component.ts` - getLiteConfig()

## Acceptance Criteria

- [ ] Issue status clarified (exists or fixed)
- [ ] If exists: fix applied and tested
- [ ] If fixed: documented when/how
