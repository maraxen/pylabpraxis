# Hardware Connectivity

**Priority**: P2 (High)
**Owner**: Full Stack
**Created**: 2026-01-06 (consolidated from 5 files)
**Status**: Active

---

## Overview

This document consolidates all hardware connectivity work including physical connections, driver architecture, and hardware discovery.

---

## 1. CLARIOstar Plate Reader ✅ RESOLVED

The CLARIOstar connectivity issue has been **fixed** by implementing a Python-side FTDI WebUSB driver in `web_serial_shim.py`.

### Solution

- **Direct WebUSB Access:** Uses `navigator.usb` via Pyodide's `js` module from the worker
- **FTDI Protocol:** Implements Reset, Baud Rate, Data Characteristics, Status Byte stripping in Python
- **Fallback Chain:** Native WebSerial → Polyfill → FTDI WebUSB (VendorID 0x0403)
- **Baud Rate:** 125000 for CLARIOstar

### Files Affected

- `praxis/web-client/src/assets/shims/web_serial_shim.py`

---

## 2. FTDI Driver Architecture Refactor ✅

The serial communication layer has been abstracted to support multiple driver types, including a browser-side FTDI WebUSB implementation.

### Status: Phase A Complete (2026-01-07)

- [x] Documented architecture in `praxis/web-client/src/app/features/repl/README.md`.
- [x] Created `ISerial` and `ISerialDriver` interfaces for abstraction.
- [x] Implemented `FtdiSerial` TypeScript driver (ports baud rate/parity/stop bits logic).
- [x] Created `DriverRegistry` for automatic device-to-driver matching.
- [x] Implemented `MockSerial` for unit tests and offline dev.

### Status: Phase B Complete (2026-01-07)

- [x] Move actual runtime I/O from Python worker to TypeScript main thread.
- [x] Implement message-passing protocol between worker and host for serial data.
- [x] Convert `web_serial_shim.py` into a thin proxy (`SerialProxy` class).

**New Files:**

- `praxis/web-client/src/app/core/services/serial-manager.service.ts`
- `praxis/web-client/src/app/core/services/serial-manager.service.spec.ts`

**Modified Files:**

- `praxis/web-client/src/assets/shims/web_serial_shim.py`
- `praxis/web-client/src/app/features/repl/jupyterlite-repl.component.ts`

---

## 3. Physical Connection Testing

Hamilton Starlet WebSerial connectivity validation checklist.

### Pre-requisites

- [ ] Physical Hamilton Starlet available
- [ ] USB cable connected
- [ ] Chrome browser (WebSerial support)

### Test Cases

| Test | Expected Result | Status |
|------|-----------------|--------|
| Device detection via WebSerial | Device appears in picker | ⏳ |
| Connection establishment | No errors, status: Connected | ⏳ |
| Basic command/response | LH responds to status query | ⏳ |
| Protocol execution | Simple transfer completes | ⏳ |

See `physical_connection_checklist.md` in archive for detailed testing steps.

---

## 4. Hardware Discovery Menu

The hardware discovery button/menu allows users to discover and register connected devices.

### Components

- `HardwareDiscoveryButtonComponent` - Trigger for discovery
- `HardwareDiscoveryService` - WebSerial/WebUSB enumeration

### Known Issues

- [ ] `KNOWN_DEVICES` map is hardcoded (see section 5)

---

## 5. Dynamic Hardware Definitions (VID/PID Sync)

**Technical Debt Item** - Currently tracked in `TECHNICAL_DEBT.md`

### Problem

`HardwareDiscoveryService` uses hardcoded `KNOWN_DEVICES` map for VID/PID → PLR backend mapping.

### Solution

1. **Backend**: Inspect PLR backend classes for `USB_VENDOR_ID`/`USB_PRODUCT_ID`
2. **API**: Expose `/api/hardware/definitions` with supported devices
3. **Frontend**: Dynamically build WebSerial filter list

### Tasks

- [ ] Enhance `MachineTypeDefinitionService` to extract VID/PID from backends
- [ ] Create hardware definitions API endpoint
- [ ] Update `HardwareDiscoveryService` to use dynamic list

---

## Related Documents

- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - VID/PID sync tracked here
- Archive: `physical_connection_checklist.md`, `hardware_discovery_menu.md`
