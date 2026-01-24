# OPFS-02: Review Asset Instantiation Under OPFS

## Context

**Service**: `src/app/features/assets/services/asset.service.ts`
**Worker**: `src/app/core/workers/sqlite-opfs.worker.ts`
**Goal**: Verify asset CRUD operations work correctly with OPFS

## Background

Asset operations (create, read, update, delete) now use async repositories that go through the OPFS worker.

## Requirements

### Phase 1: Code Review

1. Read `asset.service.ts` - especially:
   - `createMachine()`
   - `createResource()`
   - Repository usage patterns
2. Verify all methods use `getAsyncRepositories()`
3. Check no legacy `save()` calls remain

### Phase 2: Trace Data Flow

1. User creates asset in UI
2. Service calls repository
3. Repository sends to worker
4. Worker writes to OPFS
5. Confirmation returns

Document any gaps or race conditions.

### Phase 3: Test

1. Start browser mode
2. Create a machine asset
3. Create a resource asset
4. Reload page
5. Verify both persist

### Phase 4: Document

Create `opfs-asset-review.md`:

```markdown
# Asset Instantiation Under OPFS

## Code Review
- [x] createMachine uses async repo
- [x] createResource uses async repo
- [ ] Found issue: [description]

## Data Flow
[Diagram or description]

## Test Results
| Operation | Status |
|-----------|--------|
| Create machine | ✅ |
| Create resource | ✅ |
| Persist on reload | ✅ |
| Edit asset | ✅ |
| Delete asset | ✅ |

## Recommendations
[Any improvements]
```

## Acceptance Criteria

- [ ] Code reviewed for OPFS compliance
- [ ] Data flow documented
- [ ] Manual tests pass
