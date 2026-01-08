# Task: Fix Add Resource Not Working (P1)

## Context

The "Add Resource" functionality is broken in browser mode. Users cannot add resources from the PLR definitions catalog.

## Backlog Reference

See: `.agents/backlog/browser_mode_issues.md` - Item #2

## Investigation Steps

1. **Trace the Add Resource Flow**
   - Open browser dev tools (Console + Network tabs)
   - Navigate to Asset Management → Resources tab
   - Click "Add Resource" button
   - Note any console errors or failed requests

2. **Check Frontend Handler**
   - Find the "Add Resource" button click handler in `assets.component.ts` or `resource-dialog.component.ts`
   - Verify it checks `ModeService.isBrowserMode()`
   - Trace the call to `AssetService.addResource()` or similar

3. **Check SqliteService Integration**
   - Verify `SqliteService.addResource()` method exists and is called
   - Check if the resource is being written to the browser's IndexedDB/SQLite
   - Verify the write operation succeeds

4. **Check UI Refresh**
   - After add, verify the resource list refreshes
   - Check if signals/observables are properly triggering updates

## Files to Examine

- `praxis/web-client/src/app/features/assets/assets.component.ts`
- `praxis/web-client/src/app/features/assets/components/resource-dialog.component.ts`
- `praxis/web-client/src/app/features/assets/services/asset.service.ts`
- `praxis/web-client/src/app/core/services/sqlite.service.ts`

## Expected Outcome

- Users can add resources in browser mode
- Added resources appear in the Resources tab immediately
- No console errors during the add operation

## Testing

1. Add a resource (e.g., a 96-well plate)
2. Verify it appears in the Resources list
3. Refresh the page and verify it persists
4. Verify it can be used in protocol execution
