# Status: Complete
# Integration Gap Bridge Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal**: Bridge the "Integration Gap" so the Wizard's machine selection (Step 3) actually drives the Pyodide runtime (Hardware/Simulator).

**Architecture Strategy**:
1.  **Data Flow**: Wizard -> `AssetService` -> `Machine` (with `backend_config` in DB) -> `ExecutionService` -> `PythonRuntime` -> `Worker` -> `WebBridge`.
2.  **Configuration Schema**:
    -   `MachineConfig`: `{ backend_fqn: string, port_id?: string, baudrate?: number, is_simulated: boolean }`.
3.  **Strict Injection**:
    -   Worker must **NOT** hardcode `create_browser_backend()`.
    -   Worker must use `js.machine_config` to import the correct PLR backend class.
    -   Worker must use `patch_io_for_browser` if `!is_simulated`.

**Tech Stack**: Angular, Python (Pyodide), TypeScript

---

**Status Update:**
- Runtime integration fixed.
- Wizard selection now propagates to Worker.
- Dynamic backend instantiation enabled.

### Task 1: WebBridge Factory Update (Completed)

**Files:**
- Modify: `praxis/web-client/src/assets/python/web_bridge.py`

**Step 1: Write the failing test**

Create `praxis/web-client/src/assets/python/tests/test_web_bridge_factory.py`:
```python
import pytest
from web_bridge import create_configured_backend

def test_create_configured_backend_dynamic_import():
    # Mock config for a hypothetical backend
    config = {
        "backend_fqn": "pylabrobot.liquid_handling.backends.simulation.simulator.SimulatorBackend",
        "is_simulated": True
    }
    
    # This should return an instance of SimulatorBackend
    # Note: In a real test environment, we might need to mock importlib or ensure PLR is installed
    # For this plan, we assume the environment can import PLR or we mock the import logic
    backend = create_configured_backend(config)
    assert backend.__class__.__name__ == "SimulatorBackend"

def test_create_configured_backend_calls_patch_io_if_not_simulated(mocker):
    patch_io = mocker.patch("web_bridge.patch_io_for_browser")
    config = {
        "backend_fqn": "pylabrobot.liquid_handling.backends.simulation.simulator.SimulatorBackend",
        "is_simulated": False
    }
    create_configured_backend(config)
    patch_io.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `pytest praxis/web-client/src/assets/python/tests/test_web_bridge_factory.py`
Expected: FAIL (ImportError or AttributeError)

**Step 3: Implement `create_configured_backend` in `web_bridge.py`**

Modify `praxis/web-client/src/assets/python/web_bridge.py`:
```python
import importlib

def create_configured_backend(config: dict):
    """
    Dynamically creates a backend based on configuration.
    
    Args:
        config: Dict containing:
            - backend_fqn: Fully qualified name of the backend class
            - is_simulated: Boolean indicating if this is a simulation
            - Other backend-specific kwargs (port_id, baudrate, etc.)
    """
    backend_fqn = config.get("backend_fqn")
    if not backend_fqn:
        raise ValueError("backend_fqn is required in machine config")

    # Split module and class
    try:
        module_path, class_name = backend_fqn.rsplit('.', 1)
        module = importlib.import_module(module_path)
        backend_class = getattr(module, class_name)
    except (ImportError, AttributeError, ValueError) as e:
        raise ImportError(f"Could not load backend {backend_fqn}: {e}")

    # Prepare kwargs
    # Filter out keys that are not backend arguments if necessary, 
    # or pass strictly what's needed. For now, we might pass relevant keys.
    # Common backend args: packetizer_type (STAR), etc.
    # But usually backend constructors take specific args. 
    # We might need to assume config maps directly to kwargs or extract specific ones.
    # For simulation, usually no args or simple ones.
    
    # Simple strategy: instantiate with no args for Sim, or specific args for real hardware
    # tailored to what PLR expects.
    # If the user provides specific config structure, we use it.
    
    backend_kwargs = {}
    if "port_id" in config:
        backend_kwargs["device_file"] = config["port_id"] # PLR uses device_file usually
        
    instance = backend_class(**backend_kwargs)
    
    if not config.get("is_simulated", False):
        patch_io_for_browser()
        
    return instance
