# Agent Prompt: 20_settings_stepper_polish

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete
**Batch:** [260108](./README.md)
**Backlog:** [ui_consistency.md](../../backlog/ui_consistency.md)

---

## Task

Fix visual polish issues in Settings page and stepper components. User verification on 2026-01-08 confirmed:

1. **Settings Icons Cutoff**: Rounded corners on settings cards are cutting off icons. Adjust padding/overflow.
2. **Settings Visual Consistency**: Improve overall layout and appearance to match the rest of the app.
3. **Stepper Theme Sync**: Stepper number circles are hardcoded white and don't respond to light/dark theme. Replace with Material Design 3 CSS variables.

### Stepper Fix

Current (broken):

```css
.step-circle-active { background: white; }
```

Fixed:

```css
.step-circle-active { 
  background: var(--mat-sys-primary-container); 
  color: var(--mat-sys-on-primary-container); 
}
```

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [ui_consistency.md](../../backlog/ui_consistency.md) | Work item tracking |
| [settings.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/settings/) | Settings page |
| [machine-dialog.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts) | Stepper styling |

---

## Project Conventions

- **Frontend Build**: `cd praxis/web-client && npx ng build`
- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [x] Commit changes with descriptive message <!-- id: 5 -->
- [x] Update backlog item status in `ui_consistency.md` <!-- id: 6 -->
- [x] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) <!-- id: 7 -->
- [x] Mark this prompt complete in batch README <!-- id: 8 -->

---

## References

- [.agents/README.md](../../README.md) - Environment overview
