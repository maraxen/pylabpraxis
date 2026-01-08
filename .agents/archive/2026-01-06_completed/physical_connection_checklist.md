# Physical Connection Checklist - Browser Mode Hamilton Testing

**Priority**: P1 (Critical for First Light)
**Owner**: Full Stack
**Created**: 2026-01-06
**Status**: Planning

---

## Overview

This document provides a comprehensive verification checklist for testing physical hardware connectivity in **Browser Mode** with a Hamilton liquid handler. Browser mode operates entirely in the frontend using:

- **WebSerial API** for USB serial communication
- **Pyodide** (Python in WebAssembly) for protocol execution  
- **WebBridgeIO** for routing PLR commands through the browser to hardware

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Browser (Frontend Only)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐  │
│  │  Angular UI     │────▶│ HardwareDiscovery │────▶│  WebSerial API  │  │
│  │  Components     │     │    Service        │     │   (navigator.   │  │
│  └─────────────────┘     └──────────────────┘     │    serial)      │  │
│           │                       │               └────────┬────────┘  │
│           │                       │                        │           │
│           ▼                       ▼                        ▼           │
│  ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐  │
│  │ PythonRuntime   │────▶│  python.worker   │────▶│  WebBridgeIO    │  │
│  │   Service       │     │   (WebWorker)    │     │   (Python)      │  │
│  └─────────────────┘     └──────────────────┘     └─────────────────┘  │
│                                   │                        │           │
│                                   ▼                        │           │
│                          ┌──────────────────┐              │           │
│                          │  Pyodide WASM    │──────────────┘           │
│                          │  + PyLabRobot    │                          │
│                          └──────────────────┘                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ USB Serial
                          ┌──────────────────┐
                          │  Hamilton STAR   │
                          │  Liquid Handler  │
                          └──────────────────┘
```

---

## Phase 1: Browser Environment Prerequisites

### 1.1 Browser Compatibility

- [ ] **Chrome/Edge 89+** - Required for WebSerial API
- [ ] **Secure Context** - Must be HTTPS or localhost
- [ ] **WebSerial Feature Flag** - Verify `navigator.serial` exists

```javascript
// Console check
console.log('WebSerial:', 'serial' in navigator);
console.log('WebUSB:', 'usb' in navigator);
```

### 1.2 Pyodide Runtime

- [ ] **Pyodide Loads** - INIT_COMPLETE message received
- [ ] **PyLabRobot Installed** - `micropip.install(['pylabrobot'])` succeeds
- [ ] **WebBridge Loaded** - `web_bridge.py` accessible in Pyodide FS
- [ ] **REPL Functional** - Can execute `print("hello")` in REPL

### 1.3 Known Device Registry

Verify VID/PID mappings in `hardware-discovery.service.ts`:

| Device | VID:PID | Expected |
|--------|---------|----------|
| Hamilton STAR | 0x08BB:0x0106 | ✓ Recognized |
| Hamilton Starlet | 0x08BB:0x0107 | ✓ Recognized |
| Opentrons OT-2 | 0x04D8:0xE11A | ✓ Recognized |

---

## Phase 2: Hardware Discovery

### 2.1 WebSerial Port Request

- [ ] **Discovery Button Visible** - USB icon shown in UI
- [ ] **Browser Permission Prompt** - `requestPort()` triggers native dialog
- [ ] **Port Appears in List** - Selected port added to `discoveredDevices`
- [ ] **Device Identified** - VID/PID matched to Hamilton

### 2.2 Device Recognition

- [ ] **Manufacturer Detected** - "Hamilton" shown
- [ ] **Model Detected** - "STAR" or "Starlet" shown  
- [ ] **PLR Backend Inferred** - `pylabrobot.liquid_handling.backends.hamilton.STAR`
- [ ] **Status: Available** - Device ready for connection

### 2.3 Authorized Ports Persistence

- [ ] **Port Remembered** - After page refresh, authorized ports reappear via `getPorts()`
- [ ] **Re-discovery Works** - Can reconnect without re-prompting

---

## Phase 3: Serial Connection

### 3.1 Port Open

- [ ] **Open Succeeds** - `device.port.open({ baudRate: 9600 })`
- [ ] **Baud Rate Correct** - Hamilton uses 9600 (verify with device docs)
- [ ] **Reader/Writer Obtained** - Streams initialized
- [ ] **Status: Connected** - UI reflects connected state

### 3.2 Connection Tracking

- [ ] **openPorts Map Updated** - Device added to internal tracking
- [ ] **isPortOpen() Returns True** - Status queryable
- [ ] **Multiple Ports Support** - Can open additional devices simultaneously

---

## Phase 4: WebBridgeIO Integration

### 4.1 IO Patching

- [ ] **Machine Created** - `LiquidHandler(backend=STAR())`
- [ ] **IO Patched** - `patch_io_for_browser(machine, port_id)` applied
- [ ] **WebBridgeIO Attached** - Backend's `io` attribute replaced

### 4.2 Command Flow (Python → JS → Hardware)

```
Python Code        →  WebBridgeIO._send_io_command()
                   →  postMessage({type: 'RAW_IO', payload: {...}})
                   →  python.worker.ts forwards to main thread
                   →  PythonRuntimeService.handleRawIO()
                   →  HardwareDiscoveryService.writeToPort()
                   →  WebSerial writer.write()
                   →  USB → Hamilton
