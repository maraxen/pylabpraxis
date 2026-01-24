# OPFS-01: Audit Protocol Running via Pyodide Under OPFS

## Context

**Feature**: Running protocols in browser mode via Pyodide
**Change**: OPFS migration changed how data is persisted
**Goal**: Verify protocol execution works correctly with OPFS backend

## Background

With the OPFS migration:

1. SQLite database is now in OPFS (not IndexedDB)
2. Repositories are now async
3. Playground/REPL interacts with this storage

## Requirements

### Phase 1: Trace Integration Points

1. How does Pyodide access persisted data?
2. Are there direct file system operations?
3. Does the kernel use the same SQLite as the app?

### Phase 2: Test Scenarios

1. Create data in the app (asset, protocol)
2. Open playground
3. Try to access that data from Python
4. Run a protocol that reads/writes data
5. Verify persistence after reload

### Phase 3: Document Findings

Create `opfs-pyodide-audit.md`:

```markdown
# OPFS + Pyodide Integration Audit

## Integration Architecture
[How Pyodide accesses OPFS data]

## Test Results
| Scenario | Result | Notes |
|----------|--------|-------|
| Read asset from Pyodide | ✅ Pass | Uses message passing |
| Write result to storage | ⚠️ Issue | [description] |

## Issues Found
1. [Description]
   Impact: [severity]
   Recommendation: [fix]

## Recommendations
[Ordered list]
```

## Acceptance Criteria

- [ ] Integration points documented
- [ ] Test scenarios executed
- [ ] Any issues identified with recommendations
