# State Management in Praxis

State management is a critical aspect of Praxis, ensuring that the system accurately reflects the status of the laboratory automation workcell, protocols, and assets at all times. It involves several interconnected components and layers, from in-memory representations to persistent storage and real-time updates.

## Core State Management Components

Praxis employs a multi-faceted approach to state management, utilizing:

1.  **`PraxisState` (Redis-backed run-specific data)**: A dictionary-like object, persisted to Redis, for storing and retrieving JSON-serializable data specific to a single protocol run. It facilitates sharing simple state across different function calls or steps within that run. It also allows for other programs to access this data and that it persists between runs with ease.
2.  **`WorkcellRuntime` (Live Operational State)**: Manages the real-time operational state of PyLabRobot device objects, their connections, and interactions. This includes handling the live status of hardware.
3.  **Database (PostgreSQL with SQLAlchemy ORM)**: For persistent storage of foundational data (workcell configurations, protocol definitions, asset catalogs), protocol history, execution logs, and the canonical state of assets when not actively in use.
4.  **In-Memory Pydantic Models & Objects**: Used by various services (e.g., Orchestrator, AssetManager) to hold and manage the complex, live state of the application during operation, such as the current `WorkcellDefinition`, detailed `ProtocolState`, and `AssetManagerState`. These objects are constructed from database records and updated during runtime.
5.  **Redis (beyond `PraxisState`)**: Used for Celery task queuing, Celery result backend, and distributed locking mechanisms (e.g., `AssetLockManager`).

---

## 1. `PraxisState` (`praxis.backend.services.state.PraxisState`)

`PraxisState` provides a mechanism for storing and retrieving **JSON-serializable data that is specific to a single protocol execution run**. It acts as a persistent, run-scoped dictionary, backed by Redis.

### Key Characteristics & Responsibilities:

-   **Run-Specific**: Each instance is tied to a unique `run_accession_id`. Data is isolated per protocol run.
-   **Redis Persistence**: All data set in a `PraxisState` object is automatically serialized to JSON and stored in Redis under a key derived from the `run_accession_id`. It loads from Redis upon initialization.
-   **JSON-Serializable Data Only**: Designed to store simple data types that can be easily converted to and from JSON (strings, numbers, booleans, lists, dictionaries). Importantly, this includes PyLabRobot Resource and Machine objects. It is **not** intended to directly store complex Python objects that are not inherently JSON-serializable (e.g., live device driver instances, database connection objects).
-   **Shared Data Across Steps**: Facilitates the sharing of simple parameters, intermediate results, or flags between different functions or steps within the same protocol run, especially in distributed or asynchronous execution scenarios managed by Celery.
-   **Attribute and Dictionary Access**: Provides both dictionary-style (`state['key']`) and attribute-style (`state.key`) access to its data.

### How it Differs from Broader Application State:

-   `PraxisState` is **not** the central container for the entire application's live state (like the complete `WorkcellDefinition` object or the live `AssetManagerState` object graph).
-   These more complex stateful objects are typically managed by other components (e.g., `Orchestrator`, `AssetManager`, `WorkcellRuntime`) and may use data from the database as their primary source, updated during operations. `PraxisState` might store identifiers or simple status flags related to these, but not the objects themselves.

### Example Use Case:

A protocol step might generate a unique ID for a sample, which needs to be used by a subsequent, potentially asynchronous, step. This ID can be stored in `PraxisState`:
`praxis_state.current_sample_id = "sample123"`

Later, another function in the same run can retrieve it:
`sample_id = praxis_state.current_sample_id`

---

## 2. `WorkcellRuntime` (Live Operational State)

The `WorkcellRuntime` is responsible for the dynamic, real-time aspects of the workcell's operation. It acts as an abstraction layer over the physical or simulated devices.

### Key Responsibilities of `WorkcellRuntime`

- **Device Management**: Establishes and maintains connections to all devices defined in the `WorkcellDefinition`.
- **Operation Execution**: Translates high-level protocol steps into low-level commands for individual devices.
- **Real-time State Tracking**: Monitors the status of devices (e.g., busy, idle, error) and the physical state of the workcell. This includes managing the state of device-specific features like a gripper's occupancy.
- **Resource Locking**: Manages access to shared resources and devices to prevent conflicts.
- **Deck and Layout Management**: While the `WorkcellDefinition` (often loaded from the database and represented as a Pydantic model in memory) defines the static layout of the workcell deck, `WorkcellRuntime` is involved in interacting with this layout. It understands where resources (plates, tip boxes) are supposed to be according to the definition and can be instructed to interact with specific locations. The actual state of what is *currently* at each deck location, if dynamic beyond the initial setup, is typically managed by the `AssetManager` or within the `ProtocolState`, which `WorkcellRuntime` would consult or be informed by.

### Relationship with Other State Components

-   `WorkcellRuntime` operates based on the configuration provided by the `WorkcellDefinition` (which is part of the broader application state, often initialized from the database).
-   It reports status changes and operational outcomes that can lead to updates in the persistent database state (e.g., asset availability) and potentially influence data stored in `PraxisState` (e.g., recording a successful operation).
-   While `PraxisState` provides a more holistic view, `WorkcellRuntime` is focused on the immediate operational context.

---

## 3. Database (PostgreSQL with SQLAlchemy ORM)

The database serves as the persistent backbone for Praxis, storing data that needs to survive beyond a single session or execution. SQLAlchemy ORM is used to map Python objects to database tables.

