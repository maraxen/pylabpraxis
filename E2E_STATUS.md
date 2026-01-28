# E2E Test Status Report - Praxis (FINAL)

## Summary
- **Date**: 2026-01-28
- **Total Tests Analyzed**: 117
- **Passing**: 40
- **Failing**: 66 (including 18 Fatal Errors)
- **Status**: 🔴 Critical Failures Detected

## Failure Clusters

### 1. Asset Management & Persistence
- **Issues**: Add Machine/Resource dialogs failing; state not persisting across reloads.
- **Key Error**: Assets not visible in search/inventory post-creation.

### 2. Database & Export
- **Issues**: Export/Import triggers failing in browser mode; confirmation dialogs not appearing.

### 3. Protocol Execution Flow
- **Issues**: Setup wizard steps incomplete; protocol cards missing in library.
- **Key Error**: `Failed to find protocol cards`.

### 4. JupyterLite / Python Integration
- **Issues**: Severe activation failures for plugins; OPFS initialization errors.
- **Key Errors**: 
  - `Plugin '@jupyterlab/codemirror-extension:commands' failed to activate`
  - `No provider for: @jupyterlab/notebook:INotebookTracker`
  - `SQLITE_ERROR: no such table: function_protocol_definitions`

### 5. Interaction & UX
- **Issues**: Execution controls (Pause/Abort) and Deck View (Hover/Click) interactions timing out.

### 6. Deployment & Routing (GH Pages)
- **Issues**: App home loading and deep link resolution failures under simulation.

## Technical Details
- **Log File**: `/tmp/playwright_full.log`
- **Runner**: Playwright (Chromium)
- **Environment**: Local Dev Server (Vite/Angular)

## Recommended Next Steps
1. **Fix JupyterLite Plugins**: Address the missing `INotebookTracker` provider.
2. **Database Schema Injection**: Ensure `function_protocol_definitions` table is created before execution.
3. **Asset Selection Reliability**: Debug the wizard step transitions in `AssetManagementFlow`.
