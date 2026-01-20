# Phase 6: Interactive Protocols Implementation Plan

**Goal**: Implement Interactive Protocols allowing user interactions (pause, confirm, input) during protocol execution.

## Architecture

### 1. Backend (Bridge)

- **Component**: `web_bridge.py` & `praxis.interactive`
- **Responsibilities**:
  - Extend `WebBridge` to handle bi-directional communication for interaction requests.
  - Implement `request_user_interaction(type, prompt, options)` which returns an `asyncio.Future`.
  - Manage pending interactions map `interaction_id -> Future`.
  - Expose high-level API in `praxis.interactive` (`pause()`, `confirm()`, `input()`).

### 2. Worker (Pyodide/WebWorker)

- **Component**: `worker.ts` (or equivalent WebWorker handler)
- **Responsibilities**:
  - Intercept `USER_INTERACTION` messages from Python.
  - Forward these messages to the main Angular application thread.
  - Listen for interaction responses from Angular and send them back to Python.

### 3. Frontend (Angular)

- **Component**: `InteractionService` & `InteractionDialog`
- **Responsibilities**:
  - `InteractionService`: Listen for worker messages regarding interactions.
  - `InteractionDialog`: A dynamic dialog component capable of rendering:
    - **Confirmation**: Yes/No buttons.
    - **Input**: Text input field.
    - **Selection**: Dropdown or radio buttons (optional but good for future).
  - User action in Dialog resolves the interaction -> Service sends result to Worker.

### 4. Protocol API

- **Component**: `praxis.interactive` module
- **Public API**:
  - `pause(message: str)`: Pauses execution until user acknowledges.
  - `confirm(message: str) -> bool`: Asks user for Yes/No.
  - `input(prompt: str) -> str`: Asks user for text input.

---

## Plan Tasks

### Task 1: Bridge & API (Python)

**Goal**: Implement the Python-side mechanisms for requesting and awaiting user interaction.

- [x] **Extend `WebBridge`**:
  - Add `_pending_interactions: Dict[str, asyncio.Future]`.
  - Add `request_interaction(type: str, payload: dict) -> Any`.
  - Add `handle_interaction_response(id: str, value: Any)`.
- [x] **Create `praxis.interactive`**:
  - Implement `pause(msg)`.
  - Implement `confirm(msg)`.
  - Implement `input(msg)`.
  - Ensure these calls yield/await correctly within the Pyodide environment.

### Task 2: Worker & Service (Transport)

**Goal**: Ensure messages flow from Python -> Worker -> Main Thread and back.

- [x] **Update Worker**:
  - Handle message type `INTERACTION_REQUEST`.
  - Post message to main thread.
  - Handle message type `INTERACTION_RESPONSE` from main thread -> call Python callback/resume.
- [x] **Create `InteractionService`**:
  - Observable/Subject for active interactions.
  - Methods to `resolveInteraction(id, value)`.

### Task 3: UI Components (Dialogs)

**Goal**: Present the interaction requests to the user.

- [x] **Create `InteractionDialogComponent`**:
  - Template with dynamic switch based on interaction type.
  - Integration with Material Dialog or custom overlay.
- [x] **Integrate with App**:
  - Subscribe to `InteractionService` requests.
  - Automatically open dialog on request.
  - Prevent protocol execution from continuing (UI blocking not needed, but logical blocking is implicit).

### Task 4: Verification

**Goal**: Verify the end-to-end flow.

- [x] **Create `interactive_test.py`** (Test spec `interactive-protocol.spec.ts` created)
- [ ] **Run Manual Test / E2E Test**:
  - Execute protocol.
  - Verify Dialog appears.
  - Verify Python receives result and continues.
  - *Status*: Failed. Test timed out waiting for dialog.
  - *Issues*: Possible timing, import, or execution flow issue. See session logs.
