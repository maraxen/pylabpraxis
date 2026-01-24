# Jules Dispatch Log

**Dispatched**: $(date +"%Y-%m-%d %H:%M:%S")
**Total Tasks**: 26
**Dispatcher**: jules-dispatch-batch

## Session Tracking

| ID | Title | Session ID | Status | Priority | Category |
|:---|:------|:-----------|:-------|:---------|:---------|
| REFACTOR-01 | Convert relative imports → @core aliases | `DISPATCH_FAILED` | QUEUED | P2 | refactor |
| REFACTOR-02 | Convert relative imports → @features aliases | `DISPATCH_FAILED` | QUEUED | P2 | refactor |
| REFACTOR-03 | Convert relative imports → @shared aliases | `DISPATCH_FAILED` | QUEUED | P2 | refactor |
| SPLIT-01 | Decompose run-protocol.component.ts (1477 lines) | `DISPATCH_FAILED` | QUEUED | P2 | refactor |
| SPLIT-02 | Decompose playground.component.ts (1324 lines) | `DISPATCH_FAILED` | QUEUED | P2 | refactor |
| SPLIT-03 | Decompose data-visualization.component.ts (932 lines) | `DISPATCH_FAILED` | QUEUED | P2 | refactor |
| SPLIT-04 | Decompose scheduler.py (732 lines) | `DISPATCH_FAILED` | QUEUED | P2 | refactor |
| SPLIT-05 | Decompose plr_inspection.py (716 lines) | `DISPATCH_FAILED` | QUEUED | P2 | refactor |
| SPLIT-06 | Decompose resource_type_definition.py (701 lines) | `DISPATCH_FAILED` | QUEUED | P2 | refactor |
| E2E-AUDIT-01 | Audit E2E test coverage gaps | `DISPATCH_FAILED` | QUEUED | P1 | testing |
| E2E-NEW-01 | Create OPFS migration E2E tests | `DISPATCH_FAILED` | QUEUED | P1 | testing |
| E2E-NEW-02 | Create monitor detail E2E tests | `DISPATCH_FAILED` | QUEUED | P2 | testing |
| E2E-NEW-03 | Create workcell dashboard E2E tests | `DISPATCH_FAILED` | QUEUED | P2 | testing |
| E2E-RUN-01 | Run & fix asset management E2E tests | `DISPATCH_FAILED` | QUEUED | P1 | testing |
| E2E-RUN-02 | Run & fix protocol execution E2E tests | `DISPATCH_FAILED` | QUEUED | P1 | testing |
| E2E-RUN-03 | Run & fix browser persistence E2E tests | `DISPATCH_FAILED` | QUEUED | P1 | testing |
| E2E-VIZ-01 | Visual audit - Asset pages | `DISPATCH_FAILED` | QUEUED | P2 | visual |
| E2E-VIZ-02 | Visual audit - Run protocol pages | `DISPATCH_FAILED` | QUEUED | P2 | visual |
| E2E-VIZ-03 | Visual audit - Data & Playground | `DISPATCH_FAILED` | QUEUED | P2 | visual |
| E2E-VIZ-04 | Visual audit - Settings & Workcell | `DISPATCH_FAILED` | QUEUED | P2 | visual |
| JLITE-01 | Audit simulate-ghpages.sh directory structure | `DISPATCH_FAILED` | QUEUED | P1 | jupyterlite |
| JLITE-02 | Audit & fix theme CSS path doubling | `DISPATCH_FAILED` | QUEUED | P1 | jupyterlite |
| JLITE-03 | Fix Pyodide kernel auto-initialization | `DISPATCH_FAILED` | QUEUED | P1 | jupyterlite |
| OPFS-01 | Audit protocol running via Pyodide under OPFS | `DISPATCH_FAILED` | QUEUED | P2 | opfs |
| OPFS-02 | Review asset instantiation under OPFS | `DISPATCH_FAILED` | QUEUED | P2 | opfs |
| OPFS-03 | Review hardware discovery under OPFS | `DISPATCH_FAILED` | QUEUED | P2 | opfs |

---

## Summary

- **Dispatched**: 26
- **Skipped**: 0
- **Timestamp**: 2026-01-23 16:57:34

## Review Priority

Review sessions in this order:
1. **P1 Tasks** - Critical blockers and core functionality
2. **P1 Visual** - E2E runs that include visual audit
3. **P2 Tasks** - Refactoring and secondary features

## Next Steps

1. Monitor Jules dashboard for completed sessions
2. Use `jules remote list` to check status
3. Review completed sessions with `jules remote pull <session_id>`
4. Apply approved changes with `jules remote pull <session_id> --apply`
5. Update DEVELOPMENT_MATRIX.md with results
