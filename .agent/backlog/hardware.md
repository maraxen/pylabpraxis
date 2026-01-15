# Hardware Validation

**Created**: 2026-01-09
**Priority**: P2 (Required for Alpha)

---

## Overview

Browser-mode hardware connectivity is **required for v0.1.0-alpha**. These items validate that users can discover, connect to, and control hardware directly from the browser.

---

## P2: Hardware Discovery (Browser Mode)

**Status**: Open
**Difficulty**: Hard

### Problem
WebSerial/WebUSB device enumeration must work in browser mode.

### Tasks
- [ ] Test WebSerial device listing
- [ ] Test WebUSB device enumeration
- [ ] Test device identification (VID/PID matching)
- [ ] Verify browser permission flows
- [ ] Document supported devices and drivers

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

---

## P2: Frontend Protocol Execution (Browser Mode)

**Status**: Open
**Difficulty**: Hard

### Problem
Users must be able to execute protocols on connected hardware from the browser UI.

### Tasks
- [ ] Execute simple protocol on connected hardware
- [ ] Verify operation timing
- [ ] Confirm state updates during execution
- [ ] Test pause/resume/cancel flows
- [ ] Verify execution monitor updates

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
