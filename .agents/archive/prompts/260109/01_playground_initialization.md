# Agent Prompt: Playground Initialization Flow

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260109](./README.md)
**Backlog Reference:** [playground.md](../../backlog/playground.md#p1-playground-initialization)

---

## 1. The Task

The Playground currently lacks a robust, explicit initialization sequence. Users may encounter race conditions where the Python runtime or hardware drivers are not yet ready when the UI loads.

**Goal:** Implement a formal initialization workflow for the Playground that ensures:

1. The Python environment (WebWorker) is fully booted.
2. The Hardware Driver Registry has performed an initial scan.
3. The UI displays a clear "Initializing..." state (skeleton or overlay) until the system is ready.
4. Initialization errors (e.g., Worker failure) are caught and displayed with a "Retry" option.

## 2. Technical Implementation Strategy

*(Architectural guidance for implementing robust initialization orchestration)*

**Frontend Architecture:**

* **`PlaygroundRuntimeService`**: Upgrade this service to act as the orchestrator.
  * Add a signal `initializationState`: `'idle' | 'booting' | 'ready' | 'error'`.
  * Implement `initialize()`:
    * Await `PythonRuntimeService.init()`.
    * Call `DriverRegistry.initialize()` (or `scan()`).
    * Update state to `'ready'`.

* **`PlaygroundComponent`**:
  * In `ngOnInit`, call `runtime.initialize()`.
  * Use the `initializationState` signal to toggle between a **Loading View** (skeleton/spinner) and the **Main View**.
  * Disable execution controls while not `'ready'`.

**Data Flow:**

1. `PlaygroundComponent` mounts → calls `PlaygroundRuntimeService.initialize()`.
2. Service sets state to `'booting'`.
3. Service waits for Python Worker (via `PythonRuntimeService`).
4. Service triggers `DriverRegistry` scan.
5. Service sets state to `'ready'`.
6. Component renders the REPL and Protocol Editor.

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
| --- | --- |
| `praxis/web-client/src/app/features/playground/playground.component.ts` | Main UI entry point. Add loading state logic here. |
| `praxis/web-client/src/app/features/playground/playground.component.html` | Add loading template/overlay. |
| `praxis/web-client/src/app/core/services/playground-runtime.service.ts` | Orchestrate startup sequence. |
| `praxis/web-client/src/app/features/playground/drivers/driver-registry.ts` | Ensure driver scanning is exposed. |

**Reference Files (Read-Only):**

| Path | Description |
| --- | --- |
| `praxis/web-client/src/app/core/services/python-runtime.service.ts` | Provides the underlying Python environment. |
| `praxis/web-client/src/app/features/playground/playground.component.spec.ts` | Existing tests to update. |

## 4. Constraints & Conventions

* **Commands**: Use `npm` for Angular tasks.
* **Frontend Path**: `praxis/web-client`
* **Styling**: Use Tailwind utility classes for the loading overlay (e.g., `absolute inset-0 bg-white/80 flex items-center justify-center`).
* **State**: Use Angular Signals (`signal`, `computed`, `effect`).
* **Error Handling**: Fail gracefully. If the worker doesn't start, the user must know why.

## 5. Verification Plan

**Definition of Done:**

1. The Playground shows a loading indicator immediately upon navigation.
2. The indicator disappears only when Python is ready.
3. Unit tests verify the state transitions.

**Verification Commands:**

```bash
# Run unit tests for the playground component
cd praxis/web-client
npm run test -- src/app/features/playground/playground.component.spec.ts
```

---

## On Completion

* [ ] Commit changes: `feat(playground): implement robust initialization flow`
* [ ] Update backlog item status in `backlog/playground.md`
* [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
* [ ] Mark this prompt complete in batch README and set the status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/playground.md` - Full playground issue tracking
