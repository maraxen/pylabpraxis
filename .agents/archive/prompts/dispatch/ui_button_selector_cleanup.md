# Task: Remove Checkmarks from Button Selectors

**Dispatch Mode**: ⚡ **Fast Mode** (straightforward CSS/template changes)

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P2 item "Button Selector Checkmarks"
- `.agents/backlog/browser_mode_issues.md` - Issue #13

## Problem

Button selectors throughout the app show checkmarks inside the button display. This is incorrect UX - checkmarks should not appear in toggle-style button groups.

## Specific Locations to Fix

1. **Execution Monitor** - Order selector (ascending/descending)
2. **Protocol Workflow** - Simulation/Physical button selector
3. **Search for ALL instances**: `grep -rn "mat-button-toggle\|button-toggle" praxis/web-client/src`

## Implementation

For each button toggle group found:

1. Remove any `<mat-icon>check</mat-icon>` or checkmark icon inside button content
2. If checkmark is added via CSS ::after, remove that style
3. Selection state should be indicated by background color/border only (Material default)

## Testing

1. Run: `cd praxis/web-client && npm test -- --watch=false --reporters=default`
2. Manually verify in browser: `npm run start` then check execution monitor and protocol workflow

## Definition of Done

- [ ] No checkmarks visible in any button toggle selectors
- [ ] Selection state still visually clear via highlight/border
- [ ] All existing tests pass
- [ ] Update `.agents/backlog/browser_mode_issues.md` - Mark #13 as ✅ Complete with date
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "Button Selector Checkmarks" as complete

## Files Likely to Modify

- `praxis/web-client/src/app/features/execution-monitor/components/*.ts`
- `praxis/web-client/src/app/features/run-protocol/components/*.ts`
- Possibly global styles in `src/styles.scss`
