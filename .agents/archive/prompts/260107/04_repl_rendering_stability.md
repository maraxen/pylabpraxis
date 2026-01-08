# Agent Prompt: 04_repl_rendering_stability

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260107](./README.md)
**Backlog:** [repl_enhancements.md](../../backlog/repl_enhancements.md)

---

## Task

Fix the REPL not rendering until the "Refresh Kernel" button is pressed. Investigate and resolve the race condition between iframe loading and kernel initialization.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [repl_enhancements.md](../../backlog/repl_enhancements.md) | Work item tracking (Phase 1) |
| [jupyterlite-repl.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/repl/jupyterlite-repl.component.ts) | Main REPL component |
| [repl/README.md](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/repl/README.md) | REPL architecture docs |

---

## Problem Description

Users must click "Refresh Kernel" for the REPL to render. The issue is a race condition:

1. JupyterLite iframe loads
2. Kernel initialization begins
3. `praxis_repl` BroadcastChannel communication starts
4. **Race:** Component renders before kernel is ready

---

## Implementation Details

### 1. Investigate Current Flow

```typescript
// jupyterlite-repl.component.ts
// Check: When is the iframe loaded vs when is the kernel ready?
// Check: BroadcastChannel message timing
```

### 2. Potential Fixes

**Option A:** Wait for kernel ready signal before showing content

```typescript
private kernelReady = signal(false);

ngAfterViewInit() {
  this.broadcastChannel.onmessage = (event) => {
    if (event.data.type === 'kernel_ready') {
      this.kernelReady.set(true);
    }
  };
}
```

**Option B:** Add explicit initialization handshake

```typescript
// Send 'init' message, wait for 'ready' response
this.broadcastChannel.postMessage({ type: 'init' });
```

**Option C:** Retry logic with exponential backoff

### 3. Ensure Robust Startup

- Handle cases where BroadcastChannel messages are missed
- Add loading indicator during initialization
- Log timing for debugging

---

## Project Conventions

- **Frontend Dev**: `cd praxis/web-client && npm start`
- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for guidelines.

---

## On Completion

- [ ] REPL renders without requiring "Refresh Kernel" click
- [ ] Update [repl_enhancements.md](../../backlog/repl_enhancements.md) Phase 1
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) "REPL Rendering Stability"
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md)
- [archive/2026-01-06_completed/repl_jupyterlite.md](../../archive/2026-01-06_completed/repl_jupyterlite.md) - Prior REPL work
