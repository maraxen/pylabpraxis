# Hardware Connectivity - Phase B (Main Thread Migration)

**Backlog**: `hardware_connectivity.md`
**Priority**: P2
**Effort**: Large

---

## Goal

Move actual serial I/O from the Python worker thread to the TypeScript main thread for better performance and simpler debugging.

## Background

Phase A (Driver Abstraction) is complete:

- `ISerial` and `ISerialDriver` interfaces created
- `FtdiSerial` TypeScript driver implemented
- `DriverRegistry` for automatic device-to-driver matching
- `MockSerial` for unit tests and offline dev

## Current Architecture

```
[Angular Main Thread] ──WebSerial API──> [USB Device]
         │
         │ (shim injection)
         ▼
[Pyodide Worker] ──Python shim──> [Angular via postMessage]
```

## Target Architecture

```
[Angular Main Thread] ──FtdiSerial/WebSerial──> [USB Device]
         │
         │ (synchronous calls)
         ▼
[Pyodide Worker] ──proxy object──> [Main thread driver]
```

## Tasks

1. **Create Main Thread Serial Manager**
   - Singleton service to manage serial connections
   - Handle device selection and connection lifecycle
   - Expose API for Pyodide worker to call

2. **Update Python Shim**
   - Replace direct WebSerial calls with proxy to main thread
   - Use `postMessage` with `SharedArrayBuffer` for synchronous reads (if needed)
   - Fallback to async pattern if SharedArrayBuffer unavailable

3. **Update FTDI Driver**
   - Move status byte stripping to TypeScript
   - Implement baud rate changes in main thread
   - Handle reconnection and error recovery

4. **Update JupyterLite REPL**
   - Initialize main thread serial manager on load
   - Inject proxy object into Pyodide environment
   - Handle connection status updates in UI

5. **Testing**
   - E2E test with physical device
   - Mock tests for serial manager
   - Verify CLARIOstar still works

## Files to Modify

| File | Action |
|------|--------|
| `core/services/serial-manager.service.ts` | Create |
| `features/repl/drivers/ftdi-web-serial.ts` | Major refactor |
| `features/repl/shims/web_serial_shim.py` | Update proxy pattern |
| `features/repl/components/jupyterlite-repl.component.ts` | Initialize manager |

## Success Criteria

- [ ] Serial I/O runs on main thread
- [ ] Python code uses proxy to main thread driver
- [ ] CLARIOstar communications work as before
- [ ] Reconnection after disconnect works
- [ ] Performance is equal or better
