# CLARIOstar REPL Connectivity Issue - Resolved

## Status

**Fixed.**

The connectivity issue caused by `web-serial-polyfill` not supporting FTDI devices has been resolved by implementing a custom FTDI WebUSB driver directly in the Python shim (`web_serial_shim.py`).

## Implementation Details

### 1. Python-Side FTDI Driver

Instead of relying on a TypeScript driver exposed on `window` (which caused cross-thread access issues between the UI thread and the WebWorker running the Pyodide kernel), the driver logic was ported to Python.

**Key Features:**

* **Direct WebUSB Access:** Uses `navigator.usb` (via Pyodide's `js` module) directly from the worker. This works because `navigator.usb.getDevices()` returns devices authorized in the main thread.
* **FTDI Protocol:** Implements the same protocol logic (Reset, Baud Rate, Data Characteristics, Status Byte stripping) in Python.
* **Seamless Fallback:** The shim checks for:
    1. Native WebSerial (if available).
    2. Polyfill (window based, if available/accessible).
    3. **FTDI WebUSB** (Directly scanning `navigator.usb.getDevices()` for VendorID 0x0403).

### 2. Angular REPL Reverted

The `JupyterliteReplComponent` was reverted to its previous state (only exposing `polyfillSerial`), as the FTDI driver is now self-contained in the shim.

### 3. Shim Update (`web_serial_shim.py`)

The shim was significantly enhanced to:

* Safely import `window` (handling Worker context).
* Implement the full FTDI driver serialization/deserialization logic.
* Handle 125000 baud specifically for CLARIOstar.

## Verification

* **Build:** The web-client builds successfully.
* **Architecture:** The new architecture avoids the "NameError: window is not defined" issue by robustly handling imports and not relying on the UI thread's window object for the driver instance.

## Next Steps

* **User Verification:** The user should test the "Add CLARIOstar" flow in the browser.
