# Task: Fix Protocol Execution Start in Browser Mode

**Dispatch Mode**: 🧠 **Planning Mode** (critical system flow fix)

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P1 item "Start Execution Not Working"
- `.agents/backlog/browser_mode_issues.md` - Issue #3

## Problem

The "Run" button does not successfully start protocol execution in browser mode. This requires a deep dive into the simulation/execution pipeline.

## Implementation

1. Trace the `ExecutionService` flow from the "Run" button click.
2. Identify where the communication with the `PythonRuntimeService` (Pyodide worker) fails.
3. Ensure all necessary assets and parameters are correctly passed to the execution context.
4. Add robust unit and E2E tests covering this flow.

## Testing

1. E2E test: Select protocol, selection assets, and hit "Run" - verify execution starts and progress is reported.
2. Add regression tests to prevent future breakage of this core flow.

## Definition of Done

- [ ] Protocols consistently start execution in browser mode.
- [ ] Full E2E coverage for the execution flow.
- [ ] Update `.agents/backlog/browser_mode_issues.md` - Mark #3 as ✅ Complete
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "Start Execution Not Working" as complete

## Files Likely Involved

- `praxis/web-client/src/app/core/services/execution.service.ts`
- `praxis/web-client/src/app/core/services/python-runtime.service.ts`
- `praxis/web-client/src/app/features/run-protocol/`
