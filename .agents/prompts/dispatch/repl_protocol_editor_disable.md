# Task: Grey Out REPL Protocol Editor Option

**Dispatch Mode**: ⚡ **Fast Mode** (simple UI state change)

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P2 item "REPL Protocol Editor"
- `.agents/backlog/browser_mode_issues.md` - Issue #16
- `.agents/backlog/repl.md` - For REPL component context

## Problem

The REPL has a "Protocol Editor" option/mode that is not yet implemented. It should be visually disabled with a "Coming Soon" tooltip.

## Implementation

1. Find the REPL component: `praxis/web-client/src/app/features/repl/`
2. Locate any "Protocol Editor" menu item, tab, or button
3. Add `[disabled]="true"` to the element
4. Add MatTooltip: `matTooltip="Coming Soon" matTooltipPosition="above"`
5. Style disabled state appropriately (opacity, cursor)

## Testing

1. Run REPL tests: `cd praxis/web-client && npm test -- --testPathPattern=repl`
2. Manual verification: Open REPL, verify Protocol Editor is greyed out and tooltip shows

## Definition of Done

- [ ] Protocol Editor option is visually disabled (greyed out)
- [ ] Tooltip "Coming Soon" appears on hover
- [ ] Cannot click/activate the disabled option
- [ ] REPL tests pass
- [ ] Update `.agents/backlog/browser_mode_issues.md` - Mark #16 as ✅ Complete with date
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "REPL Protocol Editor" as complete

## Files to Modify

- `praxis/web-client/src/app/features/repl/repl.component.ts`
- `praxis/web-client/src/app/features/repl/repl.component.html`
