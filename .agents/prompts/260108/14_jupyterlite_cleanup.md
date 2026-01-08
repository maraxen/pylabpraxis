# Agent Prompt: 14_jupyterlite_cleanup

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [repl_enhancements.md](../../backlog/repl_enhancements.md)  
**Priority:** P3

---

## Task

Suppress harmless 404 errors for PyLabRobot virtual filesystem imports and optimize JupyterLite initial load time.

---

## Issues to Fix

### 1. 404 Errors for PyLabRobot Paths

**Problem**: Console shows 404 errors for virtual filesystem imports that are handled by Pyodide but trigger browser network requests.

**Solution**: Configure `jupyter-lite.json` to suppress or redirect these requests.

### 2. Slow Initial Load

**Problem**: REPL takes several seconds to initialize, with visible race conditions.

**Solution**: Explore pre-bundling or eager loading strategies.

---

## Implementation Steps

### 1. Configure JupyterLite JSON

Update `praxis/web-client/src/assets/jupyterlite/jupyter-lite.json`:

```json
{
  "jupyter-config-data": {
    "disabledExtensions": ["..."],
    "federated_extensions": ["..."],
    "litePluginSettings": {
      "pyodide-kernel-extension:kernel": {
        "loadPyodideOptions": {
          "indexURL": "...",
          "packages": ["micropip", ...]
        }
      }
    }
  }
}
```

### 2. Add Request Interception (if needed)

In `jupyterlite-repl.component.ts`, consider intercepting fetch for known missing paths:

```typescript
// Service worker or fetch wrapper to suppress known 404s
```

### 3. Optimize Package Loading

Consider pre-loading common packages:

- `numpy`, `pandas` if used
- PLR shims

### 4. Verify Improvements

- Check console for 404 reduction
- Measure load time before/after

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [repl_enhancements.md](../../backlog/repl_enhancements.md) | Backlog tracking |
| [jupyterlite-repl.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/repl/jupyterlite-repl.component.ts) | REPL component |
| [src/assets/jupyterlite/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/assets/jupyterlite/) | JupyterLite assets |

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for conventions.

---

## On Completion

- [ ] Commit changes with message: `chore(repl): suppress 404s and optimize JupyterLite load`
- [ ] Update [repl_enhancements.md](../../backlog/repl_enhancements.md) - mark Phase 5 items complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
