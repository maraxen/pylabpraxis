# Hardware Driver Refactor - Completed

**Archived:** 2026-01-08  
**Source:** `hardware_connectivity.md` (Phases A & B)

---

## Summary

The serial communication layer was abstracted to support multiple driver types, including a browser-side FTDI WebUSB implementation.

## Phase A: ISerial Abstraction ✅

- Created `ISerial` and `ISerialDriver` interfaces
- Implemented `FtdiSerial` TypeScript driver (baud rate/parity/stop bits)
- Created `DriverRegistry` for automatic device-to-driver matching
- Implemented `MockSerial` for unit tests and offline dev
- Documented architecture in `praxis/web-client/src/app/features/repl/README.md`

## Phase B: Main Thread Migration ✅

- Moved runtime I/O from Python worker to TypeScript main thread
- Implemented message-passing protocol between worker and host
- Converted `web_serial_shim.py` into thin `SerialProxy` class

## CLARIOstar Plate Reader ✅

Fixed via Python-side FTDI WebUSB driver:

- Direct WebUSB Access via `navigator.usb` from Pyodide worker
- FTDI Protocol implementation (Reset, Baud Rate, Data Characteristics)
- Fallback Chain: Native WebSerial → Polyfill → FTDI WebUSB

## Files Created/Modified

- `praxis/web-client/src/app/core/services/serial-manager.service.ts`
- `praxis/web-client/src/app/core/services/serial-manager.service.spec.ts`
- `praxis/web-client/src/assets/shims/web_serial_shim.py`
- `praxis/web-client/src/app/features/repl/jupyterlite-repl.component.ts`

---

## Remaining Work (Still Active)

The following items remain in `hardware_connectivity.md`:

- Physical Connection Testing (Hamilton Starlet validation)
- Hamilton E2E Validation
- Dynamic Hardware Definitions (VID/PID sync)
