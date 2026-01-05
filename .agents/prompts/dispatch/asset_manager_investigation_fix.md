# Task: Fix Asset Manager Rendering in Browser Mode

**Dispatch Mode**: 🧠 **Planning Mode** (root cause investigation required)

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P1 item "Asset Manager Not Rendering"
- `.agents/backlog/browser_mode_issues.md` - Issue #1
- `.agents/ROADMAP.md` - Investigation Notes

## Problem

The Asset Manager is showing as empty in browser mode despite `praxis.db` containing data.

## Investigation Steps

1. Verify `praxis.db` contains expected PLR data using `sqlite3` on the assets file.
2. Add debug logging to `SqliteService` and `AssetManagementComponent` to trace data loading.
3. Check browser console for errors related to database loading or service initialization.

## Implementation

1. Resolve identified root cause (e.g., pathing, timing, or query issues).
2. Ensure assets and groupings render correctly once data is flowing.

## Testing

1. E2E test to verify assets are listed on the page.
2. Unit tests for `SqliteService` queries in browser mode.

## Definition of Done

- [ ] Asset Manager displays full list of resources and machines in browser mode.
- [ ] All groupings (accordions) work as expected.
- [ ] Update `.agents/backlog/browser_mode_issues.md` - Mark #1 as ✅ Complete
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "Asset Manager Not Rendering" as complete

## Files Likely Involved

- `praxis/web-client/src/app/core/services/sqlite.service.ts`
- `praxis/web-client/src/app/features/assets/asset-management.component.ts`
