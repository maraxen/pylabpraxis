# Draft Roadmap: Pathway to "Solid Demo"

This document outlines the proposed development tracks to achieve a high-quality, feature-complete demo of PyLabPraxis.

**Goal:** A polished, interactive system demonstrating hardware connectivity, real-time visualization, data analysis, and power-user workflows.

---

## 🔌 Track 1: Hardware Bridge (Connectivity)

**Focus:** Bridge the gap between the web client and physical hardware via Network and WebSerial.

### Minimal Implementation (Demo Ready)

* **WebSerial Passthrough:** A "Connect" button in the UI that requests a WebSerial port, grabs the handle, and routes traffic to a backend Python driver instance (or bridges it via a local proxy).
* **Manual IP Connect:** Simple form to input an IP address for network-connected robots (e.g., Opentrons, Hamilton Vantage).
* **Connection Status:** Visual indicator of connection state (Connected/Connecting/Error).

### Full Implementation

* **Network Discovery:** Background mDNS/Zeroconf scanning to auto-detect devices on the local network.
* **Driver Routing:** Robust multiplexing to allow multiple web clients to "share" or "lock" access to a single hardware driver.
* **Device Profiles:** Saved configurations for known lab hardware.

---

## 👁️ Track 2: Interactive Deck (Visualizer Integration)

**Focus:** Integrate the PyLabRobot (PLR) visualizer into the Angular frontend.
**Context:** Currently, there is no PLR visualizer integration.

### Minimal Implementation (Completed)

* [x] **Render Component:** Embed the PLR visualizer inside an Angular component (`<app-deck-visualizer>`).
* [x] **Static Snapshot:** Render the *initial* state of the deck based on a mocked layout (Track 2: Minimal Integration). Refresh logic deferred to Full Implementation.

### Full Implementation

* **Real-Time WebSocket Sync:** Live updates of arm movements, tip pickups, and liquid transfers.
* **Interactive Config:** Drag-and-drop resources from a sidebar onto the visualizer slots to configure the deck before a run.
* **3D/2D Toggle:** Switch between a simplified top-down view and a rich 3D representation.

---

## 📊 Track 3: Data Insights (Visualization)

**Focus:** Visualizing experimental results and telemetry.
**Tech Strategy:** Use **Plotly.js** (via `angular-plotly.js`) for TypeScript-native rendering that aligns with the scientific Python ecosystem (users are familiar with Plotly).

### Minimal Implementation (Demo Ready)

* **Plate Heatmap:** A 96-well grid view showing "status" (Empty, Filled, Processed) or a simulated metric (Absorbance).
* **Live Telemetry Chart:** A simple line chart showing a simulated sensor value (e.g., "Temperature" or "Shaker Speed") over time during the run.

### Full Implementation

* **Interactive Dashboards:** User-configurable widgets (Histograms, Scatter plots).
* **Data Export:** One-click CSV/Excel/JSON export of run data.
* **Comparison View:** Overlay results from previous runs.

---

## ⚡ Track 4: Workflow Velocity (Polish & Speed)

**Focus:** Professional grade UX, keyboard shortcuts, and UI responsiveness.

### Minimal Implementation (Demo Ready)

* **Command Palette:** `Cmd+K` / `Ctrl+K` menu to jump to protocols, assets, or settings instantly.
* [x] **Context Menus:** Basic right-click support on assets/steps for quick actions.
* **Safe Shortcuts:** Modifier-based navigation shortcuts (e.g., `Cmd+P` for Protocols, `Cmd+R` for Resources, `Cmd+M` for Machines) to avoid input conflicts.

### Full Implementation

* **Advanced Hotkeys:** "Safe" hotkeys for critical actions (e.g., `Hold Shift + Esc` to Stop).
* **Micro-interactions:** Smooth transitions, loading skeletons, and "snappy" feedback.

---

## 🎭 Track 5: The "Golden Path" (Demo Content)

**Focus:** Orchestrating the specific scenario for the demo.

### Minimal Implementation (Demo Ready)

* **Scripted Protocol:** A robust version of `simple_transfer.py` that reliably runs in simulation mode.
* **Mock Data Generator:** A backend service that emits realistic "fake" sensor data to populate the Track 3 charts during the demo.
* **Narrative Flow:** A documented script: "Login -> Select Protocol -> Auto-fill Assets -> Visualize Deck -> Run -> See Live Data -> Pause/Resume -> Finish."

### Full Implementation

* **Error Recovery Scenario:** A protocol designed to "fail" (simulated error), demonstrating the system's error handling and user recovery workflow.
* **Complex Multi-Workcell Run:** Simulating a run that spans multiple machines.
