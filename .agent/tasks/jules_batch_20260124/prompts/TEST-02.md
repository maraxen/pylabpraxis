# TEST-02: Expand Unit Tests for linked-selector.service

## Context

**Source File**: `praxis/web-client/src/app/shared/services/linked-selector.service.ts`
**Test File**: `praxis/web-client/src/app/shared/services/linked-selector.service.spec.ts` (exists)
**Framework**: Vitest

## Requirements

Review the existing test file and expand coverage:

1. **Analyze current coverage** - Identify untested methods/branches
2. **Add missing test cases** for:
   - Observable emissions
   - State changes
   - Error conditions
   - Cleanup/disposal

3. **Test Observable patterns**:

```typescript
import { firstValueFrom } from 'rxjs';

it('should emit selected value', async () => {
  service.select(item);
  const result = await firstValueFrom(service.selected$);
  expect(result).toBe(item);
});
```

1. **Test edge cases**:
   - Selecting null/undefined
   - Multiple rapid selections
   - Unsubscribe behavior

Do NOT:

- Modify the service implementation
- Add new dependencies
- Change test configuration

## Acceptance Criteria

- [ ] Coverage increased for linked-selector.service
- [ ] All Observable emissions tested
- [ ] Edge cases covered
- [ ] All tests pass
