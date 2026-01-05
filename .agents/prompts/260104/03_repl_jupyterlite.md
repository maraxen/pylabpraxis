# Task: REPL → JupyterLite Migration (P2)

## Context

Replace the current xterm.js-based REPL with JupyterLite to provide a full notebook environment. This is a **complete replacement**, not an addition.

## Backlog Reference

See: `.agents/backlog/repl_jupyterlite.md`

## Scope

### Phase 1: JupyterLite Integration

- Add JupyterLite dependencies to the Angular project
- Create `JupyterliteReplComponent` to embed JupyterLite
- Configure for single notebook mode (not full JupyterLab UI)
- Integrate with application light/dark theme

### Phase 2: Pyodide Kernel Configuration

- Configure JupyterLite to use Pyodide kernel
- Pre-install required packages (pylabrobot, etc.)
- Create bootstrap script for kernel initialization

### Phase 3: Asset Preloading

- Auto-load all resources as Python variables on kernel start
- Auto-load all machines as Python variables
- Variable naming: `{description}_{uuid_prefix}` (e.g., `plate_96_corning_abc123`)
- Query SqliteService for asset data

### Phase 4: Quick Add Support

- Keep inventory sidebar panel
- "Insert" button adds variable name to current notebook cell
- Variable already exists from preloading, so just insert the name

### Phase 5: Cleanup

- Remove xterm.js REPL (`repl.component.ts`)
- Remove related worker files if only used for REPL
- Update routes and navigation

## Files to Create/Modify

**Create:**
- `praxis/web-client/src/app/features/repl/jupyterlite-repl.component.ts`

**Delete:**
- `praxis/web-client/src/app/features/repl/repl.component.ts` (after migration)

**Modify:**
- `package.json` - Add JupyterLite dependencies
- `angular.json` - Configure JupyterLite assets
- `praxis/web-client/src/app/features/repl/repl.routes.ts`

## Technical Notes

JupyterLite is frontend-only by design. Even in production mode, the REPL will NOT use the backend - this keeps processes isolated.

```bash
# Possible dependencies
npm install @jupyterlite/core @jupyterlite/pyodide-kernel
```

## Expected Outcome

- JupyterLite notebook interface replaces xterm.js REPL
- All resources/machines preloaded as variables
- Theme matches application
- Works entirely in browser (no backend dependency for REPL)
