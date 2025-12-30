# Specification: Browser Runtime & Static Analysis Architecture

## 1. Overview
This track validates the architecture for "Browser Mode" (Client-side execution) and robust protocol parsing. Instead of rewriting the backend in Rust, we will leverage **Pyodide** to run the existing Python logic in WebAssembly, and **LibCST** for static analysis of protocols.

## 2. Goals
*   **Pyodide Feasibility:** Prove that `pylabrobot` (PLR) can be imported and executed within a Pyodide environment in the browser.
*   **Backend Driver Shim:** Prototype a Python class (`BrowserBackend`) that intercepts PLR commands and bridges them to JavaScript (Angular) for routing to the Visualizer or WebSerial.
*   **Static Analysis (Protocols):** Validate `LibCST` for extracting protocol metadata (parameters, assets) without GxP risks associated with runtime execution.
*   **Static Analysis (PLR Inspection):** Replace runtime introspection in `DiscoveryService` with a `LibCST`-based scanner that extracts resource/machine definitions directly from the PLR source code without importing or instantiating classes.

## 3. Architecture: The "Shim" (IO Layer)
PLR separates high-level logic (`LiquidHandler`) from low-level communication (`Backend`).
*   **Native Mode:** `LiquidHandler` -> `STARBackend` -> `pyserial` -> USB.
*   **Browser Mode:** `LiquidHandler` -> `WebBridgeBackend` -> `js.postMessage` -> Angular Service -> WebSerial API -> USB.

## 4. Static Library Inspection (LibCST)
Currently, `ResourceTypeDefinitionService` instantiates PLR factory functions to get metadata. The new approach will:
1.  Scan `pylabrobot/resources/**/*.py`.
2.  Identify functions returning `Resource` subclasses.
3.  Parse constructor arguments (e.g., `Plate(size_x=127.0, ...)`).
4.  Extract metadata statically.

## 4. Acceptance Criteria
### 4.1 Pyodide Spike
*   [ ] Angular app loads `pyodide`.
*   [ ] `micropip` successfully installs `pylabrobot` (or a stripped-down wheel).
*   [ ] Python code can instantiate `LiquidHandler(backend=WebBridgeBackend())`.
*   [ ] Calling `lh.pick_up_tips()` in Python results in a `console.log` in JavaScript.

### 4.2 LibCST Spike
*   [ ] Python script using `LibCST` parses `simple_transfer.py`.
*   [ ] Script extracts the `source_plate: Plate` type hint and the `transfer_volume` default value without importing the file.
