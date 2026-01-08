# Task: Add "Easy Add" for Assets in REPL

**Dispatch Mode**: 🧠 **Planning Mode**

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P2 item "REPL Easy Add Assets"
- `.agents/backlog/repl.md`

## Problem

Currently, there is no quick way to inject machine and resource handles (variables) from the laboratory inventory into a REPL session. Users have to manually type the connection logic or variable setup.

## Implementation

1. Add an "Add to REPL" action to items in the REPL Variables Sidebar or Create a new "Inventory" tab in the REPL sidebar.
2. Clicking the action should inject the appropriate initialization code into the REPL prompt (e.g., `lh = await LiquidHandler.from_inventory('my_machine')`).
3. Ensure the injected code matches the `web_bridge.py` bootstrap patterns for browser mode.

## Testing

1. Open REPL.
2. Use the "Easy Add" feature for a machine in the inventory.
3. Verify the machine variable becomes available in the REPL session after the injected command runs.

## Definition of Done

- [ ] Users can easily add inventory machines/resources to a REPL session via UI.
- [ ] Injected code correctly initializes the asset for use in the REPL.
- [ ] Update `.agents/backlog/repl.md` with completion status.
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "REPL Easy Add Assets" as complete
