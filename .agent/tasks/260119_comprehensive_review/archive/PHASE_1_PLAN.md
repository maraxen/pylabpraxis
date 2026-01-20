# Status: Complete
# Phase 1: Architecture & Execution Engine Implementation Plan

### Status Update
- [x] All implementation tasks (1, 2, 3, 4) are completed and verification passed.
- [x] Frontend verification (`ng build`) passed.

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Unblock protocol execution in the browser by robustly serializing protocols, fixing the Pyodide environment, and streamlining machine instantiation.

**Architecture:**
1.  **Backend**: Serializes protocol functions using `cloudpickle`, stripping server-side `praxis` dependencies.
2.  **Frontend**: Fetches pickled code, deserializes in Pyodide, and executes using `runPythonAsync`.
3.  **Bridge**: Injects `WebBridgeBackend` and `Deck` objects into the execution scope.

**Tech Stack:** Python (Backend), Angular/TypeScript (Frontend), Pyodide, Cloudpickle.

---

### Task 1: Protocol Serialization Service (Backend) [x]

**Files:**
- Create: `praxis/backend/services/protocol_serializer.py`
- Modify: `praxis/backend/api/endpoints/protocols.py` (or relevant endpoint file)
- Test: `tests/backend/services/test_protocol_serializer.py`

**Step 1: Write the failing test**

```python
# tests/backend/services/test_protocol_serializer.py
import pytest
from praxis.backend.services.protocol_serializer import serialize_protocol_function

def sample_protocol(layout, **kwargs):
    return "success"

def test_serialize_protocol_function():
    # Helper to simulate a Praxis-decorated function if needed
    sample_protocol._protocol_definition = {}
    
    serialized = serialize_protocol_function(sample_protocol)
    assert isinstance(serialized, bytes)
    assert len(serialized) > 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/backend/services/test_protocol_serializer.py`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Implement Serialization Logic**

