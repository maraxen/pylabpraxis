# Task: Restore Hardware Discovery Button Across UI

**Dispatch Mode**: 🧠 **Planning Mode**

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P1 item "Hardware Discovery Button Missing"
- `.agents/backlog/browser_mode_issues.md` - Issue #6

## Problem

The "Discover Hardware" button has disappeared from browser mode UI. It should be easily accessible from several key interfaces.

## Required Locations

Ensure the button is present and functional on:

1. Home Dashboard
2. Asset Management
3. Deck View
4. REPL
5. Protocol Run (Asset selection step)
6. Command Palette

## Implementation

1. Create a shared `HardwareDiscoveryButtonComponent`.
2. Integrate this component into the templates of the listed pages.
3. Ensure it is only visible/enabled when appropriate for the current mode.

## Testing

1. Verify button visibility on all target pages.
2. Verify clicking the button triggers a hardware discovery scan.

## Definition of Done

- [ ] Discovery button is consistently available across the app.
- [ ] Button works correctly in browser mode (triggers WebSerial discovery).
- [ ] Update `.agents/backlog/browser_mode_issues.md` - Mark #6 as ✅ Complete
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "Hardware Discovery Button Missing" as complete

## Files Likely Involved

- `praxis/web-client/src/app/shared/components/` (new component)
- Feature templates for Home, Assets, Deck View, REPL, and Run Protocol.