```

**Step 4: Run test to verify it passes**

Run: `pytest praxis/web-client/src/assets/python/tests/test_web_bridge_factory.py`
Expected: PASS

**Step 5: Commit**

```bash
git add praxis/web-client/src/assets/python/web_bridge.py praxis/web-client/src/assets/python/tests/test_web_bridge_factory.py
git commit -m "feat: add create_configured_backend to web_bridge.py"
```

---

### Task 2: Worker Injection Update (Completed)

**Files:**
- Modify: `praxis/web-client/src/app/core/workers/python.worker.ts`

**Step 1: Write the failing test (Conceptual)**

Since `python.worker.ts` is a Web Worker, we verify by inspecting the generated Python code or writing a unit test for the message handler if possible. Here we rely on manual verification or a mock test.

**Step 2: Update `python.worker.ts` to handle `machine_config`**

Modify `praxis/web-client/src/app/core/workers/python.worker.ts`:
1.  Update `EXECUTE_BLOB` case to accept `machine_config`.
2.  In the generated Python script string:
    -   Import `js`
    -   Call `web_bridge.create_configured_backend(js.machine_config.to_py())` instead of hardcoded factory.

```typescript
// In handleMessage for 'EXECUTE_BLOB'
// ...
self.machine_config = data.machine_config; // Expose to JS scope for Pyodide

const pythonScript = `
import js
from web_bridge import create_configured_backend, setup_browser_context

# Create backend from injected config
backend = create_configured_backend(js.machine_config.to_py())

# ... rest of the execution setup
`;
```

**Step 3: Verification**

Run the worker (via app or test harness) and ensure `js.machine_config` is accessible.

**Step 4: Commit**

```bash
git add praxis/web-client/src/app/core/workers/python.worker.ts
git commit -m "feat: inject machine_config into python worker"
```

---

### Task 3: Execution Service Pipeline (Completed)

**Files:**
- Modify: `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts`

**Step 1: Write the failing test**

Modify `praxis/web-client/src/app/features/run-protocol/services/execution.service.spec.ts` (if exists) or create a new spec to test `executeBrowserProtocol` passing the correct config.

**Step 2: Implement Config Resolution in `ExecutionService`**

Modify `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts`:
1.  In `executeBrowserProtocol`:
    -   Fetch `ProtocolRun` using `ProtocolRunsService`.
    -   Get `machineId` from the run.
    -   Fetch `Machine` details (which includes `backend_config` or link to definition).
    -   Construct `MachineConfig` object: `{ backend_fqn: ..., is_simulated: ..., port_id: ... }`.
    -   Pass this config to `pythonRuntime.executeBlob(..., machine_config)`.

**Step 3: Update `PythonRuntimeService` interface**

Ensure `executeBlob` in `praxis/web-client/src/app/core/services/python-runtime.service.ts` accepts the new `machine_config` argument and passes it to the worker.

**Step 4: Run tests**

Run `ng test` for execution service.

**Step 5: Commit**

```bash
git add praxis/web-client/src/app/features/run-protocol/services/execution.service.ts praxis/web-client/src/app/core/services/python-runtime.service.ts
git commit -m "feat: pass machine config from execution service to runtime"
```

---

### Task 4: Verification (Pending E2E)

**Files:**
- Create: `praxis/web-client/src/assets/python/tests/manual_backend_config_test.py` (optional helper)

**Step 1: Manual End-to-End Test**

1.  Launch the app.
2.  Go to Wizard -> Select "Simulated STAR" (ensure DB has this machine with correct FQN: `pylabrobot.liquid_handling.backends.simulation.simulator.SimulatorBackend`).
3.  Run a protocol.
4.  Open Browser Console.
5.  Verify logs: "Backend initialized: SimulatorBackend".
6.  If using a real machine setting (if available locally), verify `patch_io_for_browser` was called (check for "Patching IO" logs).

**Step 2: Commit Verification Artifacts (if any)**

```bash
git add .agent/tasks/260119_comprehensive_review/PHASE_2_5_PLAN.md
git commit -m "docs: add phase 2.5 plan and verification notes"
```