### Key Data Stored in Database

- **Workcell Configurations**: Definitions of different laboratory setups, including deck layouts and device placements.
- **Protocol Definitions**: The structure and steps of laboratory protocols.
- **Execution History**: Records of past protocol runs, including start/end times, status, parameters, and links to generated data.
- **Asset Tracking**: Information about labware (plates, tubes), reagents, and samples, including their properties, history, and current (or last known) locations if not solely managed in memory during a run.
- **User and Permissions Data**: If applicable for multi-user environments.
- **System Logs and Audit Trails**: Important events and errors.

### Role in State Management

- Provides the foundational data used to construct live, in-memory state objects (like Pydantic models representing the workcell or assets) at the start of operations or a protocol run.
- Stores the results and artifacts of protocol execution, effectively a historical record of state changes.
- Ensures data integrity and durability.

---

## 4. In-Memory Pydantic Models & Objects

While `PraxisState` handles run-specific serializable data and the database holds persistent configurations, the active, complex state of the application during operation is often managed by dedicated Python objects, frequently defined using Pydantic models.

### Key Roles:

-   **Data Validation and Structure**: Pydantic models ensure these complex state objects adhere to defined schemas, have validated data, and provide clear structures.
-   **Operational Hub**: Services like the `Orchestrator` and `AssetManager` hold and manipulate these in-memory objects to reflect the current understanding of the system. For example, the `Orchestrator` might hold the `ProtocolState` for the currently executing protocol, and the `AssetManager` would manage the state of assets on the deck.
-   **Synchronization with Persistent Stores**: These in-memory objects are often initialized from the database (e.g., loading a `WorkcellDefinition`). Changes to them during runtime (e.g., an asset's location on the deck changing) are then persisted back to the database and may trigger updates to `PraxisState` if relevant for cross-step communication.

---

## State Flow During Protocol Execution

Understanding how state evolves during the lifecycle of a protocol is key:

1.  **Protocol Discovery/Loading**:
    *   A protocol definition is loaded from the database or a file.
    *   The `Orchestrator` (or a similar service) loads the relevant `WorkcellDefinition` (from the database, likely into a Pydantic model). This definition includes the deck layout.
    *   A unique `run_accession_id` is generated.
    *   A `PraxisState` instance is created for this `run_accession_id`, connecting to Redis.
    *   The protocol is parsed and validated.

2.  **Initialization**:
    *   The `Orchestrator` might populate `PraxisState` with initial run-specific parameters if they are simple and need to be shared.
    *   Complex objects like `ProtocolState` and `AssetManagerState` are initialized in memory by relevant services, based on database information (including the `WorkcellDefinition`'s deck layout) and protocol requirements.
    *   `WorkcellRuntime` connects to the required devices based on the `WorkcellDefinition`.
    *   Initial device states are confirmed.

3.  **Step Execution (Iterative Process)**:
    *   The `Orchestrator` retrieves the next step from the protocol.
    *   The step is translated into operations for `WorkcellRuntime`.
    *   Operations may be dispatched as asynchronous tasks via Celery (using Redis as broker). `PraxisState` can be used to pass simple parameters to these tasks if the task itself doesn't have direct access to the richer in-memory context of the `Orchestrator`.
    *   `WorkcellRuntime` executes operations, interacting with devices. Device operational states are managed within `WorkcellRuntime`.
    *   Upon completion of an operation/task:
        *   The result is reported back.
        *   The `Orchestrator` updates its in-memory `ProtocolState` and `AssetManagerState` (which includes the state of assets on the deck).
        *   If simple data needs to be passed to subsequent distinct steps (especially if asynchronous), it might be written to `PraxisState`.
        *   Relevant changes (e.g., asset status, step completion, measurements) are logged to the database.

4.  **Data Handling**:
    *   Data generated during steps is captured.
    *   Complex data is typically managed within the in-memory `ProtocolState` or stored directly to the database/file system.
    *   `PraxisState` might store flags or simple summaries related to data generation if needed by other steps.

5.  **Error Handling**:
    *   If an error occurs:
        *   The error is logged to the database.
        *   The in-memory `ProtocolState` is updated.
        *   `PraxisState` might be updated with error flags if other parts of a distributed workflow need to be aware.
        *   The system attempts to enter a safe state.

6.  **Protocol Completion/Termination**:
    *   Upon successful completion or termination:
        *   The final status and any summary data from in-memory state objects (like `ProtocolState`) are persisted to the database.
        *   The `PraxisState` Redis key for the run might be cleared or left for archival (depending on policy, though `clear()` is available).
        *   Resources are released by `WorkcellRuntime`.

---

## Summary

Praxis employs a layered and distributed state management strategy:
-   **`PraxisState`** provides run-specific, Redis-backed storage for simple, JSON-serializable data shared across protocol steps.
-   **`WorkcellRuntime`** manages the live, operational state of hardware.
-   The **Database (PostgreSQL)** is the source of truth for persistent configurations, historical data, and the canonical state of assets.
-   Rich **In-Memory Pydantic Models & Objects** are used by services like the Orchestrator and AssetManager to manage the complex, active state of the application during operation, including the detailed state of the workcell deck and the assets upon it.
-   **Redis** also supports Celery task management and distributed locking.

Together, these components provide a robust framework for tracking and managing the complex state of an automated laboratory environment.
