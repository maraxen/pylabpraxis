# Specification: The "Golden Path" (Demo Content)

## 1. Overview
This track defines the content and narrative for the "Solid Demo." It ensures that all the features built in other tracks come together in a cohesive, scripted story that highlights the platform's strengths.

## 2. Goals
*   **Narrative Flow:** A documented script for the demo presentation.
*   **Reliable Protocol:** A "hardened" version of `simple_transfer.py` guaranteed to work in simulation.
*   **Mock Data:** Realistic fake data generation to populate charts and logs, making the system feel "alive" without real hardware.

## 3. Minimal Implementation (Demo Ready)
*   **The Script:**
    1.  Login & Dashboard Overview.
    2.  Select `simple_transfer` Protocol.
    3.  Auto-fill Assets (Show "Availability" logic).
    4.  Visualize Deck (Show initial state).
    5.  Run (Simulation Mode).
    6.  See Live Logs & Telemetry (Mock Temp/Speed).
    7.  Command Palette Navigation (`Cmd+K`).
    8.  Finish & Export Data.
*   **Mock Data Generator:** A backend service (or simple loop in the protocol) that emits realistic data points to the telemetry topic.

## 4. Full Implementation (Post-Demo)
*   **Error Recovery Scenario:** A planned failure (e.g., "Tip Pickup Failed") that forces the user to use the recovery UI.
*   **Complex Run:** A multi-step protocol involving multiple machines (simulated).

## 5. Constraints
*   **Reliability:** The demo path must be 100% reproducible.
*   **Timing:** The run should take 2-3 minutes—long enough to show features, short enough not to bore.
