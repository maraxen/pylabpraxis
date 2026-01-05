# Task: Expand Manual Machine Configuration Options

**Dispatch Mode**: ⚡ **Fast Mode**

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P2 item "Limited Machine Types"
- `.agents/backlog/browser_mode_issues.md` - Issue #12

## Problem

The backend configuration for manually adding machines currently only seems to include "chatterbox". It needs to be expanded to support all common PyLabRobot machine types.

## Implementation

1. Locate the machine type configuration in the backend (e.g., `praxis/backend/core/machine_manager.py` or similar).
2. Expand the list of support types to include: `LiquidHandler`, `PlateReader`, `Shaker`, `PumpArray`, `Peeler`, etc.
3. Ensure the frontend "Add Machine" dialog correctly renders these options in the category/type dropdowns.

## Testing

1. Verify the "Add Machine" dialog in Asset Management shows the expanded list of types.
2. Verify a machine of a new type can be successfully added to the database.

## Definition of Done

- [ ] Manual machine addition supports a comprehensive set of PyLabRobot machine types.
- [ ] Update `.agents/backlog/browser_mode_issues.md` - Mark #12 as ✅ Complete.
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "Limited Machine Types" as complete.
