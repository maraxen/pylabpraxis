# Plan: Hardware Bridge (Connectivity)

## Phase 1: Minimal Implementation (Demo Ready)
*   [ ] Task: Implement Backend Serial Port Enumeration.
    *   [ ] Subtask: Create endpoint `GET /api/v1/hardware/ports` to list available serial ports on the server.
    *   [ ] Subtask: Write tests for filtering/sanitizing port lists.
*   [ ] Task: Build Connection Management UI.
    *   [ ] Subtask: Create `ConnectionManagerComponent` with tabs for "USB/Serial" and "Network".
    *   [ ] Subtask: Implement Serial selection form (Port dropdown, Baud rate).
    *   [ ] Subtask: Implement Network form (IP, Port).
*   [ ] Task: Implement Driver Initialization Logic.
    *   [ ] Subtask: Create endpoint `POST /api/v1/hardware/connect` that initializes the specific PLR backend (e.g., STAR, OT2).
    *   [ ] Subtask: Ensure connection state is broadcast to all clients via WebSocket.
*   [ ] Task: Conductor - User Manual Verification 'Hardware Bridge Minimal' (Protocol in workflow.md)

## Phase 2: Full Implementation
*   [ ] Task: Implement Network Discovery (mDNS).
*   [ ] Task: Implement WebSerial Passthrough (Remote Client Support).
*   [ ] Task: Conductor - User Manual Verification 'Hardware Bridge Full' (Protocol in workflow.md)
