# E2E-RUN-01: Run & Fix Asset Management E2E Tests

## Context

**Spec File**: `e2e/specs/02-asset-management.spec.ts`
**Feature**: Asset creation, editing, deletion
**Goal**: Run tests, fix failures, report visual issues

## Requirements

### Phase 1: Run Tests

```bash
npm run start:browser &
sleep 10
npx playwright test e2e/specs/02-asset-management.spec.ts --project=chromium --reporter=list
```

### Phase 2: Analyze Failures

For each failure:

1. Capture screenshot at failure point
2. Check console for errors
3. Identify root cause (selector change, timing, OPFS migration impact)

### Phase 3: Fix Tests

1. Update selectors if DOM changed
2. Add waits for async operations
3. Fix OPFS-related issues (async repositories)

### Phase 4: Visual Audit

While running tests, note:

1. UI inconsistencies
2. Alignment issues
3. Missing states (loading, empty, error)
4. Accessibility concerns

## Output

Create `asset-management-report.md`:

```markdown
# Asset Management E2E Report

## Test Results
- Total: X
- Passed: Y
- Failed: Z

## Fixes Applied
1. [file:line] - Description

## Visual Findings
1. **Issue**: Button misalignment on create dialog
   **Severity**: Low
   **Screenshot**: [path]
```

## Skills to Use

- `playwright-skill` - Test patterns
- `ui-ux-pro-max` - Visual audit criteria
- `designer.md` - Design evaluation

## Acceptance Criteria

- [ ] All tests pass
- [ ] Report generated with findings
- [ ] Commit: `test(e2e): fix asset management tests post-OPFS migration`
