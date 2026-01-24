# OPFS-03: Review Hardware Discovery Under OPFS

## Context

**Service**: `src/app/core/services/hardware-discovery.service.ts`
**Size**: 858 lines
**Goal**: Verify hardware discovery works correctly with OPFS persistence

## Background

Hardware discovery involves:

1. Scanning for connected devices
2. Caching discovery results
3. Persisting user selections
4. Auto-reconnect logic

With OPFS migration, any persistence must use async patterns.

## Requirements

### Phase 1: Code Review

1. Read `hardware-discovery.service.ts`
2. Identify all persistence operations
3. Check for:
   - Direct localStorage usage (should avoid)
   - Repository calls (should be async)
   - Any sync file operations

### Phase 2: Test Scenarios

1. Start browser mode
2. Open hardware discovery dialog
3. Simulate device discovery (mock or real)
4. Save configuration
5. Reload page
6. Verify configuration persists

### Phase 3: Edge Cases

1. What happens with no devices?
2. What if device disconnects?
3. How is state recovered after crash?

### Phase 4: Document

Create `opfs-hardware-review.md`:

```markdown
# Hardware Discovery Under OPFS

## Persistence Points Found
1. [location]: [what is persisted]

## Compliance Check
- [ ] Uses async repositories
- [ ] No direct localStorage
- [ ] Error handling for OPFS failures

## Test Results
[Table of scenarios]

## Issues/Recommendations
[Findings]
```

## Acceptance Criteria

- [ ] All persistence points identified
- [ ] OPFS compliance verified
- [ ] Test scenarios documented
