# REPL → JupyterLite Migration Backlog

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-04
**Status**: ✅ Complete (2026-01-05) - pylabrobot limitation documented

---

## Overview

Replace the current xterm.js-based REPL with JupyterLite to provide a full notebook environment. This is a **complete replacement**, not an addition. The JupyterLite environment should share the same Pyodide kernel as the rest of the browser-mode application where possible.

---

## Goals

1. **Full Notebook Environment**: Rich cell-based editing with markdown support
2. **Quick Add Support**: Retain ability to inject machine/resource handles from inventory
3. **Preloaded Assets**: Auto-load all resources, deck states, and machines as variables
4. **Shared Kernel**: Use same Pyodide kernel as browser mode execution (for browser mode)
5. **Frontend-Only**: No backend dependency for REPL even in production mode

---

## Architecture Decision: Isolated vs Shared Kernel

### Option Chosen: Frontend-Only (Isolated)

The REPL will use its own Pyodide kernel, separate from any backend Python processes. This keeps processes isolated and ensures the REPL works identically in all modes (browser, lite, production).

**Rationale**:

- Simpler architecture - no coordination with backend needed
- Consistent behavior across deployment modes
- Protects production backend from REPL-induced crashes/issues
- JupyterLite is already designed for frontend-only operation

---

## Phase 1: JupyterLite Integration

### Tasks

- [x] **Add JupyterLite Dependencies**
  - Added `jupyterlite-core` and `jupyterlite-pyodide-kernel` to pyproject.toml
  - Configure build pipeline for JupyterLite assets

- [x] **Create `JupyterliteReplComponent`**
  - Replace current `ReplComponent`
  - Embed JupyterLite in the REPL panel area via iframe
  - Configure for REPL mode (not full JupyterLab)

- [x] **Theme Integration**
  - Light/dark mode matching application theme via URL params
  - Syncs with `AppStore.theme()`

- [x] **Panel Integration**
  - Fit within existing REPL panel layout
  - Toolbar/menu bar compatibility

---

## Phase 2: Pyodide Kernel Configuration

### Tasks

- [ ] **Kernel Configuration**
  - Configure JupyterLite to use Pyodide kernel
  - Install required packages (pylabrobot, etc.)

- [ ] **Bootstrap Script**
  - Auto-run initialization code on kernel start
  - Import common PLR modules
  - Set up environment

- [ ] **Package Management**
  - Pre-install packages via JupyterLite config
  - Handle micropip for additional packages

---

## Phase 3: Asset Preloading

### Variable Naming Convention

Variables should be named descriptively with a UUID component to ensure uniqueness:

- `plate_96_corning_abc123` - Resources
- `star_hamilton_def456` - Machines
- `deck_state_ghi789` - Deck states

### Tasks

- [ ] **Resource Preloading**
  - Query SqliteService for all resources
  - Generate Python code to instantiate resource objects
  - Execute on kernel start

- [ ] **Machine Preloading**
  - Query SqliteService for all machines
  - Generate Python code to create machine handles
  - Execute on kernel start

- [ ] **Deck State Preloading**
  - Load current deck configurations
  - Create deck state variables

- [ ] **Lazy Loading Option**
  - For large inventories, consider lazy loading on first access
  - Use Python properties or `__getattr__` magic

---

## Phase 4: Quick Add Support

### Current Functionality

The current REPL has an Inventory tab with "Inject Code" buttons that insert machine/resource handles.

### Tasks

- [ ] **Inventory Panel Integration**
  - Keep sidebar panel with inventory listing
  - "Insert" button adds code to current cell

- [ ] **Code Insertion API**
  - JupyterLite API for inserting text at cursor
  - Insert variable name (which is already defined from preloading)

- [ ] **Smart Insertion**
  - Insert just the variable name if already preloaded
  - Insert full instantiation code if not preloaded

---

## Phase 5: Migration & Cleanup

### Tasks

- [ ] **Remove xterm.js REPL**
  - Delete `ReplComponent` and related files
  - Remove xterm.js dependencies
  - Remove python.worker.ts (if only used for REPL)

- [ ] **Update Navigation**
  - Ensure REPL route loads JupyterliteReplComponent
  - Update command palette references

- [ ] **Documentation**
  - Update user guides for new notebook interface
  - Document keyboard shortcuts

---

## Technical Considerations

### JupyterLite Build

JupyterLite requires a build step to generate static assets. This needs to be integrated into the Angular build pipeline.

```json
// Possible package.json scripts
{
  "scripts": {
    "jupyterlite:build": "jupyter lite build --output-dir=src/assets/jupyterlite",
    "build": "npm run jupyterlite:build && ng build"
  }
}
```

### Bundle Size

JupyterLite adds significant bundle size. Consider:

- Lazy loading the JupyterLite module
- Service worker for caching
- CDN hosting for JupyterLite assets

### Performance

- First load may be slow (Pyodide + packages)
- Implement loading spinner with progress
- Cache kernel state where possible

---

## Related Files

| File | Current | After Migration |
|------|---------|-----------------|
| `repl.component.ts` | xterm.js REPL | Delete |
| `python.worker.ts` | Pyodide worker | Review/delete if unused |
| `jupyterlite-repl.component.ts` | N/A | New main component |

---

## Success Criteria

1. [ ] JupyterLite notebook embedded in REPL panel
2. [ ] Theme matches application light/dark mode
3. [ ] All resources/machines preloaded as variables
4. [ ] Quick Add inserts variable names from inventory
5. [ ] xterm.js REPL completely removed
6. [ ] Works in browser mode without backend
7. [ ] Performance acceptable (< 5s first load)

---

## References

- [JupyterLite Documentation](https://jupyterlite.readthedocs.io/)
- [JupyterLite + Angular](https://github.com/jupyterlite/jupyterlite/discussions) (search for Angular examples)
- [Pyodide](https://pyodide.org/)
