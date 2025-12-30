# Specification: Hardware Bridge (Connectivity)

## 1. Overview
The goal of this track is to enable the PyLabPraxis web client to communicate with physical lab hardware. Currently, the system operates primarily in simulation. This track bridges that gap using WebSerial for local USB connections and network sockets for IP-based devices.

## 2. Goals
*   **WebSerial Passthrough:** Allow browser-based USB selection to route to backend drivers.
*   **Manual IP Connection:** Provide a UI for connecting to networked robots (Opentrons, Hamilton, etc.).
*   **Connection Management:** Robustly handle connection state, disconnects, and driver initialization.

## 3. Minimal Implementation (Demo Ready)
*   **WebSerial UI:** A "Connect USB" button that invokes the browser's Serial API.
*   **Serial Proxy:** A mechanism (websocket or specialized endpoint) to pipe serial data from the browser to the backend PLR driver, OR a backend-initiated local serial connection (if browser-passthrough is too complex for MVP, backend-local selection is acceptable for localhost demos).
    *   *Decision:* For MVP on localhost, we will prioritize **Backend-Local Serial Selection**. The UI will list ports available to the *server*, and the user selects one. WebSerial passthrough is a Phase 2 feature for remote clients.
*   **IP Connection Form:** Input fields for Host/Port.
*   **Visual Feedback:** Clear indicators for "Connecting...", "Connected", "Error".

## 4. Full Implementation (Post-Demo)
*   **Network Discovery:** Background mDNS/Zeroconf scanning to populate the connection list automatically.
*   **Driver Routing:** Multiplexing to allow multiple sessions to view the same hardware status.
*   **Device Profiles:** persistent configuration for specific lab setups.

## 5. Constraints
*   **Security:** Serial port access must be secure.
*   **Latency:** Control loops must be tight enough for reliable operation.
