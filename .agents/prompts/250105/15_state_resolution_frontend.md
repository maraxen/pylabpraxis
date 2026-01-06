# Prompt 15: State Resolution Frontend Dialog

Create the State Resolution Dialog for user interaction when errors occur.

## Tasks

1. Create `StateResolutionDialogComponent`:
   - Shows failed operation details
   - Lists each uncertain state with current value
   - Provides input field for user to specify actual value
   - Quick actions: "Confirm as-is", "Reset to previous"
   - Notes field for audit

2. Create `AffectedStateViewerComponent`:
   - Table view of affected resources
   - Before/After state columns

3. Integrate with ExecutionService error handling:
   - When error detected, open resolution dialog
   - After resolution, allow Resume or Abort

4. Store resolution in browser mode (SqliteService) for audit

## Files to Create

- `praxis/web-client/src/app/features/execution-monitor/dialogs/state-resolution-dialog/`
- `praxis/web-client/src/app/features/execution-monitor/components/affected-state-viewer/`

## Files to Modify

- `praxis/web-client/src/app/core/services/execution.service.ts`

## Reference

- `.agents/backlog/error_handling_state_resolution.md`
