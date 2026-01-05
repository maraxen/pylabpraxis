# Task: Improve REPL Error Messages

**Dispatch Mode**: 🧠 **Planning Mode** (backend + frontend debugging)

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P2 item "REPL Error Handling"
- `.agents/backlog/browser_mode_issues.md` - Issue #15

## Problem

When Python errors occur in the REPL, users see an uninformative "python" error instead of the full traceback.

## Implementation

1. **Browser Mode**: Update `python.worker.ts` to use `traceback.format_exc()` when catching exceptions in Pyodide.
2. **Production Mode**: Update backend REPL service to ensure exceptions captured include full traceback strings.
3. Ensure stderr is correctly routed and styled (red) in the frontend xterm UI.

## Testing

1. Trigger known errors (e.g., `1/0`, `undefined_variable`) and verify full traceback is visible.
2. Verify formatting remains clean and readable.

## Definition of Done

- [ ] Python tracebacks display full error type, message, and line numbers.
- [ ] Errors are visually distinct (red) in the REPL output.
- [ ] Update `.agents/backlog/browser_mode_issues.md` - Mark #15 as ✅ Complete
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "REPL Error Handling" as complete

## Files Likely Involved

- `praxis/web-client/src/app/features/repl/python.worker.ts`
- `praxis/backend/services/repl_service.py`
