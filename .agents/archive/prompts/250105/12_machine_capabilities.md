# Prompt 12: Machine Capabilities Verification & Theme Fix

Verify machine capabilities configuration and fix theme sync issue.

## Context

Hamilton Starlet has configurable capabilities (96-head, iSwap) that should display and save correctly.

## Tasks

1. Test Add Machine dialog with Hamilton Starlet:
   - Verify 96-head option appears
   - Verify iSwap option appears
   - Save machine, reload, verify capabilities persisted

2. Fix capability dropdown theme sync:
   - Dropdown currently always renders in light theme
   - Make it respect app theme (light/dark mode)
   - Check for hardcoded colors or missing theme class

3. Audit other machine types with capabilities (review MachineDefinitions)

## Files to Check

- `praxis/web-client/src/app/features/assets/dialogs/add-machine-dialog/`
- `praxis/web-client/src/app/features/assets/components/capability-selector/` (if exists)
- Check for mat-select or mat-menu with missing theme binding

## Reference

- `.agents/backlog/browser_mode_issues.md` (issue #14)
