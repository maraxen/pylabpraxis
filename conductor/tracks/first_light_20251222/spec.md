# Specification: End-to-End Protocol Execution (Operation "First Light")

## 1. Overview
The goal of this track is to achieve the first successful end-to-end execution of a PyLabPraxis protocol (`simple_transfer.py`) from the frontend Protocol Wizard. This involves enhancing the resource selection UI, ensuring robust backend asset resolution, and integrating the execution flow with a "Simulation Mode" toggle. A key feature is the "Autofill" mode for asset selection, which intelligently suggests available resources based on protocol constraints and user filters.

## 2. Functional Requirements

### 2.1 Asset Selector Component (`asset-selector`)
*   **Filtering:** Must accept a `plrTypeFilter` (e.g., `Plate`, `TipRack`) to constrain the list of selectable assets.
*   **Asset Information:**
    *   Display selected asset's Name and PLR Type.
    *   Show "Tags" on hover for key differentiators (e.g., "96" for well count, "V-bottom" for bottom type).
    *   Show a status indicator (e.g., "Online", "Busy", "Maintenance").
*   **Actions:**
    *   Provide a "Clear Selection" button.
    *   Allow launching the existing `ResourceDialogComponent` to browse and select definitions/assets.
*   **Output:** Must return the selected asset's `accession_id` as the form value.

### 2.2 Protocol Wizard & Execution Flow
*   **Simulation Mode:**
    *   A persistent toggle visible at all steps of the Protocol Wizard.
    *   Default state: **ON**.
*   **Execution Confirmation:**
    *   A final confirmation step is required before execution triggers, regardless of simulation or hardware mode.
*   **Start Execution:**
    *   Collects all parameter values, including asset bindings.
    *   Passes the `simulation_mode` flag to the `ExecutionService`.
    *   Triggers `ExecutionService.startRun()`.

### 2.3 Asset Resolution & Autofill (Backend/Frontend Interaction)
*   **Autofill Mode (Default):**
    *   Automatically selects the "soonest available" asset that matches:
        1.  Protocol type hints/decorator annotations.
        2.  User-specified filters (e.g., if the user manually narrows down to "96-well plates").
*   **Busy Assets:**
    *   If a selected (or autofilled) asset is busy, display a "Busy until [Time]" message.
    *   Allow selection of busy assets, implying the run will be queued (basic queueing support).
*   **Backend Resolution:**
    *   Verify `execution.py` (`_prepare_arguments`) correctly resolves `accession_id` to actual asset instances.
    *   Ensure `AssetManager` can acquire these resources.

### 2.4 Verification
*   **Logs:** Real-time execution logs must stream via WebSocket to the frontend.
*   **Status:** The protocol run status must progress to `COMPLETED` upon success.

## 3. Non-Functional Requirements
*   **No AI/LLM Dependencies:** All filtering and logic must be deterministic.
*   **Performance:** Asset selection and autofill should be responsive.
*   **Reuse:** Leverage existing components like `ResourceDialogComponent` where possible.

## 4. Acceptance Criteria
*   [ ] User can open the Protocol Wizard for `simple_transfer.py`.
*   [ ] `asset-selector` correctly filters assets based on `Plate` and `TipRack` types.
*   [ ] "Autofill" successfully pre-selects available matching assets.
*   [ ] User can manually override selection using the dialog.
*   [ ] "Simulation Mode" toggle works and persists state.
*   [ ] "Start Execution" triggers a backend run in the correct mode.
*   [ ] Backend successfully resolves asset IDs to objects.
*   [ ] Frontend displays real-time logs from the execution.
*   [ ] Run completes with a success status.

## 5. Out of Scope
*   Advanced parameter bound inference via simulation (Technical Debt).
*   Complex scheduling optimization algorithms (First Light focuses on basic availability).
*   Hardware execution (focus is Simulation Mode).
