# Mock Protocols Removal Plan

**Status**: Proposed
**Task**: Remove default mock protocols and runs from Browser Mode database.

## Goal Description

The current Browser Mode database is seeded with "Mock Protocols" (e.g., "Daily System Maintenance", "Cell Culture Feed") and associated "Mock Runs" via `sqlite.service.ts` and `browser-mode.interceptor.ts`. These mocks do not correspond to real Python protocol files in the repository and create confusion. The goal is to remove these mocks so that only real protocols (discovered by `generate_browser_db.py`) appear in the application, and the run history accurately reflects the user's actions.

## User Review Required
>
> [!WARNING]
> This change will **remove all pre-seeded default runs** ("Recent Runs") from the Browser Mode initial state. The run history will start empty for new users/sessions.

## Proposed Changes

### Core Services

#### [MODIFY] [sqlite.service.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/services/sqlite.service.ts)

- Remove imports of `MOCK_PROTOCOLS` and `MOCK_PROTOCOL_RUNS`.
- Update `seedDefaultRuns()` method to remove the logic that inserts these mock records.
- The method will be emptied (keeping the function signature if needed) to stop seeding fake runs.

### Execution Feature

#### [MODIFY] [execution.service.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/services/execution.service.ts)

- Remove import of `MOCK_PROTOCOLS`.
- Remove the fallback logic that searches `MOCK_PROTOCOLS` if a protocol is not found in the database.

### Interceptors

#### [MODIFY] [browser-mode.interceptor.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/interceptors/browser-mode.interceptor.ts)

- Remove `MOCK_PROTOCOL_RUNS` import.
- **Refactor `/protocols/runs/queue` handler**:
  - Replace mock array filtering with `sqliteService.getProtocolRuns()`.
  - Filter using RxJS (e.g., `status` in `['PENDING', 'PREPARING', 'QUEUED', 'RUNNING']`).
  - **Return proper empty paginated response** when no runs exist:

    ```typescript
    return of(new HttpResponse({
      status: 200,
      body: {
        items: [],
        total: 0,
        page: 1,
        size: 50
      }
    }));
    ```

  - Enrich the response with `protocol_name` (fetched from `sqliteService.getProtocols()` or by joining data) if required by the UI.
- **Refactor `/protocols/runs/records` handler**:
  - Replace mock array mapping with `sqliteService.getProtocolRuns()`.
  - Ensure the response format matches the expected schemas (including `duration_ms` calculation if needed).
  - Return proper empty paginated response structure (same as above).
- **Refactor `/protocols/runs/records/:id` handler**:
  - Use `sqliteService.getProtocolRun(id)` instead of searching the mock array.
  - Return 404 if run not found.

### assets/browser-data

#### [DELETE] [protocols.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/assets/browser-data/protocols.ts)

- File containing the mock protocol definitions.

#### [DELETE] [protocol-runs.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/assets/browser-data/protocol-runs.ts)

- File containing the mock protocol runs (which depend on the mock protocols).

## Verification Plan

### Automated

1. **Build Check**: Run `npm run build` in `praxis/web-client` to ensure all references to the deleted files are removed and no build errors occur.
2. **Lint**: Run code cleanup/linting to ensure unused imports are removed.

### Manual Verification

1. **Reset Database**: Load Browser Mode with `?resetdb=1` to force a re-initialization of the database.
2. **Verify Protocol Library**:
   - Confirm "Daily System Maintenance" and "Cell Culture Feed" are **NOT** present.
   - Confirm real protocols (e.g., `PCR Prep`) are present.
3. **Verify Empty State UI**:
   - Navigate to **Run History** or "Recent Runs" widget.
   - **Verify proper empty state is displayed**:
     - Should show an empty state component with icon and message (e.g., "No Runs Yet")
     - Should include helpful description (e.g., "Start a protocol simulation to see your history here")
     - Should NOT show loading spinner indefinitely
     - Should NOT show console errors or undefined data warnings
4. **Verify Analytics/Metrics**:
   - Check that any dashboard metrics (avg runtime, success rate, etc.) handle zero runs gracefully
   - Should display "N/A" or "0" instead of errors or NaN
5. **Create Verification Run**:
   - Start a new run of a real protocol (e.g., `Generic Liquid Handling`).
   - Verify it appears in the "queue" (Running) tab.
   - Wait for completion.
   - Verify it appears in the "history" (Run Records) list with correct name and status.
   - Click the run to ensure the Detail View loads correctly (verifying `getProtocolRun(id)` logic).
6. **Verify Response Structure**:
   - Open browser DevTools Network tab
   - Check `/protocols/runs/queue` response when empty
   - Verify it returns `{items: [], total: 0, page: 1, size: 50}` not `null` or `[]`
