# Status: Complete
# Phase 5: GUI-Based "Direct Control" Executor

**Goal**: Implement a GUI-based "Direct Control" executor in the Playground.

**Concept**:
Instead of typing Python code, the user sees a UI panel for each machine in the Workcell.
They can select a method (e.g., `aspirate`, `move_plate`) from a dropdown.
The UI generates a form for the arguments (using Formly or similar).
On "Execute", it sends the command to the worker/backend.

## Tasks

### Task 1: Method Introspection (Completed)
- **Status**: Completed
    - Introspection service implemented.
    - API endpoint created.
    - Tests passed.
- **Objective**: Enable the backend to expose available methods and their signatures for a given machine type.
- **Implementation Details**:
    -   Target Service: `MachineService` (or new `IntrospectionService`) in `praxis/backend/services/`.
    -   Functionality: Return list of public methods for a machine definition (PLR class) including argument types/annotations.
    -   Strategy: Use Python's `inspect` module on the backend classes (or pre-compute/cache this metadata).

### Task 2: Direct Control Component
- **Objective**: Create the frontend UI for selecting and configuring machine commands.
- **Implementation Details**:
    -   Create `DirectControlComponent` in `praxis/web-client/src/app/features/playground/components/` (or `shared/`).
    -   **UI Elements**:
        -   **Machine Selector**: Dropdown to select a machine from the current Notebook/Workcell context.
        -   **Method Selector**: Dropdown populated by the introspection API.
        -   **Argument Form**: Dynamic input form based on the selected method's signature (e.g., using `ngx-formly` or dynamic reactive forms).
        -   **Execute Button**: Triggers the command.

### Task 3: Integration
- **Objective**: Integrate the component into the Playground and execute commands.
- **Implementation Details**:
    -   Add "Direct Control" tab/panel to the Playground feature (`praxis/web-client/src/app/features/playground/`).
    -   **Execution Flow**:
        -   On "Run" click, generate the corresponding Python code (e.g., `await lh.aspirate(...)`).
        -   Send this code to the REPL/Worker via the existing execution service.
