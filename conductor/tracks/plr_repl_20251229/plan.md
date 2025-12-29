# Plan: PyLabRobot REPL (Interactive Hardware Control)

## Phase 1: Device Discovery (Backend Foundation)

### Task 1.1: Hardware Discovery Service

* [ ] Subtask: Create `praxis/backend/services/hardware_discovery.py` with:
  * [ ] `DiscoveryService.discover_serial_ports()` - List available serial ports via `serial.tools.list_ports`.
  * [ ] `DiscoveryService.discover_simulators()` - Return list of available PLR simulator backends.
  * [ ] `DiscoveryService.discover_network_devices()` - Placeholder for future mDNS scanning.
* [ ] Subtask: Create unified `DiscoveredDevice` Pydantic model in `praxis/backend/models/pydantic/hardware.py`.
* [ ] Subtask: Write unit tests for discovery service.

### Task 1.2: Hardware Connection Management

* [ ] Subtask: Create `praxis/backend/services/hardware_connection.py` with:
  * [ ] `ConnectionManager.connect(device_id, params)` - Initialize PLR backend for device.
  * [ ] `ConnectionManager.disconnect(handle)` - Gracefully close connection.
  * [ ] `ConnectionManager.get_status(handle)` - Return connection health.
* [ ] Subtask: Store connection state in Redis with TTL for stale connection cleanup.
* [ ] Subtask: Write unit tests for connection lifecycle.

### Task 1.3: Hardware Discovery API

* [ ] Subtask: Create `praxis/backend/api/hardware.py` router with:
  * [ ] `GET /api/v1/hardware/discover` endpoint.
  * [ ] `POST /api/v1/hardware/connect` endpoint.
  * [ ] `POST /api/v1/hardware/disconnect` endpoint.
  * [ ] `GET /api/v1/hardware/connections` endpoint (list active connections).
* [ ] Subtask: Add role-based access control (Admin/Engineer only).
* [ ] Subtask: Write API integration tests.

### Task 1.4: Conductor - User Manual Verification 'Device Discovery MVP'

---

## Phase 2: Device Discovery (Frontend UI)

### Task 2.1: Discovery Data Service

* [ ] Subtask: Create `HardwareDiscoveryService` in `praxis/web-client/src/app/core/services/`:
  * [ ] `discoverDevices(): Observable<DiscoveredDevice[]>`
  * [ ] `connectDevice(device: DiscoveredDevice): Observable<ConnectionHandle>`
  * [ ] `disconnectDevice(handle: string): Observable<void>`
* [ ] Subtask: Define TypeScript interfaces for `DiscoveredDevice`, `ConnectionHandle`.

### Task 2.2: Device Discovery Component

* [ ] Subtask: Create `DeviceDiscoveryComponent` in `praxis/web-client/src/app/features/assets/`:
  * [ ] Device cards with status indicators (Connected, Available, Offline).
  * [ ] "Connect" / "Disconnect" actions on each device card.
  * [ ] "Refresh" button to re-scan.
* [ ] Subtask: Add loading skeleton during discovery.
* [ ] Subtask: Handle error states (serial port access denied, etc.).

### Task 2.3: Integration with Asset Manager

* [ ] Subtask: Add "Devices" tab to Asset Manager component.
* [ ] Subtask: Cross-link discovered devices with registered machines in the database.
* [ ] Subtask: Show connection status badges on Machine list items.

### Task 2.4: Conductor - User Manual Verification 'Device Discovery UI'

---

## Phase 3: State Export/Import (Backend)

### Task 3.1: PLR State Serialization Service

* [ ] Subtask: Create `praxis/backend/services/state_serialization.py` with:
  * [ ] `export_plr_state(workcell: IWorkcell) -> dict` - Serialize deck + tracker state.
  * [ ] `import_plr_state(workcell: IWorkcell, data: dict)` - Restore deck + tracker state.
