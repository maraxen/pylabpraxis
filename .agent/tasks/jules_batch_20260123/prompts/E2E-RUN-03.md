# E2E-RUN-03: Run & Fix Browser Persistence E2E Tests

## Context

**Spec Files**:

- `e2e/specs/04-browser-persistence.spec.ts`
- `e2e/specs/05-opfs-persistence.spec.ts`
**Feature**: Data persistence in browser mode
**Goal**: Ensure persistence tests work with OPFS migration

## Background

The OPFS migration changed:

1. Storage backend from IndexedDB to OPFS
2. Repository pattern from sync to async
3. Worker architecture for SQLite operations

## Requirements

### Phase 1: Run Tests

```bash
npm run start:browser &
sleep 10
npx playwright test e2e/specs/04-browser-persistence.spec.ts e2e/specs/05-opfs-persistence.spec.ts --project=chromium --reporter=list
```

### Phase 2: Diagnose Failures

Common OPFS-related issues:

1. **Timing**: Async operations need proper waits
2. **Selectors**: OPFS toggle may have changed/removed
3. **Seeding**: Database seeding works differently

### Phase 3: Fix Tests

1. Update to use async repository patterns
2. Remove references to removed OPFS toggle (now always enabled)
3. Fix seeding expectations

## Key Files to Reference

- `src/app/core/services/sqlite/sqlite.service.ts`
- `src/app/core/workers/sqlite-opfs.worker.ts`
- `src/app/core/db/async-repositories.ts`

## Acceptance Criteria

- [ ] Both spec files pass
- [ ] Tests verify actual OPFS persistence
- [ ] Commit: `test(e2e): update persistence tests for OPFS-only mode`
