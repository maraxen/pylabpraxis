# Plan: End-to-End Protocol Execution (Operation "First Light")

## Phase 1: Frontend Core - Asset Selection

* [x] Task: Update `asset-selector` to support `plrTypeFilter` and Hover Tags. [8665826]
  * [x] Subtask: Write unit tests for `asset-selector` input filtering and tag display.
  * [x] Subtask: Implement `plrTypeFilter` logic in `asset-selector.component.ts`.
  * [x] Subtask: Implement hover tags (e.g., "96", "V-bottom") in `asset-selector.component.html`.
* [x] Task: Integrate `ResourceDialogComponent` with `asset-selector`. [9b9251f]
  * [x] Subtask: Write unit tests verifying dialog launch and selection return (accession_id).
  * [x] Subtask: Update `asset-selector` to open `ResourceDialogComponent` on click and handle the result.
* [x] Task: Conductor - User Manual Verification 'Frontend Core - Asset Selection'
  * [x] Verified: Variable names display, Auto chip toggle, unique resource assignment

## Phase 2: Backend & Frontend - Autofill & Availability

* [ ] Task: Implement Backend Availability/Soonest Available Logic.
  * [ ] Subtask: Write unit tests for `AssetManager` querying available resources with PLR type and user-specified filters.
  * [ ] Subtask: Implement logic to find the "soonest available" resource (considering active protocol runs/locks).
  * [ ] Subtask: Expose this logic via a new `GET /api/v1/resources/available` endpoint.
* [ ] Task: Implement Frontend Autofill Trigger.
  * [ ] Subtask: Write unit tests for `RunProtocolComponent` parameter initialization with autofill logic.
  * [ ] Subtask: Implement automatic pre-population of `asset-selector` fields by calling the availability API on wizard initialization.
* [ ] Task: Conductor - User Manual Verification 'Backend & Frontend - Autofill & Availability' (Protocol in workflow.md)

## Phase 3: Execution Flow Integration

* [x] Task: Implement persistent "Simulation Mode" toggle and Wizard wiring. [nav-rail]
  * [x] Subtask: Add simulation toggle to navigation rail with localStorage persistence.
  * [x] Subtask: Wire `ExecutionService.startRun()` to pass `simulation_mode` to backend.
  * [ ] Subtask: (Optional) Add confirmation dialog before execution.
* [x] Task: Backend Asset Resolution & Execution Hook. [runs-endpoint]
  * [x] Subtask: Create POST /runs endpoint accepting `simulation_mode` parameter.
  * [x] Subtask: Initialize ProtocolExecutionService in main.py lifespan.
  * [x] Subtask: Add get_protocol_execution_service dependency.
  * [x] Subtask: Fix Asset Reservation Bug (release assets on complete/cancel). [Session 8]
  * [x] Subtask: Implement Cancellation Flow (Redis commands + Scheduler update). [Session 8]
* [ ] Task: Conductor - User Manual Verification 'Execution Flow Integration' (Protocol in workflow.md)

## Phase 4: E2E Verification & WebSocket Logs

* [/] Task: Real-time Log Streaming & UI Feedback.
  * [x] Subtask: Fix WebSocket URL path (`/execution/` segment missing). [Dec 24]
  * [x] Subtask: Fix `stopRun` endpoint to use `/cancel` instead of `/stop`. [Dec 24]
  * [ ] Subtask: Write unit tests for WebSocket log reception and display in `RunProtocolComponent`.
  * [ ] Subtask: Ensure frontend UI updates in real-time as logs are received from the backend.
* [ ] Task: Final E2E Simulation Run.
  * [ ] Subtask: Debug 500 error on `POST /api/v1/protocols/runs` (blocking).
  * [ ] Subtask: Fix Plotly.js configuration in `LiveDashboardComponent` (blocking).
  * [ ] Subtask: Manually execute `simple_transfer.py` in simulation mode via the Protocol Wizard.
  * [ ] Subtask: Verify that the run completes successfully and the status reaches `COMPLETED`.
* [ ] Task: Conductor - User Manual Verification 'E2E Verification & WebSocket Logs' (Protocol in workflow.md)

## Workflow Velocity Plan & Known Bugs

### Known Bugs

* [ ] **Command Palette Navigation**: Arrow keys (Up/Down) are buggy/inconsistent even after recent fixes. Requires investigation into `MatDialog` focus trapping or conflict with other listeners.
* [ ] **500 Error on Run Start**: `POST /api/v1/protocols/runs` returns 500 when starting protocol execution. Blocking E2E verification.
* [ ] **Plotly.js Config Error**: `LiveDashboardComponent` fails to render due to missing Plotly.js configuration. Blocking live dashboard.
