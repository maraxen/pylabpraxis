# Plan: Browser Runtime & Static Analysis

## Phase 1: Static Analysis (LibCST)
*   [ ] Task: POC Protocol Parser with LibCST.
    *   [ ] Subtask: Create `scripts/analyze_protocol_cst.py`.
    *   [ ] Subtask: Implement `CSTVisitor` to extract function arguments, type hints, and decorators.
    *   [ ] Subtask: Verify it can parse `simple_transfer.py` and output a JSON schema of requirements.
*   [ ] Task: POC PLR Library Inspector with LibCST.
    *   [ ] Subtask: Create `scripts/inspect_plr_cst.py`.
    *   [ ] Subtask: Implement visitor to scan `pylabrobot` vendor modules.
    *   [ ] Subtask: Extract `size_x`, `size_y`, and `category` from factory function bodies without instantiation.

## Phase 2: Pyodide Environment
*   [ ] Task: Angular Pyodide Integration.
    *   [ ] Subtask: Add `pyodide` CDN script or npm package to `praxis/web-client`.
    *   [ ] Subtask: Create `PythonRuntimeService` in Angular to manage the WASM worker.
*   [ ] Task: Dependency Resolution.
    *   [ ] Subtask: Attempt `micropip.install('pylabrobot')`.
    *   [ ] Subtask: Identify blockers (e.g., `pyserial`, `requests` dependency chains).
    *   [ ] Subtask: Create a "browser-compatible" PLR patch or mock if necessary (mocking out hardware I/O modules).

## Phase 3: The IO Bridge
*   [ ] Task: Implement `WebBridgeBackend` (Python).
    *   [ ] Subtask: Create a Python class inheriting from `pylabrobot.liquid_handling.backends.LiquidHandlerBackend`.
    *   [ ] Subtask: Implement `setup()`, `stop()`, and command methods to call `js.self.postMessage`.
*   [ ] Task: End-to-End "Hello World".
    *   [ ] Subtask: Run a 3-line Python script in browser that sends a "Tip Pickup" command to the Angular console.
