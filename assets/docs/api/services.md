# Service Layer Reference

The service layer implements business logic and provides a clean interface for the API layer.

## Core Services

### Protocol Definition Service

**Class:** `praxis.backend.services.protocol_definition.ProtocolDefinitionCRUDService`

Manages protocol definitions, which are the static templates for execution.
- **Responsibilities:**
    - Creating, reading, updating, and deleting protocol definitions.
    - Managing parameters and metadata associated with protocols.
    - Handling protocol versioning (if applicable).

### Protocol Run Service

**Class:** `praxis.backend.services.protocols.ProtocolRunService`

Manages the execution instances of protocols.
- **Responsibilities:**
    - Creating new protocol runs from definitions.
    - Tracking execution status (PENDING, RUNNING, COMPLETED, FAILED).
    - Storing execution logs and telemetry data.
    - Interfacing with the scheduler to queue runs.

### Machine Service

**Class:** `praxis.backend.services.machine.MachineService`

Manages laboratory machines and instruments.
- **Responsibilities:**
    - Registering new machines (liquid handlers, plate readers, etc.).
    - Tracking machine status (IDLE, BUSY, OFFLINE).
    - Managing machine configuration and connection details.
    - Integration with PyLabRobot backends.

### Resource Service

**Class:** `praxis.backend.services.resource.ResourceService`

Manages labware and consumables (resources).
- **Responsibilities:**
    - Tracking inventory of plates, tips, troughs, etc.
    - Managing resource properties (e.g., volume, location).
    - Handling resource definitions and types.

### Deck Service

**Class:** `praxis.backend.services.deck.DeckService`

Manages the physical layout of machine decks.
- **Responsibilities:**
    - Defining deck slots and positions.
    - Tracking what resources are currently on the deck.
    - Validating deck layouts for protocol execution.

### Workcell Service

**Class:** `praxis.backend.services.workcell.WorkcellService`

Manages the overall workcell configuration, which may contain multiple machines.
- **Responsibilities:**
    - Aggregating machine and resource status.
    - Providing a unified view of the automation system.

## Discovery Services

### Discovery Service

**Class:** `praxis.backend.services.discovery_service.DiscoveryService`

Handles the auto-discovery of protocols and hardware definitions.
- **Responsibilities:**
    - Scanning directories for python protocol files.
    - Parsing protocol parameters and metadata.
    - Syncing discovered items with the database.

### Machine Type Definition Service

**Class:** `praxis.backend.services.machine_type_definition.MachineTypeDefinitionService`

Provides access to static definitions of machine types supported by the system (e.g., from PyLabRobot).

### Resource Type Definition Service

**Class:** `praxis.backend.services.resource_type_definition.ResourceTypeDefinitionService`

Provides access to static definitions of resource types (plates, tip racks) supported by the system.

## Utility Services

### CRUD Base

**Class:** `praxis.backend.services.utils.crud_base.CRUDBase`

A generic base class providing standard Create, Read, Update, Delete operations for SQLAlchemy models. Most services inherit from this to provide consistent data access patterns.
