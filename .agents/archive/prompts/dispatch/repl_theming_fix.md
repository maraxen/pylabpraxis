# Task: Fix REPL Light/Dark Mode Theming

**Dispatch Mode**: 🧠 **Planning Mode** (requires debugging)

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P2 item "REPL Light/Dark Mode"
- `.agents/backlog/browser_mode_issues.md` - Issue #14
- `.agents/backlog/repl.md` - REPL architecture context

## Problem

The REPL does not properly apply light/dark theme. The xterm.js terminal theme needs to be synchronized with the application theme preference.

## Investigation Steps

1. Find REPL component: `praxis/web-client/src/app/features/repl/`
2. Check how xterm.js terminal is initialized and if it subscribes to app theme changes.
3. Verify CSS variables are correctly mapped to xterm.js theme options.

## Implementation

1. Subscribe to app theme service in REPL component.
2. Define light/dark theme objects for xterm.js.
3. Update terminal option `theme` when the application theme toggles.

## Testing

1. Run REPL tests: `npm test -- --testPathPattern=repl`
2. Manual verification: Toggle app theme and ensure REPL background and text colors update accordingly.

## Definition of Done

- [ ] REPL background and text colors match the application theme.
- [ ] Text remains readable with high contrast in both modes.
- [ ] Theme updates dynamically without page refresh.
- [ ] Update `.agents/backlog/browser_mode_issues.md` - Mark #14 as ✅ Complete
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "REPL Light/Dark Mode" as complete

## Files Likely to Modify

- `praxis/web-client/src/app/features/repl/repl.component.ts`
- `praxis/web-client/src/app/features/repl/repl.component.scss`
