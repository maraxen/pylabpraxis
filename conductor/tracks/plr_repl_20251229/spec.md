# Specification: PyLabRobot REPL (Interactive Hardware Control)

## 1. Overview

The PyLabRobot REPL provides an interactive Python console for direct hardware control, prototyping commands, and live experimentation. It enables power users and automation engineers to interact with devices via PyLabRobot in real-time without deploying a full protocol. This track also introduces robust state export/import capabilities for both Praxis and PLR.

## 2. Goals

* **Interactive REPL:** A Python REPL (IPython-like) accessible from the Praxis UI for live PLR command execution.
* **Device Discovery:** Client-side device discovery UI that enumerates available hardware (simulators, serial devices, network devices).
* **State Export/Import:** First-class support for exporting and restoring the complete state of a workcell, including liquid volumes, tip status, and resource positions.
* **Session Persistence:** REPL sessions can be saved/restored, enabling reproducible debugging workflows.

## 3. Functional Requirements

### 3.1 Device Discovery Service

* **Backend Discovery API:**
  * `GET /api/v1/hardware/discover` - Enumerate all discoverable devices:
    * Simulated backends (always available)
    * Serial ports (USB-connected devices)
    * Network devices (via mDNS/manual IP entry)
  * Return device metadata: type, connection status, last seen, driver class.
* **Frontend Discovery UI:**
  * "Discover Devices" panel in the Assets section.
  * Show discovered devices with connect/disconnect actions.
  * Device cards display: Name, Type, Status Indicator, Connection Method.
* **Connection Management:**
  * `POST /api/v1/hardware/connect` - Initialize a device connection.
  * `POST /api/v1/hardware/disconnect` - Gracefully close a connection.
  * Connection state persisted in Redis for session continuity.

### 3.2 REPL Interface

* **Backend REPL Service:**
  * IPython kernel running in a background process/thread.
  * WebSocket endpoint (`/ws/repl`) for bidirectional I/O.
  * Pre-configured namespace with:
    * Current workcell (`workcell`)
    * Active liquid handler (`lh`)
    * All assigned resources (`plates`, `tip_racks`, etc.)
    * Helper functions (`pick_up_tips()`, `aspirate()`, `dispense()`, etc.)
  * Command history persisted per user.
* **Frontend REPL Component:**
  * Terminal-like interface (xterm.js or similar).
  * Syntax highlighting for Python.
  * Autocomplete support (via Jedi/LSP).
  * Output panel for results: stdout, stderr, and rich outputs (images, tables).
  * "Run Selection" to execute highlighted code snippets.
* **Safety Features:**
  * Read-only mode toggle (disables hardware mutations).
  * Confirmation prompts for destructive operations (tip eject, large volume transfers).
  * Rate limiting to prevent command flooding.

### 3.3 State Export/Import

#### 3.3.1 PLR State (PyLabRobot Layer)

* **Export:**
  * Full deck serialization via `resource.serialize()`.
  * Tracker state (tip counts, liquid volumes) via `serialize_all_state()`.
  * Output format: JSON file.
* **Import:**
  * Load deck structure via `Resource.deserialize()`.
  * Restore tracker state via `load_all_state()`.
  * Validation: Check for resource name conflicts, missing definitions.

#### 3.3.2 Praxis State (Application Layer)

* **Export:**
  * Current `PraxisState` dictionary (Redis-backed).
  * Run history for the active session.
  * Asset assignments and reservations.
  * Output format: JSON file with schema version.
* **Import:**
  * Merge or replace state into Redis.
  * Re-establish asset reservations.
  * Emit state change events to connected clients.

#### 3.3.3 Combined State Bundle

* **Export:**
  * ZIP archive containing:
    * `plr_state.json` - PLR deck and tracker state.
    * `praxis_state.json` - Application state.
    * `metadata.json` - Timestamp, version, user.
* **Import:**
  * Unpack and validate bundle.
  * Atomic restore of both layers.
  * Rollback on failure.

### 3.4 State Export/Import UI

* **Export UI:**
  * "Export State" button in the REPL toolbar and Asset Manager.
  * Options: Include run history, include logs.
  * Download as `.praxis-state` file.
* **Import UI:**
  * "Import State" button with file picker.
  * Preview panel showing what will be restored.
  * Conflict resolution for duplicate names.

## 4. API Specification

### 4.1 Device Discovery

```
GET /api/v1/hardware/discover
Response: { devices: [{ id, name, type, driver_class, connection_status, last_seen }] }

POST /api/v1/hardware/connect
Body: { device_id, connection_params: {...} }
Response: { success, device_id, connection_handle }

POST /api/v1/hardware/disconnect
Body: { connection_handle }
Response: { success }
```

### 4.2 REPL

```
WebSocket /ws/repl
Messages:
  -> { type: "execute", code: "..." }
  <- { type: "output", stream: "stdout", content: "..." }
  <- { type: "output", stream: "stderr", content: "..." }
  <- { type: "result", data: {...}, repr: "..." }
  <- { type: "complete", success: bool }
  -> { type: "complete_request", code: "...", cursor_pos: N }
  <- { type: "complete_response", matches: [...] }
```

### 4.3 State Export/Import

```
GET /api/v1/state/export
Query: ?include_plr=true&include_praxis=true&include_history=false
Response: application/octet-stream (ZIP file)

POST /api/v1/state/import
Body: multipart/form-data (ZIP file)
Response: { success, imported: { plr_resources: N, praxis_keys: N } }

GET /api/v1/state/export/preview
Response: { plr: { resources: [...] }, praxis: { keys: [...] }, conflicts: [...] }
```

## 5. Non-Functional Requirements

* **Latency:** REPL command execution should feel instant (<200ms for simple commands).
* **Isolation:** REPL sessions are isolated per user; one user's commands don't affect another's view.
* **Security:** REPL access is gated by role (Admin/Engineer only). State import requires admin privileges.
* **Robustness:** REPL kernel crashes should not take down the main backend; kernels are restarted automatically.

## 6. Acceptance Criteria

* [ ] User can view a list of discoverable devices (simulators always present).
* [ ] User can connect to a simulated liquid handler from the UI.
* [ ] REPL opens with pre-loaded namespace (`lh`, `workcell` available).
* [ ] User can execute `lh.pick_up_tips(...)` and see real-time feedback.
* [ ] Autocomplete works for PLR objects and methods.
* [ ] User can export current state as a downloadable file.
* [ ] User can import a state bundle and see resources restored.
* [ ] State import shows preview and handles conflicts gracefully.
* [ ] REPL session persists across page refresh (reconstructed from state).

## 7. Dependencies

* **Hardware Bridge Track:** Device connection infrastructure (partially overlaps).
* **WebSocket Infrastructure:** Real-time log streaming (already exists for protocol runs).
* **PLR Serialization:** `serialize()` and `deserialize()` methods in PyLabRobot.

## 8. Out of Scope (Phase 1)

* Multi-user collaborative REPL sessions.
* REPL command recording to protocol conversion.
* Hardware debugging tools (oscilloscope integration, motor diagnostics).
* Version control for state snapshots (future: Git-like state history).