```

### 4.3 Response Flow (Hardware → JS → Python)

```
Hamilton USB       →  WebSerial reader.read()
                   →  HardwareDiscoveryService.readFromPort()
                   →  postMessage({type: 'RAW_IO_RESPONSE', ...})
                   →  python.worker.ts receives
                   →  web_bridge.handle_io_response()
                   →  _pending_reads[request_id].set_result(data)
                   →  Python await completes
```

---

## Phase 5: Low-Level Communication Tests

### 5.1 Write Operations

- [ ] **Write Single Byte** - `writeToPort(portId, new Uint8Array([0x05]))`
- [ ] **Write Command** - Hamilton command format successful
- [ ] **Write Large Data** - Multi-byte commands work
- [ ] **No Data Loss** - All bytes transmitted

### 5.2 Read Operations

- [ ] **Read Fixed Size** - `readFromPort(portId, 10)` returns 10 bytes
- [ ] **Read Line** - `readLineFromPort(portId)` returns until `\n`
- [ ] **Read Timeout** - TimeoutError raised after specified duration
- [ ] **Async Future Resolution** - Pending reads complete when data arrives

### 5.3 Error Handling

- [ ] **Device Disconnected** - Error caught and reported
- [ ] **Read Timeout** - Graceful timeout handling
- [ ] **Write Failure** - Error propagated to Python

---

## Phase 6: PyLabRobot Machine Tests

### 6.1 Machine Setup

```python
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends.hamilton import STAR
import web_bridge

lh = LiquidHandler(backend=STAR())
web_bridge.patch_io_for_browser(lh, 'serial-port-id')
await lh.setup()  # ← Test this
```

- [ ] **setup() Completes** - No timeout or error
- [ ] **Firmware Query Sent** - Hamilton initialization commands transmitted
- [ ] **Response Received** - Machine acknowledges

### 6.2 Resource Assignment

```python
from pylabrobot.resources import STARDeck
deck = STARDeck()
lh.assign_child_resource(deck, rails=1)
```

- [ ] **Deck Assigned** - No errors
- [ ] **Position Tracking** - Resources have correct coordinates

### 6.3 Basic Operations (Simulated First)

Before testing with liquid, verify command transmission:

- [ ] **pick_up_tips** - Command transmitted, waiting for response
- [ ] **drop_tips** - Command transmitted
- [ ] **aspirate** - Command transmitted
- [ ] **dispense** - Command transmitted

---

## Phase 7: End-to-End Protocol Execution

### 7.1 Simple Protocol

```python
async def test_protocol(lh):
    """Minimal connectivity test - no liquid operations."""
    # Just verify we can communicate
    await lh.home()  # Or equivalent initialization
