# Research: Machine Selection and Backend Arguments

**Date**: 2026-01-19
**Scope**: Backend (`praxis/backend`) and Shared Models
**Focus**: Machine Selection, Backend Arguments, and Argument Resolution

## 1. Machine -> Backend Mapping

The system uses a separated model architecture to map Machines to their Backends, transitioning from a legacy single-definition model to a composed Frontend/Backend definition model.

### Key Models

*   **`MachineBackendDefinition`** (`praxis/backend/models/domain/machine_backend.py`):
    *   Represents the hardware driver (e.g., `HamiltonStarBackend`).
    *   **Argument Schema**: Stores the JSON schema for connection parameters in `connection_config`.
    *   **Type**: Includes a `backend_type` enum (REAL_HARDWARE, SIMULATOR).
    *   **FQN**: Stores the Python class path (e.g., `pylabrobot.liquid_handling.backends.hamilton.STAR`).

*   **`MachineFrontendDefinition`** (`praxis/backend/models/domain/machine_frontend.py`):
    *   Represents the abstract machine interface (e.g., `STAR`).
    *   **Argument Schema**: Stores user-configurable capabilities schema in `capabilities_config`.
    *   **FQN**: Stores the Python class path (e.g., `pylabrobot.liquid_handling.liquid_handler.LiquidHandler` or specific subclass).

*   **`Machine`** (`praxis/backend/models/domain/machine.py`):
    *   Represents a physical instance of a machine.
    *   **Links**: Has foreign keys to both `MachineFrontendDefinition` and `MachineBackendDefinition`.
    *   **Backend Arguments**: Stored in `backend_config` (JSON blob).
    *   **Frontend Arguments**: Stored in `properties_json` (JSON blob, inherited from `Asset` model).

### Storage of Arguments
*   **Backend Arguments**: Stored as a JSON blob in the `backend_config` field of the `Machine` table.
*   **Frontend Arguments**: Stored as a JSON blob in the `properties_json` field of the `Machine` (via `Asset`) table.

## 2. Argument Resolution

Argument resolution and machine initialization occur in **`WorkcellRuntime`** (specifically `MachineManagerMixin`), not in `ExecutionService` or `WebBridge`.

**Location**: `praxis/backend/core/workcell_runtime/machine_manager.py` -> `initialize_machine` method.

### Resolution Logic (New Separation Path)

When a `Machine` instance has both `frontend_definition_accession_id` and `backend_definition_accession_id`:

1.  **Backend Initialization**:
    *   **Class**: Resolved from `MachineBackendDefinition.fqn`.
    *   **Arguments**: `backend_config` from the `Machine` instance is unpacked (`**backend_config`) into the backend class constructor.
    *   **Result**: A backend instance is created.

2.  **Frontend Initialization**:
    *   **Class**: Resolved from `MachineFrontendDefinition.fqn`.
    *   **Arguments**: `properties_json` from the `Machine` instance is copied to `init_params`.
    *   **Backend Injection**: The created backend instance is injected into `init_params` with the key `"backend"`.
    *   **Name Injection**: The machine name is injected into `init_params` with the key `"name"`.
    *   **Filtering**: `init_params` are filtered to match the frontend class `__init__` signature. Extra parameters are put into an `options` dict if the constructor accepts it, or discarded with a warning.
    *   **Result**: The frontend instance is created with the backend instance passed to it.

3.  **Setup**:
    *   The system calls `await machine_instance.setup()` if available.

## 3. Frontend/Backend Args

The system distinguishes between frontend and backend arguments through the data model structure:

*   **Backend-Only Args**:
    *   **Definition**: Defined in `MachineBackendDefinition.connection_config` (Schema).
    *   **Instance Value**: Stored in `Machine.backend_config`.
    *   **Usage**: Passed exclusively to the Backend constructor.
    *   **Examples**: Port, baud rate, IP address, simulation settings.

*   **Frontend-Only Args**:
    *   **Definition**: Defined in `MachineFrontendDefinition.capabilities_config` (Schema).
    *   **Instance Value**: Stored in `Machine.properties_json`.
    *   **Usage**: Passed to the Frontend (LiquidHandler) constructor.
    *   **Examples**: Deck size, custom capabilities, configuration options that don't belong to the driver.

### Legacy/Compatibility
There is a legacy path where `Machine.fqn` is used directly. In this case, `properties_json` is used for initialization, and it is assumed the class handles its own backend creation or is a monolithic class. This path is taken if the specific frontend/backend definition FKs are missing.
