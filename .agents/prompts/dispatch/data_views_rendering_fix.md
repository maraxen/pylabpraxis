# Task: Fix Schema-Defined Data Views Rendering

**Dispatch Mode**: 🧠 **Planning Mode**

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P1 item "Data Views Not Rendering"
- `.agents/backlog/browser_mode_issues.md` - Issue #5

## Problem

Protocol decorator `@data_view` definitions are not rendering on the protocol setup screens. Related visualizations like summary card "traces" are also missing.

## Implementation

1. Trace the loading of protocol metadata from the backend/SqliteService to the UI.
2. Verify that the frontend components responsible for rendering data views correctly handle the schema-defined data.
3. Map the "traces" data to the Home screen summary cards and ensure they are populated.

## Testing

1. Select a protocol known to have `@data_view` definitions and verify they appear during setup.
2. Verify home screen summary cards show visual traces (mini-charts).

## Definition of Done

- [ ] Protocol setup displays all schema-defined data views.
- [ ] Home screen cards show visual progress/stat traces.
- [ ] Update `.agents/backlog/browser_mode_issues.md` - Mark #5 as ✅ Complete
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "Data Views Not Rendering" as complete

## Files Likely Involved

- `praxis/web-client/src/app/features/run-protocol/`
- `praxis/web-client/src/app/features/home/`
