# Service Layer Reference

The service layer implements business logic and provides a clean interface for the API layer.

## Overview

Services follow a consistent pattern:

```python
class EntityService(CRUDBase[EntityOrm, EntityCreate, EntityUpdate]):
    """Service for entity operations."""

    async def get(self, session: AsyncSession, id: str) -> Entity:
        ...

    async def list(self, session: AsyncSession, filters: SearchFilters) -> list[Entity]:
        ...

    async def create(self, session: AsyncSession, data: EntityCreate) -> Entity:
        ...

    async def update(self, session: AsyncSession, id: str, data: EntityUpdate) -> Entity:
        ...

    async def delete(self, session: AsyncSession, id: str) -> None:
        ...
```

## Core Services

### ProtocolService

Manages protocol definitions and discovery.

```python
from praxis.backend.services import protocol_service

# Get a protocol
protocol = await protocol_service.get(session, protocol_id)

# List with filters
protocols = await protocol_service.list(
    session,
    filters=SearchFilters(search="transfer", category="Liquid Handling")
)

# Get with execution history
protocol = await protocol_service.get_with_runs(session, protocol_id)
```

### ProtocolRunService

Manages protocol execution records.

```python
from praxis.backend.services import protocol_run_service

# Create a new run
run = await protocol_run_service.create(session, ProtocolRunCreate(
    protocol_id=protocol_id,
    parameters=params,
    status=RunStatus.PENDING
))

# Update status
await protocol_run_service.update_status(session, run.id, RunStatus.RUNNING)

# Get run with logs
run = await protocol_run_service.get_with_logs(session, run_id)
```

### MachineService

Manages laboratory instruments.

```python
from praxis.backend.services import machine_service

# List idle machines
machines = await machine_service.list(
    session,
    filters=SearchFilters(status=MachineStatus.IDLE)
)

# Update status
await machine_service.update_status(session, machine_id, MachineStatus.RUNNING)

# Get with connection info
machine = await machine_service.get_with_connection(session, machine_id)
```

### ResourceService

Manages labware and consumables.

```python
from praxis.backend.services import resource_service

# List available plates
plates = await resource_service.list(
    session,
    filters=SearchFilters(category="Plate", status=ResourceStatus.AVAILABLE)
)

# Decrement quantity (for consumables)
await resource_service.decrement_quantity(session, tip_rack_id, amount=8)

# Check availability
available = await resource_service.check_availability(
    session,
    resource_ids=[r1, r2, r3]
)
```

### DeckService

Manages deck layouts and positions.

```python
from praxis.backend.services import deck_service

# Get deck for workcell
deck = await deck_service.get_for_workcell(session, workcell_id)

# Update slot assignment
await deck_service.assign_slot(
    session,
    deck_id=deck.id,
    slot="1",
    resource_id=plate.id
)

# Get deck state
state = await deck_service.get_state(session, deck_id)
```

### WorkcellService

Manages workcell configurations.

```python
from praxis.backend.services import workcell_service

# Get default workcell
workcell = await workcell_service.get_default(session)

# Get with all components
workcell = await workcell_service.get_with_components(session, workcell_id)
```

## Discovery Services

### DiscoveryService

Syncs definitions from PyLabRobot.

```python
from praxis.backend.services import discovery_service

# Sync all definitions
result = await discovery_service.sync_all(session)
# Returns: {"machines": 15, "resources": 60, "protocols": 3}

# Sync specific type
await discovery_service.sync_machine_definitions(session)
await discovery_service.sync_resource_definitions(session)
await discovery_service.sync_protocols(session)
```

### MachineDefinitionService

Manages machine type definitions.

```python
from praxis.backend.services import machine_definition_service

# List all definitions
definitions = await machine_definition_service.list(session)

# Search by manufacturer
opentrons = await machine_definition_service.list(
    session,
    filters=SearchFilters(manufacturer="Opentrons")
)

# Get by FQN
flex = await machine_definition_service.get_by_fqn(
    session,
    "pylabrobot.liquid_handling.backends.opentrons.OpentronsBackend"
)
```

### ResourceDefinitionService

Manages resource type definitions.

```python
from praxis.backend.services import resource_definition_service

# List by category
plates = await resource_definition_service.list(
    session,
    filters=SearchFilters(category="Plate")
)

# Search
results = await resource_definition_service.search(session, "corning 96")
```

## Utility Functions

### Query Builder

```python
from praxis.backend.services.utils.query_builder import apply_filters

# Apply search filters to a query
stmt = select(ProtocolOrm)
stmt = apply_filters(stmt, ProtocolOrm, filters)
```

### Accession ID Generator

```python
from praxis.backend.utils.accession import generate_accession_id

# Generate unique accession IDs
id = generate_accession_id("PROTO")  # PROTO-A1B2C3
id = generate_accession_id("MACH")   # MACH-X4Y5Z6
```

## Error Handling

Services raise specific exceptions:

```python
from praxis.backend.services.exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    ValidationError,
    ConflictError
)

try:
    protocol = await protocol_service.get(session, "nonexistent")
except EntityNotFoundError as e:
    # Handle not found
    pass

try:
    await resource_service.acquire(session, resource_id, run_id)
except ConflictError as e:
    # Resource already in use
    pass
```

## Transaction Management

Services expect a session to be passed in:

```python
from praxis.backend.db import async_session_maker

async with async_session_maker() as session:
    try:
        # Multiple operations in one transaction
        machine = await machine_service.create(session, machine_data)
        await deck_service.assign_slot(session, deck_id, "1", machine.id)

        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

For API routes, use the dependency:

```python
from praxis.backend.api.deps import get_db

@router.post("/machines")
async def create_machine(
    data: MachineCreate,
    session: AsyncSession = Depends(get_db)
):
    return await machine_service.create(session, data)
```

## Testing Services

```python
import pytest
from praxis.backend.services import protocol_service

@pytest.mark.asyncio
async def test_create_protocol(db_session):
    protocol = await protocol_service.create(
        db_session,
        ProtocolCreate(
            name="Test Protocol",
            source_path="/protocols/test.py"
        )
    )

    assert protocol.id is not None
    assert protocol.name == "Test Protocol"

@pytest.mark.asyncio
async def test_list_protocols(db_session, sample_protocols):
    protocols = await protocol_service.list(
        db_session,
        filters=SearchFilters(limit=10)
    )

    assert len(protocols) == len(sample_protocols)
```
