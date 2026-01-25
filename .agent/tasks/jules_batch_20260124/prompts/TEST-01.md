# TEST-01: Add Unit Tests for name-parser.ts

## Context

**Source File**: `praxis/web-client/src/app/shared/utils/name-parser.ts`
**Test File**: `praxis/web-client/src/app/shared/utils/name-parser.spec.ts` (create or expand)
**Framework**: Vitest (check existing spec files for patterns)

## Requirements

Create comprehensive unit tests covering:

1. **All public functions** - Test every exported function
2. **Happy path** - Normal inputs produce expected outputs
3. **Edge cases**:
   - Empty strings
   - Null/undefined inputs (if allowed)
   - Special characters
   - Very long strings
   - Unicode characters

4. **Follow existing patterns** - Look at `linked-selector.service.spec.ts` for test structure

Example test structure:

```typescript
import { describe, it, expect } from 'vitest';
import { parseName, formatName } from './name-parser';

describe('name-parser', () => {
  describe('parseName', () => {
    it('should parse standard name format', () => {
      expect(parseName('John Doe')).toEqual({ first: 'John', last: 'Doe' });
    });

    it('should handle empty string', () => {
      expect(parseName('')).toEqual({ first: '', last: '' });
    });
  });
});
```

Do NOT:

- Modify the source file
- Add mock data to other files
- Change test configuration

## Acceptance Criteria

- [ ] Test file exists at `name-parser.spec.ts`
- [ ] All public functions have at least 2 test cases
- [ ] Edge cases covered
- [ ] `npm test -- --filter=name-parser` passes
