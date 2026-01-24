# E2E-RUN-02: Run & Fix Protocol Execution E2E Tests

## Context

**Spec File**: `e2e/specs/03-protocol-execution.spec.ts`
**Feature**: Protocol running and monitoring
**Goal**: Run tests, fix failures, report visual issues

## Requirements

### Phase 1: Run Tests

```bash
npm run start:browser &
sleep 10
npx playwright test e2e/specs/03-protocol-execution.spec.ts --project=chromium --reporter=list
```

### Phase 2: Fix Failures

1. Analyze each failure
2. Check for OPFS-related async issues
3. Update selectors if needed
4. Add appropriate waits

### Phase 3: Visual Audit

Note during test runs:

1. Protocol setup UI clarity
2. Execution progress indicators
3. Error message presentation
4. Results display formatting

## Output

Create `protocol-execution-report.md` with:

- Test results summary
- Fixes applied
- Visual findings

## Acceptance Criteria

- [ ] All tests pass
- [ ] No flaky tests (run 3x)
- [ ] Visual findings documented
- [ ] Commit: `test(e2e): fix protocol execution tests`
