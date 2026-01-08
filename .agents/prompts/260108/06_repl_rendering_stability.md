# Agent Prompt: 06_repl_rendering_stability

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [repl_enhancements.md](../../backlog/repl_enhancements.md)  
**Priority:** P2

---

## Task

Fix the REPL not rendering until "Refresh Kernel" button is pressed. Investigate and resolve the race condition between iframe loading and kernel initialization.

---

## Implementation Steps

### 1. Investigate Race Condition

Analyze the JupyterLite iframe lifecycle in:

- `praxis/web-client/src/app/features/repl/jupyterlite-repl.component.ts`

Identify where `praxis_repl` BroadcastChannel communication may fail at startup.

### 2. Implement Robust Initialization

```typescript
// Possible solutions:
// 1. Add iframe onload handler before kernel init
// 2. Implement retry logic for BroadcastChannel connection
// 3. Add explicit ready signal handshake between main app and JupyterLite
```

### 3. Add Loading State

Ensure the REPL shows a proper loading indicator while kernel initializes, rather than blank screen.

### 4. Verify Fix

- Load the REPL page fresh
- Confirm kernel connects automatically without manual refresh
- Test with both light and dark themes

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [repl_enhancements.md](../../backlog/repl_enhancements.md) | Backlog tracking |
| [jupyterlite-repl.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/repl/jupyterlite-repl.component.ts) | Main REPL component |
| [praxis/web-client/src/app/features/repl/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/repl/) | REPL feature directory |

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for conventions.

---

## On Completion

- [ ] Commit changes with message: `fix(repl): resolve kernel initialization race condition`
- [ ] Update [repl_enhancements.md](../../backlog/repl_enhancements.md) - mark Phase 1 complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
- [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) - Known issues
