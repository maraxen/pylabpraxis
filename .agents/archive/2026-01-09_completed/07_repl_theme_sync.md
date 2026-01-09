# Agent Prompt: 07_repl_theme_sync

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [repl_enhancements.md](../../backlog/repl_enhancements.md)  

---

## Task

Implement JupyterLite theme synchronization to match the main app's dark/light mode setting.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [repl_enhancements.md](../../backlog/repl_enhancements.md) | Work item tracking (Phase 2) |
| `praxis/web-client/src/app/features/repl/jupyterlite-repl.component.ts` | REPL component |
| `praxis/web-client/src/assets/jupyterlite/` | JupyterLite assets |
| `praxis/web-client/src/app/layout/unified-shell.component.ts` | Theme toggle location |

---

## Implementation

1. **Theme Detection**:
   - Subscribe to app's theme change observable
   - Get current theme state from `ThemeService` or equivalent

2. **JupyterLite Theme API**:
   - Research JupyterLite's theme configuration options
   - Identify postMessage or iframe communication for theme changes
   - Consider `jupyter-lite.json` configuration

3. **CSS Variable Injection**:
   - Inject app's CSS variables into JupyterLite iframe
   - Match primary colors, background, text colors

4. **Initial Load**:
   - Set correct theme before iframe loads
   - Handle race conditions between theme detection and iframe ready

---

## Expected Outcome

- JupyterLite switches to dark mode when app is in dark mode
- Theme changes in app immediately reflect in JupyterLite
- Consistent visual experience across the application

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
