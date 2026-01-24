# E2E-NEW-02: Create Monitor Detail E2E Tests

## Context

**Route**: `/app/monitor/:id`
**Component**: `run-detail.component.ts`
**Goal**: Add E2E coverage for run detail/monitoring views

## Requirements

### Test Scenarios

1. **Navigate to Run Detail**
   - From monitor list, click on a run
   - Verify detail view loads
   - Check URL contains run ID

2. **Detail View Content**
   - Verify run metadata displays
   - Check progress indicators
   - Verify action buttons present

3. **Live Updates** (if applicable)
   - Verify real-time status updates
   - Check log streaming

4. **Error States**
   - Navigate to invalid run ID
   - Verify error handling

### Test Setup

```typescript
import { test, expect } from '@playwright/test';
import { MonitorPage } from '../page-objects/monitor.page';

test.describe('Run Detail View', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Create a run to view
    // Navigate to /app/monitor
  });
  
  test('displays run details', async ({ page }) => {
    // Implementation
  });
});
```

## Acceptance Criteria

- [ ] New spec file: `e2e/specs/monitor-detail.spec.ts`
- [ ] Page object: `e2e/page-objects/monitor.page.ts`
- [ ] All tests pass
- [ ] Commit: `test(e2e): add monitor detail view coverage`

## Server Command

```bash
npm run start:browser
```
