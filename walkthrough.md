# Walkthrough - State Inspection & Reporting Enhancement

## Overview
This enhancement enables real-time state inspection and post-run "time travel" for backend-executed protocol runs. Previously, these features were only available in "Browser Mode".

## Changes

### 1. Backend Persistence
- **Model Update:** Added `state_before_json` and `state_after_json` to the `FunctionCallLog` table.
- **Orchestrator Integration:** The protocol decorator now captures full `WorkcellRuntime` state snapshots before and after every decorated protocol function call.
- **Database:** Updated `praxis.db` (SQLite) and regenerated the browser schema to include these new columns.

### 2. State History API
- **New Endpoint:** `GET /api/v1/protocols/runs/{run_id}/state-history`.
- **Functionality:** Retrieves all function call logs for a specific run, including the captured state snapshots, formatted for the frontend timeline.
- **Models:** Introduced `praxis/backend/models/domain/simulation.py` with Pydantic models mirroring the frontend's expected structures.

### 3. Frontend Integration
- **Service Update:** `SimulationResultsService.getStateHistory()` now fetches data from the backend API when not in browser mode.
- **Live View UI:** Improved the "Live View" tab in the Run Detail page to show the deck layout even before the first state update is received.
- **Model Alignment:** Added `raw_plr_state` to the `StateSnapshot` interface to allow the UI to handle backend state snapshots gracefully.

## How to Verify

1.  **Start the Backend:** Ensure the backend is running with the updated SQLite database.
2.  **Execute a Protocol:** Run any protocol through the web interface (ensure it's using the backend, not browser-only mode).
3.  **Monitor Live State:**
    - Go to the **Execution Monitor**.
    - Click on your active run.
    - Switch to the **Live View** tab. You should see the deck layout.
4.  **Verify History:**
    - Once the run completes (or while it's running), switch to the **State Inspector** tab.
    - You should see the **Operation Timeline** populated with steps.
    - Clicking on a step should update the deck state (if snapshots were captured correctly).

## Technical Notes
- **Storage:** Full snapshots are stored for every operation. For production, we should consider delta-compression if protocol runs become very long.
- **SQLite:** All migrations were applied to `praxis.db`.