* [ ] Subtask: Leverage existing `workcell.save_state_to_file()` / `load_state_from_file()` methods.
* [ ] Subtask: Write unit tests verifying round-trip serialization.

### Task 3.2: Praxis State Serialization Service

* [ ] Subtask: Extend `PraxisState` class with:
  * [ ] `export_to_dict() -> dict` - Full state dump with schema version.
  * [ ] `import_from_dict(data: dict, merge: bool = False)` - Restore state.
* [ ] Subtask: Include run history and asset reservations in export.
* [ ] Subtask: Write unit tests for state export/import.

### Task 3.3: Combined State Bundle Handler

* [ ] Subtask: Create `praxis/backend/services/state_bundle.py` with:
  * [ ] `create_bundle(include_plr, include_praxis, include_history) -> bytes` - ZIP creation.
  * [ ] `extract_bundle(bundle: bytes) -> BundleContents` - ZIP extraction and validation.
  * [ ] `import_bundle(bundle: BundleContents, atomic: bool = True)` - Apply state.
* [ ] Subtask: Define `BundleManifest` schema with version, timestamp, checksums.
* [ ] Subtask: Write integration tests for bundle lifecycle.

### Task 3.4: State Export/Import API

* [ ] Subtask: Create endpoints in `praxis/backend/api/state.py`:
  * [ ] `GET /api/v1/state/export` - Download state bundle.
  * [ ] `POST /api/v1/state/import` - Upload and restore bundle.
  * [ ] `GET /api/v1/state/export/preview` - Preview current exportable state.
  * [ ] `POST /api/v1/state/import/preview` - Preview import contents and conflicts.
* [ ] Subtask: Require admin role for import operations.
* [ ] Subtask: Write API integration tests.

### Task 3.5: Conductor - User Manual Verification 'State Export/Import MVP'

---

## Phase 4: REPL Backend

### Task 4.1: REPL Kernel Service

* [ ] Subtask: Create `praxis/backend/core/repl/kernel.py` with:
  * [ ] IPython kernel initialization with custom namespace.
  * [ ] Pre-loaded objects: `workcell`, `lh`, helper functions.
  * [ ] Execution method returning stdout, stderr, result.
* [ ] Subtask: Implement kernel isolation (separate thread/process per session).
* [ ] Subtask: Handle kernel crashes with automatic restart.

### Task 4.2: REPL WebSocket Handler

* [ ] Subtask: Create `praxis/backend/api/repl_ws.py` WebSocket endpoint `/ws/repl`.
* [ ] Subtask: Message types: `execute`, `output`, `result`, `complete`, `complete_request`.
* [ ] Subtask: Integrate with existing WebSocket infrastructure.
* [ ] Subtask: Add user authentication for WebSocket connection.

### Task 4.3: Command Completions

* [ ] Subtask: Integrate Jedi for Python autocompletion.
* [ ] Subtask: Expose `complete_request` message type returning completion matches.
* [ ] Subtask: Write tests for completion accuracy.

### Task 4.4: Session Persistence

* [ ] Subtask: Store command history per user in Redis.
* [ ] Subtask: Store kernel namespace snapshot for session restore.
* [ ] Subtask: Implement `GET /api/v1/repl/history` endpoint.

### Task 4.5: Conductor - User Manual Verification 'REPL Backend MVP'

---

## Phase 5: REPL Frontend

### Task 5.1: Terminal Component

* [ ] Subtask: Install and configure `xterm.js` in Angular project.
* [ ] Subtask: Create `ReplTerminalComponent` with:
  * [ ] Terminal rendering with Python syntax highlighting.
  * [ ] WebSocket connection to `/ws/repl`.
  * [ ] Input handling with command history (up/down arrows).

### Task 5.2: Autocomplete Integration

* [ ] Subtask: Trigger `complete_request` on Tab key press.
* [ ] Subtask: Display completion popup menu.
* [ ] Subtask: Apply selected completion to input.

