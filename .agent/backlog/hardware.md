# Hardware Validation

**Created**: 2026-01-09
**Priority**: P2 (Required for Alpha)

---

## Overview

Browser-mode hardware connectivity is **required for v0.1.0-alpha**. These items validate that users can discover, connect to, and control hardware directly from the browser.

---

## P2: Hardware Discovery (Browser Mode)

**Status**: 🔄 Partially Implemented
**Difficulty**: Hard

### Problem
WebSerial/WebUSB device enumeration must work in browser mode.

### Tasks
- [ ] Test WebSerial device listing
- [ ] Test WebUSB device enumeration
- [ ] Test device identification (VID/PID matching)
- [ ] Verify browser permission flows
- [ ] Document supported devices and drivers

### Evidence (from 2026-01-20 Recon)
- ✅ `HardwareDiscoveryService.ts` has robust WebSerial/WebUSB discovery logic
- ✅ `KNOWN_DEVICES` registry with VID/PID for Hamilton STARlet (0x08BB:0x0107), STAR (0x08BB:0x0106), BMG CLARIOstar (0x0403:0xBB68), Opentrons OT-2 (0x04D8:0xE11A)
- ❌ No E2E tests for physical discovery (CI/CD limitations)
- ❌ No validation logs or "Flight Checklists" found

---

## P2: Connection Persistence

**Status**: Open
**Difficulty**: Medium

### Problem
Hardware connections should persist correctly across sessions.

### Tasks
- [ ] Test connection state across page refresh
- [ ] Test reconnection after device disconnect
- [ ] Test connection recovery after errors
- [ ] Document persistence behavior

---

## P2: Plate Reader Validation

**Status**: Open
**Difficulty**: Medium

### Problem
Plate reader hardware connectivity was previously working but recent changes may have introduced regressions.

### Context
- Previously validated but changes made since
- May need debugging to restore functionality

### Tasks
- [ ] Connect to plate reader from browser
- [ ] Execute read operation
- [ ] Verify data returned correctly
- [ ] Test error handling
- [ ] Document any required fixes

### Evidence (from 2026-01-20 Recon)
- ✅ BMG CLARIOstar VID/PID mapped (0x0403:0xBB68)
- ✅ WebUSB discovery logic present
- ❌ Current status "Open" due to potential regressions

---

## P2: Frontend Protocol Execution (Browser Mode)

**Status**: 🔄 Partially Implemented
**Difficulty**: Hard

### Problem
Users must be able to execute protocols on connected hardware from the browser UI.

### Tasks
- [x] Execute simple protocol on connected hardware (via `startBrowserRun()`)
- [ ] Verify operation timing
- [x] Confirm state updates during execution (signals, IndexedDB persistence)
- [ ] Test pause/resume/cancel flows (Pause/Resume: ❌ Not Started, Cancel: 🔄 In Progress)
- [x] Verify execution monitor updates (LiveDashboardComponent implemented)

### Evidence (from 2026-01-20 Recon)
- ✅ `ExecutionService.startBrowserRun()` orchestrates blob fetching, machine config, worker execution
- ✅ `PythonRuntimeService.executeBlob()` sends protocol binaries to Pyodide worker
- ✅ State tracked via Angular signals and persisted to IndexedDB
- ❌ No Pause/Resume service methods or UI components
- 🔄 "Stop" button exists but `PythonRuntimeService.interrupt()` is placeholder

---

## P2: Playground Hardware

**Status**: Open
**Difficulty**: Hard

### Problem
Playground must support interactive hardware control.

### Tasks
- [ ] Connect to device from playground
- [ ] Execute commands interactively
- [ ] Verify state tracking
- [ ] Test error handling
- [ ] Test with plate reader

---

## P2: Hamilton Starlet Validation

**Status**: Open
**Difficulty**: Hard

### Problem
Hamilton Starlet hardware connectivity must be validated for alpha.

### Tasks
- [ ] Connect to Hamilton Starlet from browser
- [ ] Execute protocol on Hamilton Starlet
- [ ] Validate 96-head operations
- [ ] Test iSwap functionality
- [ ] Document any limitations

### Evidence (from 2026-01-20 Recon)
- ✅ VID/PID mapped in `KNOWN_DEVICES` registry
- ✅ `PythonRuntimeService.handleRawIO` bridge implemented for WebSerial commands
- ❌ End-to-end validation not performed