```

- [ ] **Protocol Starts** - ExecutionService triggers Pyodide
- [ ] **Commands Sent** - RAW_IO messages observed in console
- [ ] **Responses Received** - RAW_IO_RESPONSE messages observed
- [ ] **Protocol Completes** - EXEC_COMPLETE received

### 7.2 Physical Movement Test

⚠️ **SAFETY**: Ensure deck is clear before running

- [ ] **Home Command** - Robot homes successfully
- [ ] **Pipette Move** - Controlled movement observed
- [ ] **Position Feedback** - Position data returned correctly

---

## Phase 8: State Tracking & Error Recovery

### 8.1 Connection State

- [ ] **State Persists** - Connection survives short disconnects
- [ ] **Reconnection Logic** - Can re-establish after disconnect
- [ ] **Status Updates** - UI reflects current connection state

### 8.2 Error Scenarios

- [ ] **USB Cable Disconnect** - Error detected and reported
- [ ] **Browser Tab Close** - Cleanup happens gracefully
- [ ] **Pyodide Crash** - Can reinitialize without page refresh

### 8.3 State Resolution

- [ ] **Uncertain State Detected** - After failed operation
- [ ] **Resolution Dialog Shows** - User can specify actual state
- [ ] **Audit Logged** - Resolution recorded in SqliteService

---

## Phase 9: UI/UX Verification

### 9.1 Discovery UI

- [ ] **Discovery Button** - USB icon, consistent placement
- [ ] **Discovery Dialog** - Opens, shows scanning state
- [ ] **Device List** - Discovered devices displayed
- [ ] **Add to Inventory** - Can register device as machine

### 9.2 Connection Indicators

- [ ] **Status Badge** - Shows connected/disconnected
- [ ] **Error Messages** - Displayed on failures
- [ ] **Activity Indicator** - Shows when transmitting

### 9.3 REPL Integration

- [ ] **Inject Code** - Can inject machine handle from Assets tab
- [ ] **Execute Commands** - Python commands reach hardware
- [ ] **Output Display** - Responses shown in terminal

---

## Phase 10: Device Persistence in Asset Management

This phase tests that discovered and registered devices persist correctly across various scenarios.

### 10.1 Device Registration to Asset Inventory

After discovering a device via WebSerial:

- [ ] **Register as Machine** - "Add to Inventory" button works
- [ ] **Machine Appears in Assets** - Shows in Assets → Machines tab
- [ ] **Correct Backend Assigned** - PLR backend matches device (e.g., `STAR`)
- [ ] **Connection Info Saved** - Port/device ID stored with machine
- [ ] **"Physical" vs "Simulated"** - Hardware machine NOT marked as simulated

### 10.2 Page Refresh Persistence

After registering a discovered device:

- [ ] **Refresh Browser** - F5 or Cmd+R
- [ ] **Machine Still in Inventory** - Appears in Assets → Machines
- [ ] **WebSerial Re-Authorization** - Browser prompts or remembers port
- [ ] **Can Reconnect** - Port can be reopened without re-discovery
- [ ] **State Matches Pre-Refresh** - Same name, backend, config

### 10.3 Disconnect and Reconnect Scenarios

#### USB Cable Disconnect

- [ ] **Device Removed Mid-Session** - Unplug USB cable
- [ ] **Error Detected** - UI shows disconnected state
- [ ] **Machine Record Persists** - Still in inventory (not deleted)
- [ ] **Reconnect Flow** - Plug back in, device re-discoverable
- [ ] **Re-Link to Existing Machine** - Can reconnect to same machine record

#### Browser Tab Close/Reopen

- [ ] **Close Tab** - Close browser completely
- [ ] **Reopen at localhost:4200** - Fresh load
- [ ] **Machines Still in IndexedDB** - Query SqliteService shows records
- [ ] **WebSerial Requires User Gesture** - Must click to re-authorize port
- [ ] **Full Workflow Restorable** - Can re-establish hardware connection

#### Power Cycle Device

- [ ] **Turn Off Hardware** - Power cycle the Hamilton
- [ ] **Device Not Listed in Discovery** - No longer appears in `getPorts()`
- [ ] **Machine Record Unchanged** - Inventory still shows machine
- [ ] **Power On Hardware** - Device reappears
- [ ] **Re-authorize Port** - Works correctly

### 10.4 IndexedDB Persistence Layer

Browser mode stores data in IndexedDB via sql.js:

- [ ] **Database Initialized** - `praxis.db` loaded on startup
- [ ] **Asset Tables Exist** - `assets`, `machines`, `resources` tables
- [ ] **CRUD Operations Work** - Create, read, update, delete
- [ ] **Persistence Across Sessions** - Data survives browser restart
- [ ] **No Data Corruption** - Table integrity maintained

### 10.5 Multi-Device Scenarios

If multiple devices are connected:

- [ ] **Discover Multiple Ports** - List shows all authorized devices
- [ ] **Register Both** - Can add multiple machines
- [ ] **Distinct Entries** - Each has unique accession_id
- [ ] **Individual Reconnection** - Can reconnect to each independently
- [ ] **Correct Port Binding** - Each machine uses its own port

### 10.6 Machine Deletion

- [ ] **Delete Machine from Inventory** - Via Assets → Machines
- [ ] **Confirmation Dialog** - "Are you sure?"
- [ ] **Machine Removed** - No longer in list
- [ ] **Port Still Authorized** - WebSerial permission retained
- [ ] **Can Re-Discover** - Device shows up in discovery again
- [ ] **Can Re-Register** - Add as new machine works

---

## Testing Matrix

| Test | Hamilton STAR | Hamilton Starlet | Notes |
|------|---------------|------------------|-------|
| WebSerial Discovery | ⬜ | ⬜ | VID/PID match |
| Port Open | ⬜ | ⬜ | 9600 baud |
| WebBridgeIO Patch | ⬜ | ⬜ | STAR backend |
| setup() | ⬜ | ⬜ | Firmware init |
| home() | ⬜ | ⬜ | Physical movement |
| pick_up_tips | ⬜ | ⬜ | Command format |
| Full Protocol | ⬜ | ⬜ | E2E validation |
| **Persistence Tests** | | | |
| Register to Inventory | ⬜ | ⬜ | Creates machine record |
| Refresh Persistence | ⬜ | ⬜ | Survives F5 |
| Disconnect/Reconnect | ⬜ | ⬜ | USB unplug recovery |
| Session Persistence | ⬜ | ⬜ | Survives tab close |

---

## Known Limitations

1. **No Backend Fallback** - Browser mode cannot fall back to server-side hardware access
2. **Single Browser Only** - Hardware locked to one browser tab
3. **WebSerial Permission Scope** - User must grant permission each session (unless remembered)
4. **Pyodide Startup Time** - Initial load of WASM + PLR takes ~10-30 seconds
5. **No Multi-User** - Hardware cannot be shared between users in browser mode
6. **IndexedDB Quotas** - Browser may clear storage under pressure (rare on desktop)
7. **No Cross-Tab Communication** - Each tab maintains separate Pyodide instance

---

## Debug Checklist

If something fails, check in order:

1. **Console Errors** - F12 → Console tab
2. **WebSerial Logs** - `[HardwareDiscovery]` prefixed messages
3. **Worker Messages** - `RAW_IO` / `RAW_IO_RESPONSE` in Network tab (if using SharedWorker)
4. **Python Errors** - `STDERR` messages in REPL output
5. **Device Power** - Is Hamilton powered on and ready?
6. **USB Connection** - Try different port/cable
7. **Baud Rate** - Confirm 9600 or device-specific rate
8. **IndexedDB State** - F12 → Application → IndexedDB → check tables
9. **SqliteService Logs** - `[SqliteService]` prefixed console messages

---

## Files Reference

| File | Purpose |
|------|---------|
| `hardware-discovery.service.ts` | WebSerial discovery and port I/O |
| `python-runtime.service.ts` | Pyodide worker management |
| `python.worker.ts` | WebWorker for Python execution |
| `web_bridge.py` | WebBridgeIO class and IO patching |
| `plr-definitions.ts` | Known machine VID/PID mappings |
| `sqlite.service.ts` | IndexedDB/sql.js persistence layer |
| `repositories.ts` | CRUD operations for assets |
| `asset.service.ts` | Asset management logic |
| `machine-dialog.component.ts` | Machine add/edit dialog |

---

## Success Criteria

- [ ] Can discover Hamilton via WebSerial
- [ ] Can open serial connection
- [ ] Python code in REPL can execute `await lh.setup()`
- [ ] Commands reach hardware (observe lights/movement)
- [ ] Responses received in Python
- [ ] Can run simple protocol end-to-end
- [ ] **Registered machines persist in IndexedDB**
- [ ] **Machines survive page refresh**
- [ ] **Can reconnect after USB disconnect**
- [ ] **Multi-session persistence works**

---

## Test Execution Log

Use this section to record test results:

| Date | Tester | Phase | Result | Notes |
|------|--------|-------|--------|-------|
| | | | | |
| | | | | |
| | | | | |

---

## Related Documents

- [modes_and_deployment.md](./modes_and_deployment.md) - Browser mode architecture
- [hardware_discovery_menu.md](./hardware_discovery_menu.md) - Discovery UI specs
- [browser_mode_issues.md](./browser_mode_issues.md) - Known browser mode issues
- [repl_jupyterlite.md](./repl_jupyterlite.md) - REPL enhancements
- [browser_mode_defaults.md](./browser_mode_defaults.md) - Default asset population
- [browser_sqlite_schema_sync.md](./browser_sqlite_schema_sync.md) - IndexedDB schema details
- [error_handling_state_resolution.md](./error_handling_state_resolution.md) - Error recovery workflows
