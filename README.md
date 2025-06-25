# PyLabPraxis

[**Docs**](https://docs.pylabrobot.org) | [**Forum**](https://forums.pylabrobot.org) | [**Installation**](https://docs.pylabrobot.org/installation.html) | [**Getting started**](https://docs.pylabrobot.org/basic.html)

## What is PyLabPraxis?

PyLabPraxis is a comprehensive Python-based platform designed to automate and manage laboratory workflows. It leverages the [PyLabRobot](https://pylabrobot.org/) library to interface with a wide range of lab automation hardware. PyLabPraxis provides a robust backend system built with FastAPI, enabling protocol execution, asset management, real-time hardware control, and persistent state management. Its primary goal is to facilitate the seamless execution of experiments in an automated lab environment with a frontend accessible to users of any skill level. It ensures consistent data logging practices, inventory management, reservation, and works with type-hinted python functions using PyLabRobot objects.

Developed for the Ovchinnikov group in MIT Biology.

## Core Architecture

PyLabPraxis employs a modular, service-oriented architecture designed for scalability and maintainability. The key architectural pillars are:

1. **FastAPI Backend**: Provides a RESTful API for all interactions, including protocol management, execution control, and asset monitoring.
2. **PyLabRobot Integration**: Core to its functionality, PyLabPraxis uses PyLabRobot for abstracting hardware interactions, allowing for control of various lab instruments like liquid handlers, plate readers, etc.
3. **PostgreSQL Database**: Serves as the primary persistent data store for:
    * Protocol definitions and versions.
    * Protocol run history, status, and results.
    * Asset definitions (e.g., machine types, resource types) and instances (specific physical assets).
    * Workcell configurations and deck layouts.
    * User management data (via Keycloak integration).
4. **Redis**: Utilized for:
    * **Runtime State Management**: Storing `PraxisState` for individual protocol runs.
    * **Distributed Locking**: `AssetLockManager` uses Redis to ensure exclusive access to assets during operations.
    * **Celery Broker & Backend**: Managing asynchronous task queues for protocol execution.
5. **Celery**: Enables asynchronous execution of long-running laboratory protocols, improving responsiveness and scalability of the system.
6. **Docker & Docker Compose**: The entire backend ecosystem is designed for deployment using Docker, facilitating isolated, reproducible, and scalable environments for the application and its services (PostgreSQL, Redis, Keycloak, SMTP).

## Key Components

The backend is composed of several core components, primarily within `praxis/backend/core/`, each with distinct responsibilities:

* **`ProtocolExecutionService` (`protocol_execution_service.py`)**: A high-level service that acts as the main entry point for all protocol execution workflows. It integrates various components to manage the lifecycle of a protocol run, supporting both immediate and scheduled (asynchronous via Celery) execution.
* **`Orchestrator` (`orchestrator.py`)**: The central component responsible for the step-by-step execution of a defined protocol. It fetches protocol definitions, prepares the execution environment (including `PraxisState`), acquires necessary assets via the `AssetManager`, executes the protocol's Python functions, and logs progress and results.
* **`ProtocolScheduler` (`scheduler.py`)**: Manages the scheduling of protocol runs. It analyzes resource requirements for a protocol, reserves the necessary assets, and queues the execution task with Celery.
* **`AssetManager` (`asset_manager.py`)**: Handles the lifecycle and allocation of physical laboratory assets (machines and resources). It interacts with the `WorkcellRuntime` to get live PyLabRobot objects and updates the database with asset status (e.g., `IN_USE`, `AVAILABLE`). It also manages asset definitions and synchronization with PyLabRobot's capabilities.
* **`AssetLockManager` (`asset_lock_manager.py`)**: Provides a mechanism for distributed locking of assets using Redis, preventing conflicts when multiple processes or protocol runs might attempt to use the same asset simultaneously.
* **`WorkcellRuntime` (`workcell_runtime.py`)**: Manages the *live, operational instances* of PyLabRobot objects (machines, resources). It dynamically instantiates these objects based on database definitions, handles their setup and teardown (connecting/disconnecting from hardware), and can save/restore their state for persistence and recovery.
* **`Workcell` (`workcell.py`)**: An in-memory container holding all configured PyLabRobot objects for the current lab setup. It provides a structured way to access and manage these live objects and their states.
* **`ProtocolCodeManager` (`protocol_code_manager.py`)**: Responsible for fetching, preparing, and loading protocol code for execution. It can handle protocols from various sources, such as Git repositories or local file systems, and manages module imports.
* **`PraxisRunContext` (`run_context.py`)**: An object passed through the execution flow of a protocol, carrying run-specific information like the unique run ID, a reference to the `PraxisState`, the current database session, and logging context.
* **`Protocol Decorators` (`decorators.py`)**: Python decorators used to define functions as PylabPraxis protocols. These decorators facilitate the automatic extraction of metadata (parameters, asset requirements, description) and integrate the function into the Praxis execution and discovery system.
* **Database Interaction Services (various modules in `praxis/backend/services/`)**: A crucial abstraction layer encapsulating all direct database interactions. Modules like `protocols.py`, `machine.py`, `resource_instance.py`, `workcell.py`, `function_output_data.py`, etc., provide CRUD operations and specialized queries for their respective ORM models, ensuring that business logic components do not interact directly with SQLAlchemy.
* **`API Layer` (modules in `praxis/backend/api/`)**: FastAPI routers and endpoints that expose the system's functionality over HTTP. This includes endpoints for protocol discovery, execution, status monitoring, asset management, and workcell configuration.

## Data Structures

PyLabPraxis utilizes two main types of data structures, primarily defined within `praxis/backend/models/`:

1. **ORM Models** (e.g., `asset_management_orm.py`, `protocol_definitions_orm.py`, `machine_orm.py`, `deck_orm.py`, `function_data_output_orm.py`):
    * These SQLAlchemy models represent the database schema and are used for persistent storage of all critical information.
    * Examples include `ProtocolDefinitionOrm`, `ProtocolRunOrm`, `ResourceInstanceOrm`, `MachineOrm`, `FunctionCallLogOrm`, `DeckLayoutOrm`, `FunctionDataOutputOrm`.
    * They define the relationships between different entities (e.g., a protocol run consists of multiple function calls; a machine can have multiple resources).

2. **Pydantic Models** (e.g., `asset_pydantic_models.py`, `protocol_pydantic_models.py`, `machine_pydantic_models.py`, `deck_pydantic_models.py`, `function_data_output_pydantic_models.py`):
    * Used for data validation, serialization, and deserialization, especially for API request and response bodies.
    * Ensure type safety and provide clear data contracts for the API.
    * Examples include `ProtocolStartRequest`, `AssetRequirementModel`, `ResourceInstanceResponse`, `ProtocolInfo`, `DeckLayoutResponse`, `FunctionDataOutputResponse`.

## State Management

State management is critical in an automated lab environment and is handled at multiple levels in PyLabPraxis:

1.  **`PraxisState` (`praxis.backend.services.state.PraxisState`)**:
    *   Provides a dictionary-like object, **backed by Redis and keyed by a unique `run_accession_id`**, for storing and retrieving **JSON-serializable runtime data specific to a single protocol run**.
    *   This allows simple data (like flags, IDs, or small parameters) to be shared across different function calls or asynchronous steps within that particular run.
    *   It is **not** intended to hold large, complex, or non-serializable Python objects directly.

2.  **`WorkcellRuntime` State & In-Memory Objects**:
    *   `WorkcellRuntime` manages the live operational state of PyLabRobot objects (e.g., a liquid handler's current tip status, a plate's location on deck).
    *   More broadly, services like the `Orchestrator` and `AssetManager` use rich **in-memory Python objects** (often Pydantic models) to represent the complex, live state of the application. This includes the `WorkcellDefinition`, detailed `ProtocolState` (tracking execution progress), and `AssetManagerState`.
    *   These in-memory objects are typically initialized from the database.
    *   `WorkcellRuntime` provides mechanisms to **backup** the entire workcell's PyLabRobot object states to a persistent file (e.g., JSON) and **restore** from it, crucial for recovery.
    *   Critical aspects of this live state are synchronized with the **database** (e.g., asset availability, current location if tracked).

3.  **Database (PostgreSQL)**:
    *   The ultimate source of truth for **persistent configuration, definitions, and historical data**.
    *   Stores the defined state of assets (e.g., `ResourceInstanceOrm.status`, `MachineOrm.status`), protocol definitions, workcell layouts, and records the history of protocol runs (status, inputs, outputs).
    *   Provides the foundational data for initializing the live, in-memory state objects.

4.  **Redis (beyond `PraxisState`)**:
    *   **`AssetLockManager`**: Uses Redis for distributed locks to manage exclusive access to assets.
    *   **Celery**: Uses Redis as a message broker (to send tasks to workers) and as a result backend (to store task completion status and results).

**How it Fits Together:**

*   When a protocol starts, a `PraxisState` instance is created in Redis for that specific run.
*   The `Orchestrator` and other services load configurations and definitions from the database into **in-memory Pydantic models and other Python objects** to manage the live state of the workcell, protocol, and assets.
*   The `Orchestrator` passes a `PraxisRunContext` (which includes access to the run's `PraxisState`) to protocol functions.
*   Protocol functions can read from and write to `PraxisState` to share simple, serializable data between steps.
*   `AssetManager` requests live asset objects from `WorkcellRuntime`. `WorkcellRuntime` instantiates these based on database definitions and manages their live operational state.
*   Changes in live asset status (e.g., a machine becoming busy) are reflected by `AssetManager` and `WorkcellRuntime`, and these changes are updated in the in-memory state objects and persisted to the database.
*   `AssetLockManager` ensures that an asset acquired by one protocol run is not simultaneously used by another.
*   Upon completion or failure, the final status of the protocol run and any significant outputs (often derived from the in-memory state objects) are persisted to the PostgreSQL database.
*   `WorkcellRuntime` can periodically back up the live PyLabRobot object states.

## Execution Workflow (Simplified)

1. **Request**: A user or system initiates a protocol run via the API, providing the protocol name/ID and any user parameters.
2. **Scheduling (Optional)**: For asynchronous execution, the `ProtocolExecutionService` passes the request to the `ProtocolScheduler`.
    * The `Scheduler` analyzes the protocol's asset requirements.
    * It attempts to reserve the required assets using the `AssetLockManager`.
    * If successful, it queues a task in Celery via `execute_protocol_run_task`.
3. **Task Execution (Celery Worker)**:
    * A Celery worker picks up the task.
    * It initializes the `Orchestrator` (or uses a shared instance with proper context).
4. **Orchestration**:
    * The `Orchestrator` fetches the protocol definition (code and metadata) using `ProtocolCodeManager` and database services.
    * It prepares the execution context (`PraxisRunContext`), including initializing `PraxisState`.
    * It acquires the necessary live assets (PyLabRobot objects) from the `AssetManager`, which in turn interacts with `WorkcellRuntime`.
    * The `Orchestrator` then executes the protocol's Python functions sequentially, passing the context and acquired assets.
    * Each function call, its parameters, and its outcome are logged to the database.
5. **State Updates**: During execution, protocol functions can modify `PraxisState`. The state of physical assets is managed by `WorkcellRuntime` and reflected in the database by `AssetManager`.
6. **Completion/Failure**:
    * Upon completion, the `Orchestrator` finalizes logging, updates the protocol run status to `COMPLETED` in the database, and ensures assets are released via `AssetManager`.
    * In case of failure, the status is updated to `FAILED`, error information is logged, and attempts are made to release assets safely.
7. **Results**: Outputs and results from the protocol, including any data explicitly saved as `FunctionDataOutputOrm`, are stored in the database, associated with the protocol run and specific function calls.

## Services Overview (`praxis.backend.services/`)

The `praxis.backend.services/` package contains a suite of modules that abstract database interactions and provide business logic for different entities. This promotes separation of concerns and makes the core logic cleaner. Key service modules include:

* **`protocols.py`**: Manages CRUD operations and logic for protocol definitions, protocol runs, and function call logs.
* **`resource_instance.py` & `resource_type_definition.py`**: Handle data and logic for resource instances and their definitions (e.g., plates, tips).
* **`machine.py`**: Manages machine-specific data, status, and associations.
* **`workcell.py`**: Manages workcell configurations and related data.
* **`deck_instance.py`, `deck_position.py`, `deck_type_definition.py`**: Handle persistence and logic for deck layouts, slot configurations, and deck types.
* **`discovery_service.py`**: Discovers protocol functions from code, extracts metadata, and stores them as protocol definitions.
* **`function_output_data.py`**: Manages the storage and retrieval of structured data outputs generated by protocol functions.
* **`plate_parsing.py` & `plate_viz.py`**: Provide utilities for parsing plate data and generating visualizations.
* **`praxis_orm_service.py`**: Provides a general interface for common database operations.
* **`state.py`**: Contains the `PraxisState` implementation for run-specific Redis-backed state.
* **`scheduler.py`**: (Note: Core scheduling logic is in `praxis.backend.core.scheduler.py`, this might be a helper or a different aspect of scheduling if present here).

## API Overview (`praxis.backend.api/`)

PyLabPraxis exposes a RESTful API built with FastAPI. Key endpoint groups include:

* **`/protocols`**:
  * Discover available protocols.
  * Get details of specific protocols.
  * Create, start, and manage protocol runs.
  * Get status and results of protocol runs.
* **`/resources` / `/assets`**:
  * List and manage resource definitions (types of plates, tips, etc.).
  * List and manage resource instances (specific physical items).
* **`/machines`**:
  * List and manage machine definitions and instances.
  * Control machine states.
* **`/workcell`**:
  * Manage workcell configurations.
  * Get live deck layouts and workcell state.
* **`/function_data_outputs`**:
  * Manage and retrieve structured data outputs generated by protocol functions.

The API uses Pydantic models for request and response validation and serialization, ensuring clear and robust communication.

## Lab Configuration & Getting Started

(This section can be expanded with specific setup instructions for databases, Redis, Keycloak, and PyLabRobot hardware.)

### Keycloak Setup

1. Start the Keycloak server:

    ```bash
    # (Instructions for starting Keycloak, typically via Docker Compose)
    docker-compose up keycloak
    ```

2. Configure realms, clients, and users as per Keycloak documentation and PyLabPraxis requirements.

## Development

PyLabPraxis uses standard Python development tools:

* **`pytest`**: For running unit and integration tests.

    ```bash
    make test
    ```

* **`pylint`**: For code style enforcement.

    ```bash
    make lint
    ```

* **`mypy`**: For static type checking.

    ```bash
    make typecheck
    ```

Refer to `CONTRIBUTING.md` for more details on the development process.

---

**Disclaimer:** PyLabPraxis is not officially endorsed or supported by any robot manufacturer. If you use a firmware driver such as the STAR driver provided here, you do so at your own risk. Usage of a firmware driver such as STAR may invalidate your warranty. Please contact us with any questions.

graph LR
    %% Define reusable styles for component types
    classDef service fill:#f9f,stroke:#333,stroke-width:2px
    classDef entrypoint fill:#bbf,stroke:#333,stroke-width:2px
    classDef dataService fill:#ddf,stroke:#333,stroke-width:2px
    classDef dataModel fill:#eef,stroke:#333,stroke-width:2px
    classDef runtimeState fill:#ffd,stroke:#333,stroke-width:2px
    classDef externalDB fill:#afa,stroke:#333,stroke-width:2px
    classDef externalService fill:#ffc,stroke:#333,stroke-width:2px
    classDef externalLib fill:#cfa,stroke:#333,stroke-width:2px
    classDef codeArtifact fill:#e0e0e0,stroke:#333,stroke-width:2px

    %% Frontend Subgraph
    subgraph Frontend
        Flutter_Frontend["Flutter Frontend<br/>User Interface"]
    end

    %% Backend Services Subgraph
    subgraph Backend
        direction TB

        subgraph "Entry & Orchestration"
            API_Layer("FastAPI API Layer")
            ProtocolExecutionService("ProtocolExecutionService")
            Orchestrator("Orchestrator")
            ProtocolScheduler("ProtocolScheduler")
            CeleryTasks("Celery Tasks")
        end

        subgraph "Core Logic & Runtimes"
            WorkcellRuntime("WorkcellRuntime")
            Workcell{{"Workcell PLR Objects"}}
            AssetManager("AssetManager")
            AssetLockManager("AssetLockManager")
            PraxisRunContext("PraxisRunContext")
        end

        subgraph "Data & Discovery"
            DataServices("Data Services")
            Models("ORM & Pydantic Models")
            ProtocolDiscoveryService("ProtocolDiscoveryService")
            ProtocolCodeManager("ProtocolCodeManager")
            ProtocolDecorators("@protocol_function")
        end
    end

    %% External Services and Data Stores Subgraph
    subgraph "External Dependencies"
        direction TB
        PostgreSQL("PostgreSQL")
        Redis[("Redis Cache/Broker/Locks")]
        Keycloak("Keycloak Auth")
        PyLabRobotLib("PyLabRobot Library")
        Protocol_Files(["Protocol Files"])
        SMTP_Server("SMTP Server")
    end

    %% Apply Classes to Nodes
    class Flutter_Frontend,API_Layer entrypoint
    class ProtocolExecutionService,Orchestrator,ProtocolScheduler,CeleryTasks,WorkcellRuntime,AssetManager,AssetLockManager,ProtocolDiscoveryService,ProtocolCodeManager service
    class DataServices dataService
    class Models dataModel
    class Workcell,PraxisRunContext runtimeState
    class PostgreSQL externalDB
    class Redis,Keycloak,SMTP_Server externalService
    class PyLabRobotLib externalLib
    class Protocol_Files,ProtocolDecorators codeArtifact


    %% Define Connections
    Flutter_Frontend -- "HTTP/REST & WebSockets" --> API_Layer
    API_Layer -- "Handles Requests" --> ProtocolExecutionService
    API_Layer -- "CRUD Operations" --> DataServices
    API_Layer -- "Uses for Req/Res" --> Models
    ProtocolExecutionService -- "Coordinates" --> Orchestrator
    ProtocolExecutionService -- "Coordinates" --> ProtocolScheduler
    ProtocolScheduler -- "Queues Task" --> CeleryTasks
    CeleryTasks -- "Executes via" --> Orchestrator
    Orchestrator -- "Executes Code From" --> Protocol_Files
    Orchestrator -- "Controls Hardware via" --> WorkcellRuntime
    WorkcellRuntime -- "Controls Hardware via" --> PyLabRobotLib
    WorkcellRuntime -- "Manages Live Objects" --> Workcell
    Orchestrator -- "Uses" --> AssetManager
    ProtocolScheduler -- "Checks Locks" --> AssetLockManager
    AssetManager -- "Uses" --> AssetLockManager
    AssetManager -- "Interacts with" --> WorkcellRuntime
    AssetLockManager -- "Uses" --> Redis
    Orchestrator -- "Creates & Passes" --> PraxisRunContext
    Orchestrator -- "Logs via" --> DataServices
    DataServices -- "Accesses" --> PostgreSQL
    DataServices -- "Uses" --> Models
    PraxisRunContext -- "Carries State from" --> Redis
    ProtocolDiscoveryService -- "Scans" --> Protocol_Files
    ProtocolDiscoveryService -- "Uses" --> ProtocolCodeManager
    ProtocolDiscoveryService -- "Finds" --> ProtocolDecorators
    ProtocolDiscoveryService -- "Writes Metadata to" --> DataServices
    API_Layer -- "Authenticates via" --> Keycloak
    Orchestrator -- "Sends Notifications via" ---> SMTP_Server

---

## Asset Model Refactor (2025-06)

### Overview

The asset-related backend models have been **unified and modernized**. All asset types (machines, resources, decks, workcells) now inherit from a single `Asset` base model, with standardized field names and relationships. This change simplifies asset management, improves consistency, and removes legacy/obsolete fields and class names.

### Key Changes

- **Unified Asset Model:**
  - All asset types now use a common set of fields: `accession_id`, `name`, `fqn`, `asset_type`, `location`, `plr_state`, `plr_definition`, `properties_json`.
  - Relationships between assets (e.g., resource <-> machine) are standardized and explicit.
- **Obsolete Fields Removed:**
  - Legacy fields (e.g., `user_assigned_name`, old FQN fields, `ResourceInstanceOrm`, `DeckInstanceOrm`) are gone.
  - All ORM and Pydantic models are consistent and up to date.
- **Exports Updated:**
  - Only current, valid models and enums are exported in `models/__init__.py`.
- **Documentation:**
  - This section summarizes the rationale and provides guidance for updating services and APIs.

### Guidance for Updating Services & APIs

- **Use Unified Fields:**
  - Update all service and API logic to use the new asset model fields (`accession_id`, `name`, etc.).
  - Remove references to legacy/obsolete fields and classes.
- **Relationships:**
  - Use the new standardized relationships for asset associations (e.g., `resource_counterpart`, `machine_counterpart`).
- **Testing:**
  - Update or add tests to ensure compatibility with the new asset model structure.
- **Imports:**
  - Import asset models and enums from `praxis.backend.models` as re-exported in `__init__.py`.

See the code and docstrings in `praxis/backend/models/` for details.

---

