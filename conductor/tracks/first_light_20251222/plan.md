# Plan: End-to-End Protocol Execution (Operation "First Light")

## Phase 1: Frontend Core - Asset Selection
*   [ ] Task: Update `asset-selector` to support `plrTypeFilter` and Hover Tags.
    *   [ ] Subtask: Write unit tests for `asset-selector` input filtering and tag display.
    *   [ ] Subtask: Implement `plrTypeFilter` logic in `asset-selector.component.ts`.
    *   [ ] Subtask: Implement hover tags (e.g., "96", "V-bottom") in `asset-selector.component.html`.
*   [ ] Task: Integrate `ResourceDialogComponent` with `asset-selector`.
    *   [ ] Subtask: Write unit tests verifying dialog launch and selection return (accession_id).
    *   [ ] Subtask: Update `asset-selector` to open `ResourceDialogComponent` on click and handle the result.
*   [ ] Task: Conductor - User Manual Verification 'Frontend Core - Asset Selection' (Protocol in workflow.md)

## Phase 2: Backend & Frontend - Autofill & Availability
*   [ ] Task: Implement Backend Availability/Soonest Available Logic.
    *   [ ] Subtask: Write unit tests for `AssetManager` querying available resources with PLR type and user-specified filters.
    *   [ ] Subtask: Implement logic to find the "soonest available" resource (considering active protocol runs/locks).
    *   [ ] Subtask: Expose this logic via a new `GET /api/v1/resources/available` endpoint.
*   [ ] Task: Implement Frontend Autofill Trigger.
    *   [ ] Subtask: Write unit tests for `RunProtocolComponent` parameter initialization with autofill logic.
    *   [ ] Subtask: Implement automatic pre-population of `asset-selector` fields by calling the availability API on wizard initialization.
*   [ ] Task: Conductor - User Manual Verification 'Backend & Frontend - Autofill & Availability' (Protocol in workflow.md)

## Phase 3: Execution Flow Integration
*   [ ] Task: Implement persistent "Simulation Mode" toggle and Wizard wiring.
    *   [ ] Subtask: Write unit tests for `RunProtocolComponent` state management of the simulation toggle.
    *   [ ] Subtask: Add simulation toggle to the global/persistent section of the Protocol Wizard UI.
    *   [ ] Subtask: Implement "Start Execution" confirmation dialog and final logic to trigger `ExecutionService.startRun()`.
*   [ ] Task: Backend Asset Resolution & Execution Hook.
    *   [ ] Subtask: Write integration tests for `execution.py` (`_prepare_arguments`) verifying resolution of `accession_id` to asset objects.
    *   [ ] Subtask: Verify `AssetManager.acquire()` correctly locks resources by ID during execution.
*   [ ] Task: Conductor - User Manual Verification 'Execution Flow Integration' (Protocol in workflow.md)

## Phase 4: E2E Verification & WebSocket Logs
*   [ ] Task: Real-time Log Streaming & UI Feedback.
    *   [ ] Subtask: Write unit tests for WebSocket log reception and display in `RunProtocolComponent`.
    *   [ ] Subtask: Ensure frontend UI updates in real-time as logs are received from the backend.
*   [ ] Task: Final E2E Simulation Run.
    *   [ ] Subtask: Manually execute `simple_transfer.py` in simulation mode via the Protocol Wizard.
    *   [ ] Subtask: Verify that the run completes successfully and the status reaches `COMPLETED`.
*   [ ] Task: Conductor - User Manual Verification 'E2E Verification & WebSocket Logs' (Protocol in workflow.md)