Create `praxis/backend/services/protocol_serializer.py`:
-   Import `cloudpickle`.
-   Define `serialize_protocol_function(func)`.
-   **Critical**: Check if `func` is decorated (e.g., has `__wrapped__` or `_protocol_definition`). If so, unwrap it to get the raw function.
-   Return `cloudpickle.dumps(func)`.

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/backend/services/test_protocol_serializer.py`
Expected: PASS

**Step 5: Expose API Endpoint**

Modify `praxis/backend/api/endpoints/protocols.py`:
-   Add GET `/protocols/{id}/code/binary`.
-   Use `ProtocolCodeManager` to load the function.
-   Use `serialize_protocol_function` to dump it.
-   Return `Response(content=data, media_type="application/octet-stream")`.

**Step 6: Commit**

```bash
git add praxis/backend/services/protocol_serializer.py tests/backend/services/test_protocol_serializer.py praxis/backend/api/endpoints/protocols.py
git commit -m "feat(exec): add protocol serialization service and endpoint"
```

---

### Task 2: Pyodide Environment & Execution (Frontend) [x]

**Files:**
- Modify: `praxis/web-client/src/app/core/workers/python.worker.ts`
- Modify: `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts`
- Test: `praxis/web-client/src/app/features/run-protocol/services/execution.service.spec.ts`

**Step 1: Prepare Pyodide Environment**

Modify `python.worker.ts`:
-   Ensure `micropip.install("cloudpickle")` is called during initialization.
-   Ensure `pylabrobot` is installed/loaded.

**Step 2: Update Execution Service to Fetch Blob**

Modify `execution.service.ts`:
-   Add method `fetchProtocolBlob(id: string): Observable<ArrayBuffer>`.
-   Update `executeProtocol` to use this blob instead of raw text if running in browser mode.

**Step 3: Implement Blob Execution in Worker**

Modify `python.worker.ts`:
-   Add a handler for `EXECUTE_BLOB` message.
-   Logic:
    ```python
    import cloudpickle
    import js
    
    # protocol_bytes provided via js context or argument
    protocol_func = cloudpickle.loads(bytes(protocol_bytes))
    
    # Execute
    # TODO: Argument injection (handled in next task)
    await protocol_func(**kwargs)
    ```
-   Use `pyodide.runPythonAsync` to execute the wrapper script that does the unpickling and calling.

**Step 4: Verification (Manual/E2E)**

-   Since this is hard to unit test without a running Pyodide instance in CI, use `playwright-skill` to verify.
-   Create a test that loads the app, goes to a protocol, and clicks "Simulate" (which should trigger this flow).

**Step 5: Commit**

```bash
git add praxis/web-client/src/app/core/workers/python.worker.ts praxis/web-client/src/app/features/run-protocol/services/execution.service.ts
git commit -m "feat(exec): implement pyodide execution of pickled protocols"
```

---

### Task 3: Argument Injection & WebBridge Updates [x]

**Files:**
- Modify: `praxis/web-client/src/assets/python/web_bridge.py`
- Modify: `praxis/web-client/src/app/core/workers/python.worker.ts`

**Step 1: Update WebBridge for Backend Injection**

Modify `web_bridge.py`:
-   Ensure `WebBridgeBackend` is robust.
-   Add helper `create_browser_layout()` that returns a layout configured with `WebBridgeBackend`.

**Step 2: Inject Arguments in Worker**

Modify `python.worker.ts` (Python execution string construction):
-   Before calling `protocol_func`, construct the arguments.
-   **Backend Injection**:
    ```python
    from praxis.web_client.web_bridge import WebBridgeBackend
    from pylabrobot.liquid_handling import LiquidHandler
    
    # Inject backend if the protocol accepts it
    backend = WebBridgeBackend()
    kwargs['backend'] = backend
    
    # If the protocol expects a deck/layout, we might need to construct it here
    # or ensure the protocol constructs it using the injected backend.
    ```
-   **Constraint**: The prompt specifically asks to "inject `backend` and `deck` args".
-   Update the Python wrapper code in `python.worker.ts` to inspect the `protocol_func` signature (using `inspect`) and inject `backend` and `deck` if present.

**Step 3: Verification**

-   Run a protocol that requires `backend` (e.g., `def run(backend): ...`).
-   Verify it receives the `WebBridgeBackend`.

**Step 4: Commit**

```bash
git add praxis/web-client/src/assets/python/web_bridge.py praxis/web-client/src/app/core/workers/python.worker.ts
git commit -m "feat(exec): inject backend and deck arguments into pyodide execution"
```

---

### Task 4: Auto-Lock Deck Logic (Backend/Shared) [x]

**Files:**
- Modify: `praxis/backend/core/workcell_runtime/machine_manager.py`
- Test: `tests/backend/core/workcell_runtime/test_machine_manager.py`

**Step 1: Write failing test**

```python
# tests/backend/core/workcell_runtime/test_machine_manager.py
async def test_initialize_machine_auto_selects_deck(machine_manager, mock_machine_model, db_session):
    # Setup mock machine with allowed_decks metadata
    mock_machine_model.allowed_decks = ["standard_deck"] 
    # Mock finding a definition for "standard_deck"
    
    machine = await machine_manager.initialize_machine(mock_machine_model)
    
    assert machine.deck is not None
    assert machine.deck.name == "standard_deck"
```

**Step 2: Run test**

Run: `pytest ...` -> FAIL

**Step 3: Implement Auto-Selection**

Modify `praxis/backend/core/workcell_runtime/machine_manager.py`:
-   In `initialize_machine`:
-   Check `machine_model.allowed_decks`.
-   If `len(allowed_decks) == 1` and no deck is explicitly configured in `properties_json`:
    -   Lookup the deck definition.
    -   Instantiate it.
    -   Assign to `machine_instance.deck`.

**Step 4: Run test**

Run: `pytest ...` -> PASS

**Step 5: Commit**

```bash
git add praxis/backend/core/workcell_runtime/machine_manager.py
git commit -m "feat(runtime): auto-select deck if unique compatible definition exists"
```

---

### Verification Plan

1.  **Backend Serialization**: Run `test_protocol_serializer.py`.
2.  **Frontend Execution**:
    -   Start Backend (`uv run uvicorn ...`).
    -   Start Frontend (`ng serve`).
    -   Navigate to a protocol.
    -   Click "Simulate".
    -   Check Browser Console for "Pyodide loaded", "Protocol executed".
    -   Verify no "Module 'praxis' not found" errors.
3.  **Arg Injection**:
    -   Use a test protocol: `def run(backend): print(backend)`.
    -   Verify output contains `WebBridgeBackend`.
