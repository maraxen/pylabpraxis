# Praxis Overview

The PylabPraxis backend is a sophisticated Python-based platform, built with FastAPI, designed to automate laboratory workflows. It focuses on orchestrating experimental protocols, managing physical and logical laboratory assets, and maintaining a real-time interface with PyLabRobot-controlled hardware.

graph TD
    subgraph Frontend
        Flutter_Frontend[Flutter Frontend]
    end

    subgraph Backend (Python FastAPI)
        API_Layer[FastAPI API Layer]
        Orchestrator[Orchestrator]
        AssetManager[AssetManager]
        WorkcellRuntime[WorkcellRuntime]
        Workcell[Workcell (PLR Object Container)]
        DataServices[Data Services]
        Models[ORM Models]
        ProtocolDiscoveryService[Protocol Discovery Service]
        PraxisState[PraxisState (Runtime Data)]
        PraxisRunContext[PraxisRunContext (Execution Context)]
        UtilityModules[Utility Modules]
    end

    subgraph External Services
        PostgreSQL[PostgreSQL Database]
        Keycloak[Keycloak (Auth Server)]
        Redis[Redis (Cache/State/Locks)]
        PyLabRobot[PyLabRobot]
        Protocol_Files[Protocol Files (Python Code)]
        Docker_SMTP[Docker SMTP Server]
    end

    Flutter_Frontend -- HTTP/REST --> API_Layer
    Flutter_Frontend -- WebSockets --> API_Layer

    API_Layer -- calls --> Orchestrator
    API_Layer -- calls --> AssetManager
    API_Layer -- calls --> WorkcellRuntime
    API_Layer -- queries --> ProtocolDiscoveryService

    Orchestrator -- manages execution --> AssetManager
    Orchestrator -- manages execution --> WorkcellRuntime
    Orchestrator -- logs via --> DataServices
    Orchestrator -- uses for state --> Redis
    Orchestrator -- fetches definitions --> DataServices
    Orchestrator -- loads functions from --> Protocol_Files
    Orchestrator -- manages --> PraxisState
    Orchestrator -- passes --> PraxisRunContext
    Orchestrator -- uses --> UtilityModules
    Orchestrator -- sends notifications via --> UtilityModules

    AssetManager -- manages live PLR --> WorkcellRuntime
    AssetManager -- persists via --> DataServices
    AssetManager -- uses for locking --> Redis
    AssetManager -- interacts with --> Workcell
    AssetManager -- uses --> UtilityModules

    WorkcellRuntime -- controls hardware --> PyLabRobot
    WorkcellRuntime -- updates/fetches state --> DataServices
    WorkcellRuntime -- manages live objects from --> Workcell
    WorkcellRuntime -- uses --> UtilityModules

    ProtocolDiscoveryService -- scans --> Protocol_Files
    ProtocolDiscoveryService -- stores definitions --> DataServices
    ProtocolDiscoveryService -- uses --> UtilityModules

    PraxisState -- stores data in --> Redis
    PraxisRunContext -- carries --> PraxisState
    PraxisRunContext -- carries --> DataServices (session)

    DataServices -- interacts with --> PostgreSQL
    DataServices -- uses --> Models

    PostgreSQL -- stores data --> Models

    Keycloak -- provides auth to --> API_Layer
    Keycloak -- manages user data --> PostgreSQL (Keycloak's own DB)

    Redis -- stores runtime state/locks --> Orchestrator
    Redis -- stores runtime state/locks --> AssetManager
    Redis -- stores runtime state/locks --> PraxisState
    Redis -- used by --> UtilityModules

    PyLabRobot -- provides objects & control --> WorkcellRuntime
    PyLabRobot -- introspection for --> ProtocolDiscoveryService
    PyLabRobot -- introspection for --> AssetManager

    UtilityModules -- provides helpers to --> Orchestrator
    UtilityModules -- provides helpers to --> AssetManager
    UtilityModules -- provides helpers to --> WorkcellRuntime
    UtilityModules -- provides helpers to --> ProtocolDiscoveryService
    UtilityModules -- interacts with --> Redis
    UtilityModules -- interacts with --> PostgreSQL (for db setup)
    UtilityModules -- interacts with --> Docker_SMTP

    style Orchestrator fill:#f9f,stroke:#333,stroke-width:2px
    style AssetManager fill:#f9f,stroke:#333,stroke-width:2px
    style WorkcellRuntime fill:#f9f,stroke:#333,stroke-width:2px
    style Workcell fill:#ccf,stroke:#333,stroke-width:2px
    style API_Layer fill:#bbf,stroke:#333,stroke-width:2px
    style DataServices fill:#ddf,stroke:#333,stroke-width:2px
    style Models fill:#eef,stroke:#333,stroke-width:2px
    style PostgreSQL fill:#afa,stroke:#333,stroke-width:2px
    style Keycloak fill:#ffc,stroke:#333,stroke-width:2px
    style Redis fill:#ffc,stroke:#333,stroke-width:2px
    style PyLabRobot fill:#cfa,stroke:#333,stroke-width:2px
    style ProtocolDiscoveryService fill:#f9f,stroke:#333,stroke-width:2px
    style Protocol_Files fill:#e0e0e0,stroke:#333,stroke-width:2px
    style PraxisState fill:#ffd,stroke:#333,stroke-width:2px
    style PraxisRunContext fill:#ffd,stroke:#333,stroke-width:2px
    style UtilityModules fill:#ddd,stroke:#333,stroke-width:2px
    style Docker_SMTP fill:#ffb,stroke:#333,stroke-width:2px

## **High-Level Backend Overview**

Core Architectural Principles:

* API-First Design: The backend exposes a comprehensive REST API via FastAPI, enabling seamless interaction with the Flutter-based frontend and other external systems.
* Modular Componentry: Logic is strictly separated into distinct core components (Orchestrator, AssetManager, WorkcellRuntime, Workcell) with clearly defined responsibilities, promoting maintainability and scalability.
* Database-Centric Data Management: PostgreSQL serves as the primary persistent data store for all definitions, logs, and asset states. Data access is abstracted through a dedicated service layer utilizing SQLAlchemy ORMs for robust and consistent interactions.
* PyLabRobot Integration: Deep integration with the PyLabRobot library allows for direct control and abstraction of various laboratory instruments and resources.
* Containerization: The entire backend ecosystem is designed for deployment using Docker and Docker Compose, facilitating isolated and reproducible environments.
* Authentication & Authorization: Keycloak is integrated to manage user identities and access control.

Key Backend Components & Their Roles:

1. FastAPI Application & API Layer (main.py, backend/api/)
   * main.py: Serves as the application's entry point, handling FastAPI initialization, global logging configuration, database schema setup (within its lifespan function), and the instantiation of critical singleton services like the Orchestrator.
   * backend/api/: Contains various FastAPI routers (protocols.py, assets.py, workcell\_api.py) that define and group API endpoints. These endpoints manage protocol discovery and execution, asset querying and modification, and real-time workcell state monitoring. They rely on dependency injection (backend/api/dependencies.py) to securely access database sessions and core business logic components.
2. Core Business Logic (backend/core/)
   * Orchestrator (orchestrator.py): This is the central brain for protocol execution. It is responsible for fetching protocol definitions from the database, preparing the execution environment (including PraxisState for run-specific data), injecting required assets (by interacting with AssetManager), and executing the Python functions defined as protocols. It also manages the comprehensive logging of protocol runs and individual function calls to the database and processes control commands (e.g., pause, resume, cancel) during execution.
   * AssetManager (asset\_manager.py): Manages the entire lifecycle and allocation of physical laboratory assets. It serves as the primary interface for acquiring and releasing machines and resources for protocol runs, ensuring proper locking and status updates in the database. AssetManager leverages dedicated data services for its database interactions and coordinates directly with WorkcellRuntime to activate and deactivate the live PyLabRobot hardware instances. It also includes functionality to synchronize PyLabRobot definitions with the application's asset catalog in the database.
   * WorkcellRuntime (workcell\_runtime.py): Manages the *live, operational instances* of PyLabRobot objects. It's responsible for dynamically instantiating PyLabRobot Machine and Resource objects based on database definitions (e.g., FQNs and configuration parameters). It performs the actual setup() and stop() calls on these objects to connect/disconnect from hardware. WorkcellRuntime holds references to the primary Workcell instance (which contains the base PLR objects) and facilitates their placement on simulated or physical decks. It also provides structured representations of the live deck state for frontend visualization.
   * Workcell (workcell.py): This class serves as a clean, high-level container for *all configured PyLabRobot objects* (machines and resources) within the lab setup. It is primarily responsible for holding these PLR instances in memory (potentially loaded from configuration files) and managing their internal state (e.g., content levels, positions) through PyLabRobot's serialization mechanisms. It offers methods for saving and loading the entire workcell's state (including nested resource states) to/from JSON files and for continuous backup. Crucially, Workcell does not directly manage asset allocation status in the database or implement asset locking; these responsibilities are delegated to AssetManager and WorkcellRuntime.
   * Deck Management (New Approach): The dedicated Deck class in backend/core/deck.py is being deprecated. Instead, deck layouts will be handled through:
     * Dynamic Inference: A utility to infer deck layouts on the fly based on protocol arguments.
     * User File Uploads: Allowing users to upload custom deck layout files.
     * In-Function Layout Generation with @deck\_layout Decorator: Enabling programmatic definition of deck layouts directly within protocol files using a new @deck\_layout decorator.
   * Protocol Definition & Discovery: This crucial aspect of the backend enables the system to understand and manage executable laboratory protocols:
     * @protocol\_function Decorator: Developers define protocols as standard Python functions, annotated with this decorator (e.g., in backend/protocol\_core/decorators.py). This decorator is used to embed rich metadata (name, version, description, parameters with type hints and constraints, required assets, execution flags like is\_top\_level) directly within the function's code. It also wraps the original function with an async-capable executor that:
     * Enforces that the protocol is only run via an Orchestrator that provides a valid PraxisRunContext.
     * Injects shared run state into the function based on its signature.
     * Handles automatic logging and run-control commands (pause, resume, cancel).
     * Allows both async and sync functions to be decorated, safely running synchronous
        code in a separate thread to prevent blocking.
     * ProtocolDiscoveryService: This service (in backend/protocol\_core/discovery\_service.py) is responsible for scanning configured Python code sources (Git repositories or local file system paths). It identifies @protocol\_function decorated functions, extracts their embedded metadata, and for undecorated functions, attempts to infer basic protocol information from their signatures. This collected metadata is then converted into structured Pydantic models.
     * FunctionProtocolDefinitionOrm (ORM Models): The structured metadata extracted by the ProtocolDiscoveryService is persisted into the PostgreSQL database using the FunctionProtocolDefinitionOrm SQLAlchemy ORM model (defined in backend/models/protocol\_definitions\_orm.py). This model, along with related ParameterDefinitionOrm and AssetDefinitionOrm, stores a canonical, static definition of each discoverable protocol.
     * Orchestrator's Role in Inspection & Execution:
      At startup, the Orchestrator is responsible for populating an in-memory PROTOCOL_REGISTRY. It does this by fetching all FunctionProtocolDefinitionOrm records from the database and creating a ProtocolRuntimeInfo object for each, which holds the function's definition, its database ID, and a reference to the actual Python function object.

      When a protocol run is initiated, the Orchestrator's primary role is to create the initial PraxisRunContext and set it as the active context using Python's contextvars module. This makes the context implicitly available to the entire downstream async call stack. It then invokes the top-level protocol function.
     When a protocol run is initiated, the Orchestrator retrieves the relevant FunctionProtocolDefinitionOrm from the database, which includes its unique database ID. The Orchestrator's _prepare_protocol_code method dynamically loads the Python module to get a reference to the decorated function.
      The_prepare_arguments method then prepares the arguments for the protocol's execution wrapper. Crucially, this now includes two special keyword arguments:
      `__praxis_run_context__`: The fully-formed PraxisRunContext for the run.
      `__function_db_id__`: The database ID of the FunctionProtocolDefinitionOrm being executed.
   * Protocol Run Context & State Management (backend/core/run\_context.py, backend/utils/state.py):
     * PraxisState: This class (from backend/utils/state.py) represents the *canonical, mutable shared state* for a single top-level protocol run. It is designed to hold all experimental parameters, intermediate results, and tracking information that needs to persist across different steps or function calls within a run. It is backed by Redis for efficient runtime in-memory access and persistence, allowing for robust state management even across application restarts (for pause/resume scenarios). The Orchestrator manages the lifecycle of a PraxisState instance for each run.
     * PraxisRunContext: This immutable object (from backend/core/run\_context.py) is the central carrier of essential execution and logging information that is passed down the call stack of @protocol\_function calls. For each function call, the PraxisRunContext provides:
       * run\_guid: The unique identifier of the top-level protocol run.
       * protocol\_run\_db\_id: The database ID of the ProtocolRunOrm entry.
       * function\_definition\_db\_id: The database ID of the currently executing FunctionProtocolDefinitionOrm.
       * parent\_function\_call\_log\_id: The database ID of the calling function's log entry (for building the call hierarchy).
       * db\_session: The SQLAlchemy session for database interactions within the function's scope (e.g., for logging).
       * canonical\_state: A reference to the mutable PraxisState object for the current run.
         The @protocol\_function decorator is responsible for creating and propagating updated PraxisRunContext instances to maintain the correct call hierarchy and context for nested protocol function calls.
      Note: The database ID of the currently executing function is now passed explicitly to the decorator wrapper by the caller (i.e., the Orchestrator or the context's nested call method) alongside the context itself.
     * Implicit Nested Call Tracking
        A primary design goal of Praxis is to allow protocol authors to write simple, standard Python code. The framework is architected to automatically track the full hierarchy of nested calls without requiring special syntax from the user.

    This is achieved through a combination of the in-memory PROTOCOL_REGISTRY and contextvars:

    When a decorated function like await some_other_function() is called, its @protocol_function wrapper executes.
    The wrapper looks up its own metadata (including its database ID) from the PROTOCOL_REGISTRY.
    It retrieves the caller's PraxisRunContext from the active ContextVar. This gives it the parent's identity for logging.
    It logs its own execution, creating a parent-child link in the database, and allows for
    run related statistics (failure modes, time to run, etc.) to be tracked, with different
    versions cleanly separted.
    It then creates a new context for its own execution scope and sets this as the new active context in the ContextVar before running the user's code.
    When the function completes, the wrapper restores the ContextVar to its previous state.
    This process ensures every call is automatically logged and tracked in the correct hierarchy, allowing developers to write natural Python code.
3. Data Service Layer (backend/services/)
   * This package provides a crucial abstraction layer, encapsulating all direct database interactions. Instead of direct ORM manipulation in business logic, components interact with dedicated service classes.
   * protocol\_data\_service.py: Manages CRUD operations for protocol definitions, protocol run instances, and detailed function call logs.
   * asset\_data\_service.py: Handles broad asset-related data, including resource definitions (ResourceDefinitionCatalogOrm) and resource instances (ResourceInstanceOrm). It provides methods for creating, retrieving, updating, and listing these assets.
   * machine\_data\_service.py: Specializes in managing machine-specific data, including MachineOrm entries. It provides methods for CRUD operations on machine definitions, tracking their status (MachineStatusEnum), and managing their association with protocol runs.
   * workcell\_data\_service.py: Focuses on managing data related to the overall workcell configuration, including WorkcellOrm and potentially other high-level workcell metadata. It provides methods for defining and retrieving workcell-specific settings and configurations.
   * deck\_data\_service.py: Handles the persistent storage and retrieval of DeckLayoutOrm and DeckSlotOrm models, managing predefined deck configurations.
   * praxis\_orm\_service.py: Offers a more generalized interface for common database operations, used by various parts of the system.
   * All these services utilize SQLAlchemy ORM models defined in backend/models/ to interact with the PostgreSQL database.
4. Utility Modules (backend/utils/)
   * This package contains various helper modules that provide common functionalities and abstractions used across the backend.
   * db.py: This foundational module handles all database connectivity setup for the PostgreSQL database. It defines the SQLAlchemy async\_engine, AsyncSessionLocal (for creating asynchronous sessions), the Base class for ORM models, and the init\_praxis\_db\_schema() function (which is called during application startup within main.py's lifespan function to create database tables). It also manages the loading of database connection strings from configuration.
   * errors.py: Defines custom exception classes (e.g., WorkcellRuntimeError, AssetAcquisitionError, ProtocolCancelledError). These exceptions provide a structured way to handle specific error conditions within the application, allowing for more precise error logging, reporting, and recovery mechanisms.
   * logging.py: Provides a centralized and standardized approach to logging within the backend. It offers a get\_logger function for consistent logger instantiation and includes powerful decorators (log\_async\_runtime\_errors, log\_runtime\_errors) that automatically catch, log, and optionally re-raise exceptions from both asynchronous and synchronous functions. This ensures consistent error reporting and debugging across the application.
   * notify.py: Provides utilities for sending various types of notifications (e.g., email, SMS). This module can be integrated into protocols or the Orchestrator to alert users about protocol status changes, errors, or other important events.
   * plr\_inspection.py: Contains helper functions for introspecting PyLabRobot (PLR) classes and objects. It's used by the AssetManager (specifically in sync\_pylabrobot\_definitions) to extract metadata (like constructor parameters, resource dimensions, categories) from PLR objects, which is then used to populate the ResourceDefinitionCatalogOrm in the database.
   * redis\_lock.py: Implements a distributed locking mechanism using Redis. This utility is crucial for managing concurrent access to shared resources across different backend processes or protocol runs, preventing race conditions and ensuring data integrity. It can be used by AssetManager or Orchestrator for fine-grained control over critical sections.
   * run\_control.py: Provides functions for sending and retrieving control commands (e.g., "PAUSE", "RESUME", "CANCEL") to a running protocol. These commands are typically communicated via Redis and are actively monitored and acted upon by the Orchestrator to manage the lifecycle of a protocol run.
   * notify.py: Provides a standardized interface for sending various types of notifications (e.g., email, SMS, push notifications). This module is primarily used by the Orchestrator to inform users about the lifecycle events of their protocol runs (start, completion, success, failure, pause, resume, cancel) and can also be used for other system-level alerts. It integrates with an external SMTP server for email delivery.
5. External Services
   * PostgreSQL Database: The primary persistent data store for all definitions, logs, and asset states. Available via docker.
   * Keycloak (Auth Server): Integrated to manage user identities and access control, also managing its own user data in a PostgreSQL database. Available via Docker.
   * Redis (Cache/State/Locks): Used for efficient runtime in-memory caching, managing shared state, and implementing distributed locking mechanisms to prevent race conditions. Available via Docker.
   * PyLabRobot: The core library providing objects and control mechanisms for various laboratory instruments and resources.
   * Protocol Files (Python Code): The source Python files containing the definitions of laboratory protocols, which are discovered and executed by the backend. User-provided.
   * SMTP Server: A Simple Mail Transfer Protocol (SMTP) server (e.g., Postfix, Mailhog for development) used by the praxis.backend.utils.notify module to send email notifications. This ensures that the backend can dispatch alerts and updates to users about protocol statuses or system events. Available via Docker.

Key Database Interaction Points:

* Application Startup (main.py): Ensures the database schema is initialized and all necessary tables are created via init\_praxis\_db\_schema() (called from main.py's lifespan function).
* Protocol Execution (Orchestrator): Persistently logs protocol runs and individual function calls, updating their statuses and storing input/output data and state snapshots using protocol\_data\_service.
* Asset Management (AssetManager, WorkcellRuntime): AssetManager drives the updates to MachineOrm (via machine\_data\_service) and ResourceInstanceOrm (via asset\_data\_service) statuses (e.g., IN\_USE, AVAILABLE) and manages asset definitions (ResourceDefinitionCatalogOrm) through relevant data services. WorkcellRuntime updates machine and resource instance statuses based on their live operational state and fetches necessary configuration from the database during instantiation.
* API Endpoints (backend/api/): All API calls needing persistent data interaction utilize injected AsyncSession objects and rely on the data service layer to perform queries and updates.
