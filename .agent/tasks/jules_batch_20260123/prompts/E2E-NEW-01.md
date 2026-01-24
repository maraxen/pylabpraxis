# E2E-NEW-01: Create OPFS Migration E2E Tests

## Context

**Related Spec**: `e2e/specs/05-opfs-persistence.spec.ts`
**Feature**: OPFS-based SQLite persistence (browser mode)
**Recent Migration**: Moved from IndexedDB to OPFS

## Background

The application recently migrated from IndexedDB-backed sql.js to OPFS-native SQLite WASM. Tests need to verify:

1. Data persists across page reloads
2. Data survives browser close/reopen
3. Migration from old storage works (if applicable)
4. Large data sets handle correctly

## Requirements

### Test Scenarios to Create/Update

1. **Basic Persistence Test**
   - Create asset in browser mode
   - Reload page
   - Verify asset still exists

2. **Cross-Session Persistence**
   - Create data, close browser context
   - Reopen, verify data persists

3. **Data Integrity**
   - Create multiple related entities
   - Verify relationships survive reload

4. **Error Recovery**
   - Simulate storage quota issues
   - Verify graceful degradation

### Test Configuration

```typescript
// Use browser mode startup
webServer: {
  command: 'npm run start:browser',
  port: 4200,
  reuseExistingServer: true
}
```

## Acceptance Criteria

- [ ] All persistence scenarios covered
- [ ] Tests pass with `npx playwright test e2e/specs/*opfs*`
- [ ] No flaky failures (run 3x to confirm)
- [ ] Commit: `test(e2e): add comprehensive OPFS persistence tests`

## Skills to Use

- `playwright-skill` - For test patterns
- Refer to existing `05-opfs-persistence.spec.ts` for patterns

## Anti-Requirements

- Do NOT test Docker/backend mode in these tests
- Do NOT modify core OPFS implementation