### Task 5.3: Rich Output Panel

* [ ] Subtask: Create `ReplOutputComponent` for non-text outputs:
  * [ ] Image rendering (matplotlib plots from PLR visualizer).
  * [ ] Table rendering (pandas DataFrames).
  * [ ] Error highlighting with traceback parsing.
* [ ] Subtask: Scrollback buffer with configurable limit.

### Task 5.4: REPL Toolbar

* [ ] Subtask: Add toolbar with:
  * [ ] "Clear Output" button.
  * [ ] "Export State" button (triggers state export).
  * [ ] "Read-Only Mode" toggle.
  * [ ] "Restart Kernel" button.
* [ ] Subtask: Display kernel status indicator (Running, Busy, Crashed).

### Task 5.5: Integration with Main Layout

* [ ] Subtask: Add REPL as a toggleable bottom panel (similar to browser dev tools).
* [ ] Subtask: Add keyboard shortcut to toggle REPL (Ctrl+`).
* [ ] Subtask: Persist REPL open/closed state in localStorage.

### Task 5.6: Conductor - User Manual Verification 'REPL Frontend MVP'

---

## Phase 6: State Export/Import (Frontend UI)

### Task 6.1: State Export UI

* [ ] Subtask: Add "Export State" action to Asset Manager toolbar.
* [ ] Subtask: Create `StateExportDialogComponent` with:
  * [ ] Checkboxes: Include PLR state, Include Praxis state, Include history.
  * [ ] Preview of what will be exported.
  * [ ] "Download" button triggering file download.

### Task 6.2: State Import UI

* [ ] Subtask: Add "Import State" action to Asset Manager toolbar.
* [ ] Subtask: Create `StateImportDialogComponent` with:
  * [ ] File picker for `.praxis-state` bundles.
  * [ ] Preview panel showing resources/keys to be imported.
  * [ ] Conflict resolution UI for duplicate names.
  * [ ] "Import" button with confirmation.

### Task 6.3: Conductor - User Manual Verification 'State Export/Import UI'

---

## Phase 7: Polish & Safety

### Task 7.1: Safety Confirmations

* [ ] Subtask: Add confirmation modal for destructive REPL commands.
* [ ] Subtask: Implement rate limiting for REPL commands (max 10/sec).
* [ ] Subtask: Log all REPL commands for audit trail.

### Task 7.2: Error Handling Polish

* [ ] Subtask: Graceful error messages for serial port permission issues.
* [ ] Subtask: Handle WebSocket disconnects with reconnect logic.
* [ ] Subtask: Handle state import validation failures with actionable messages.

### Task 7.3: Documentation

* [ ] Subtask: Add REPL user guide to docs.
* [ ] Subtask: Document state bundle format for interoperability.
* [ ] Subtask: Add example scripts for common REPL workflows.

### Task 7.4: Conductor - User Manual Verification 'REPL Polish & Safety'

---

## Notes

### Coordination with Hardware Bridge Track

The Hardware Bridge track (`hardware_bridge_20251223`) covers similar ground for device connectivity. Key differences:

* **Hardware Bridge:** Focuses on production protocol execution with robust connection management.
* **REPL Track:** Focuses on interactive exploration and debugging.

Shared infrastructure:

* Serial port enumeration (`/api/v1/hardware/ports` from Hardware Bridge).
* Connection state storage in Redis.

To avoid duplication, Phase 1 of this track should reuse/extend the Hardware Bridge service where applicable.

### PLR Serialization Capabilities

PyLabRobot provides:

* `resource.serialize()` → JSON representation of resource structure.
* `resource.serialize_all_state()` → Tracker state (tips, volumes).
* `resource.save_state_to_file(fn)` → Combined structure + state to file.
* `Resource.deserialize(data)` → Reconstruct from JSON.
* `resource.load_state_from_file(fn)` → Restore state.

These methods are the foundation for Phase 3.
