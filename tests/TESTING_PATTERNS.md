# PyLabPraxis Testing Patterns and Examples

This document provides detailed testing patterns and real examples for each layer of the PyLabPraxis backend.

## Table of Contents
1. [API Layer Testing](#api-layer-testing)
2. [Service Layer Testing](#service-layer-testing)
3. [Core Component Testing](#core-component-testing)
4. [Integration Testing](#integration-testing)
5. [Mocking Strategies](#mocking-strategies)
6. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)

---

## API Layer Testing

### Pattern: CRUD Operations

**Objective**: Test full HTTP request/response cycle including validation, business logic, and persistence.

**Example: Create Operation**
```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.factories import WorkcellFactory, MachineFactory

@pytest.mark.asyncio
async def test_create_resource(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a resource via POST /api/v1/resources/."""
    # SETUP: Create dependencies
    workcell = WorkcellFactory()
    machine = MachineFactory(workcell=workcell)
    await db_session.flush()  # Generate IDs

    # ACT: Make API request
    response = await client.post(
        "/api/v1/resources/",
        json={
            "name": "test_resource",
            "fqn": "test.resource",
            "machine_id": str(machine.accession_id),
        },
    )

    # ASSERT: Check response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_resource"
    assert data["machine_id"] == str(machine.accession_id)

    # ASSERT: Verify database persistence
    result = await db_session.get(ResourceOrm, data["accession_id"])
    assert result is not None
    assert result.name == "test_resource"
```

**Example: Read Operation**
```python
@pytest.mark.asyncio
async def test_get_resource(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving a resource by ID via GET /api/v1/resources/{id}."""
    # SETUP: Create test resource
    resource = ResourceFactory()
    await db_session.flush()

    # ACT: Make GET request
    response = await client.get(f"/api/v1/resources/{resource.accession_id}")

    # ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["accession_id"] == str(resource.accession_id)
    assert data["name"] == resource.name
```

**Example: List Operation with Filtering**
```python
@pytest.mark.asyncio
async def test_list_resources_with_filter(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test listing resources with machine_id filter."""
    # SETUP: Create multiple resources
    machine1 = MachineFactory()
    machine2 = MachineFactory()
    ResourceFactory.create_batch(3, machine=machine1)
    ResourceFactory.create_batch(2, machine=machine2)
    await db_session.flush()

    # ACT: Request resources for machine1 only
    response = await client.get(
        f"/api/v1/resources/?machine_id={machine1.accession_id}"
    )

    # ASSERT: Verify filtered results
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for item in data:
        assert item["machine_id"] == str(machine1.accession_id)
```

**Example: Update Operation**
```python
@pytest.mark.asyncio
async def test_update_resource(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test updating a resource via PATCH."""
    # SETUP: Create resource
    resource = ResourceFactory(name="old_name")
    await db_session.flush()

    # ACT: Update via API
    response = await client.patch(
        f"/api/v1/resources/{resource.accession_id}",
        json={"name": "new_name"},
    )

    # ASSERT: Check response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "new_name"

    # ASSERT: Verify database was updated
    await db_session.refresh(resource)
    assert resource.name == "new_name"
```

**Example: Delete Operation**
```python
@pytest.mark.asyncio
async def test_delete_resource(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test deleting a resource via DELETE."""
    # SETUP: Create resource
    resource = ResourceFactory()
    resource_id = resource.accession_id
    await db_session.flush()

    # ACT: Delete via API
    response = await client.delete(f"/api/v1/resources/{resource_id}")

    # ASSERT: Check response
    assert response.status_code == 200

    # ASSERT: Verify resource no longer exists
    deleted = await db_session.get(ResourceOrm, resource_id)
    assert deleted is None
```

### Pattern: Error Handling

**Example: Not Found Error**
```python
@pytest.mark.asyncio
async def test_get_resource_not_found(client: AsyncClient) -> None:
    """Test 404 error when resource doesn't exist."""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/v1/resources/{fake_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

**Example: Validation Error**
```python
@pytest.mark.asyncio
async def test_create_resource_invalid_data(client: AsyncClient) -> None:
    """Test 422 validation error with invalid data."""
    response = await client.post(
        "/api/v1/resources/",
        json={"name": ""},  # Empty name should fail validation
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("name" in str(err) for err in errors)
```

**Example: Conflict Error**
```python
@pytest.mark.asyncio
async def test_create_duplicate_resource(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test 409 conflict when creating duplicate resource."""
    resource = ResourceFactory(name="unique_name")
    await db_session.flush()

    # Try to create another with same name
    response = await client.post(
        "/api/v1/resources/",
        json={"name": "unique_name"},
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()
```

---

## Service Layer Testing

### Pattern: CRUD Service Methods

**Example: Service Method with Database**
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from praxis.backend.services.deck import DeckService
from tests.factories import DeckFactory

@pytest.mark.asyncio
async def test_deck_service_get_by_id(db_session: AsyncSession) -> None:
    """Test DeckService.get_by_id method."""
    # SETUP: Create test deck
    deck = DeckFactory()
    await db_session.flush()

    # ACT: Call service method
    service = DeckService(db_session)
    result = await service.get_by_id(deck.accession_id)

    # ASSERT: Verify result
    assert result is not None
    assert result.accession_id == deck.accession_id
    assert result.name == deck.name
```

**Example: Service Method Returning None**
```python
@pytest.mark.asyncio
async def test_deck_service_get_by_id_not_found(db_session: AsyncSession) -> None:
    """Test DeckService.get_by_id returns None for non-existent deck."""
    service = DeckService(db_session)
    fake_id = uuid.uuid4()

    result = await service.get_by_id(fake_id)

    assert result is None
```

**Example: Service Method with Business Logic**
```python
@pytest.mark.asyncio
async def test_deck_service_remap_machine_id(db_session: AsyncSession) -> None:
    """Test DeckService correctly remaps parent_machine_id to machine_id."""
    # SETUP: Create deck with parent_machine_accession_id
    machine = MachineFactory()
    deck = DeckFactory(parent_machine_accession_id=machine.accession_id)
    await db_session.flush()

    # ACT: Retrieve via service
    service = DeckService(db_session)
    result = await service.get_by_id(deck.accession_id)

    # ASSERT: Verify remapping occurred
    assert result.machine_id == str(machine.accession_id)
    assert result.parent_accession_id == str(machine.accession_id)
```

### Pattern: Service Methods with External Dependencies

**Example: Mocking Redis in Service**
```python
import pytest
from unittest.mock import AsyncMock, patch
from praxis.backend.services.state import PraxisState

@pytest.mark.asyncio
async def test_praxis_state_get_value():
    """Test PraxisState.get method with mocked Redis."""
    # SETUP: Mock Redis client
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b'{"key": "value"}'

    with patch('praxis.backend.services.state.redis.Redis', return_value=mock_redis):
        state = PraxisState(run_id=uuid.uuid4())

        # ACT: Get value from state
        result = await state.get("some_key")

        # ASSERT: Verify Redis was called
        assert result == {"key": "value"}
        mock_redis.get.assert_called_once()
```

**Example: Mocking Celery Task**
```python
import pytest
from unittest.mock import patch, MagicMock
from praxis.backend.services.scheduler import ProtocolScheduler

@pytest.mark.asyncio
async def test_scheduler_queues_task(db_session: AsyncSession):
    """Test that scheduler queues a Celery task."""
    # SETUP: Mock Celery task
    with patch('praxis.backend.core.celery_tasks.execute_protocol_run_task') as mock_task:
        mock_task.delay = MagicMock(return_value="task_id_123")

        scheduler = ProtocolScheduler(db_session)
        protocol_run = ProtocolRunFactory()

        # ACT: Schedule execution
        result = await scheduler.schedule_execution(protocol_run)

        # ASSERT: Verify task was queued
        assert result.celery_task_id == "task_id_123"
        mock_task.delay.assert_called_once_with(str(protocol_run.accession_id))
```

---

## Core Component Testing

### Pattern: Heavy Mocking for Isolated Units

**Example: AssetManager with Mocked Dependencies**
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from praxis.backend.core.asset_manager import AssetManager

@pytest.mark.asyncio
async def test_asset_manager_acquire_machine():
    """Test AssetManager.acquire_asset for a machine."""
    # SETUP: Create all mocks
    mock_db_session = AsyncMock()
    mock_workcell_runtime = MagicMock()
    mock_deck_service = AsyncMock()
    mock_machine_service = AsyncMock()
    mock_resource_service = AsyncMock()

    # Configure mock return values
    mock_machine = MagicMock()
    mock_machine.accession_id = uuid.uuid4()
    mock_machine.status = "AVAILABLE"
    mock_machine_service.get_by_name.return_value = mock_machine

    mock_live_machine = MagicMock()
    mock_workcell_runtime.get_live_machine.return_value = mock_live_machine

    # Create AssetManager with mocks
    asset_manager = AssetManager(
        db_session=mock_db_session,
        workcell_runtime=mock_workcell_runtime,
        deck_service=mock_deck_service,
        machine_service=mock_machine_service,
        resource_service=mock_resource_service,
    )

    # ACT: Acquire asset
    from praxis.backend.models import AssetRequirementModel
    requirement = AssetRequirementModel(name="liquid_handler", type="machine")
    result = await asset_manager.acquire_asset(
        protocol_run_accession_id=uuid.uuid4(),
        asset_requirement=requirement,
    )

    # ASSERT: Verify calls were made
    mock_machine_service.get_by_name.assert_called_once_with("liquid_handler")
    mock_workcell_runtime.get_live_machine.assert_called_once_with(mock_machine.accession_id)
    assert result == mock_live_machine
```

### Pattern: Testing State Changes

**Example: Orchestrator State Transitions**
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from praxis.backend.core.orchestrator import Orchestrator

@pytest.mark.asyncio
async def test_orchestrator_updates_run_status():
    """Test that Orchestrator updates protocol run status correctly."""
    # SETUP: Mock dependencies
    mock_db_session = AsyncMock()
    mock_asset_manager = AsyncMock()
    mock_workcell_runtime = MagicMock()

    mock_protocol_run = MagicMock()
    mock_protocol_run.accession_id = uuid.uuid4()
    mock_protocol_run.status = "PENDING"

    orchestrator = Orchestrator(
        db_session=mock_db_session,
        asset_manager=mock_asset_manager,
        workcell_runtime=mock_workcell_runtime,
    )

    # ACT: Execute protocol (which should update status)
    with patch.object(orchestrator, '_execute_protocol_function', return_value={"result": "ok"}):
        await orchestrator.execute_existing_protocol_run(mock_protocol_run, {})

    # ASSERT: Verify status was updated
    assert mock_protocol_run.status == "COMPLETED"
    mock_db_session.commit.assert_called()
```

---

## Integration Testing

### Pattern: Multi-Component Interaction

**Example: Protocol Execution Flow (Simplified)**
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.core.asset_manager import AssetManager
from tests.factories import ProtocolDefinitionFactory, MachineFactory

@pytest.mark.integration
@pytest.mark.asyncio
async def test_protocol_execution_end_to_end(db_session: AsyncSession):
    """Test complete protocol execution flow from scheduling to completion."""
    # SETUP: Create protocol definition and required assets
    protocol = ProtocolDefinitionFactory()
    machine = MachineFactory()
    await db_session.flush()

    # Create real services (not mocked)
    from praxis.backend.services.deck import DeckService
    from praxis.backend.services.machine import MachineService
    from praxis.backend.core.workcell_runtime import WorkcellRuntime

    deck_service = DeckService(db_session)
    machine_service = MachineService(db_session)
    workcell_runtime = WorkcellRuntime(db_session)

    asset_manager = AssetManager(
        db_session=db_session,
        workcell_runtime=workcell_runtime,
        deck_service=deck_service,
        machine_service=machine_service,
    )

    orchestrator = Orchestrator(
        db_session=db_session,
        asset_manager=asset_manager,
        workcell_runtime=workcell_runtime,
    )

    # ACT: Execute protocol
    result = await orchestrator.execute_protocol(
        protocol_name=protocol.name,
        user_params={"volume": 100},
    )

    # ASSERT: Verify execution completed
    assert result["status"] == "COMPLETED"
    assert "outputs" in result
```

---

## Mocking Strategies

### When to Mock vs. Use Real Objects

| Component | Strategy | Reason |
|-----------|----------|--------|
| Database | Use real (in transaction) | Need to test actual SQL and constraints |
| Redis | Mock | External dependency, state not critical for most tests |
| Celery | Mock | Async task queue, don't want actual task execution |
| PyLabRobot | Mock | Hardware abstraction, no real hardware in tests |
| Services | Use real in integration tests | Test inter-service communication |
| HTTP clients | Mock | External APIs shouldn't be called in tests |

### Mocking Patterns

**Pattern: Mock Async Function**
```python
from unittest.mock import AsyncMock

mock_function = AsyncMock(return_value="result")
result = await mock_function()
assert result == "result"
```

**Pattern: Mock Sync Function**
```python
from unittest.mock import MagicMock

mock_function = MagicMock(return_value="result")
result = mock_function()
assert result == "result"
```

**Pattern: Mock Property**
```python
from unittest.mock import PropertyMock, MagicMock

mock_obj = MagicMock()
type(mock_obj).status = PropertyMock(return_value="AVAILABLE")
assert mock_obj.status == "AVAILABLE"
```

**Pattern: Patch Module-Level Function**
```python
from unittest.mock import patch

with patch('praxis.backend.services.protocols.get_protocol') as mock_get:
    mock_get.return_value = ProtocolOrm(name="test")
    result = await some_function_that_calls_get_protocol()
```

**Pattern: Patch Class Method**
```python
with patch.object(AssetManager, 'acquire_asset', new_callable=AsyncMock) as mock_acquire:
    mock_acquire.return_value = MagicMock()
    result = await asset_manager.acquire_asset(...)
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Factory Not Bound to Session

**Problem**:
```python
deck = DeckFactory()  # Creates deck but not in test session!
```

**Solution**:
```python
# In API tests, client fixture handles this automatically
# In service tests, bind explicitly:
DeckFactory._meta.sqlalchemy_session = db_session
deck = DeckFactory()
```

### Pitfall 2: Not Flushing Before Using IDs

**Problem**:
```python
machine = MachineFactory()
# machine.accession_id is None!
```

**Solution**:
```python
machine = MachineFactory()
await db_session.flush()  # Generates IDs
# Now machine.accession_id is populated
```

### Pitfall 3: Mocking Too Much

**Problem**: Mocking everything makes tests meaningless
```python
# Bad: This test doesn't test anything!
mock_service.create_deck = AsyncMock(return_value=deck)
result = await service.create_deck(...)
assert result == deck
```

**Solution**: Only mock external boundaries
```python
# Good: Test real logic, mock only external dependencies
mock_redis.set = AsyncMock()
result = await service.create_deck(...)  # Real service logic runs
mock_redis.set.assert_called_once()
```

### Pitfall 4: Not Testing Error Paths

**Problem**: Only testing happy paths
```python
def test_create_deck():
    result = deck_service.create(valid_data)
    assert result.name == valid_data["name"]
```

**Solution**: Test error scenarios
```python
def test_create_deck_duplicate_name():
    deck_service.create({"name": "test"})

    with pytest.raises(DuplicateNameError):
        deck_service.create({"name": "test"})
```

### Pitfall 5: Shared State Between Tests

**Problem**: Tests pass individually but fail when run together
```python
# BAD: Module-level state
_cached_machine = None

def test_first():
    global _cached_machine
    _cached_machine = MachineFactory()

def test_second():
    # Assumes _cached_machine exists!
    assert _cached_machine is not None
```

**Solution**: Each test is fully independent
```python
def test_first(db_session):
    machine = MachineFactory()
    await db_session.flush()
    # Machine only exists in this test's transaction

def test_second(db_session):
    # Creates its own machine
    machine = MachineFactory()
    await db_session.flush()
```

### Pitfall 6: Not Awaiting Async Functions

**Problem**:
```python
result = service.get_by_id(deck_id)  # Returns coroutine, not result!
```

**Solution**:
```python
result = await service.get_by_id(deck_id)
```

---

## Summary

- **API Tests**: Use real database, test full HTTP cycle, verify both response and persistence
- **Service Tests**: Use real database in transactions, mock external dependencies only
- **Core Tests**: Heavy mocking, focus on unit isolation and logic correctness
- **Integration Tests**: Minimize mocking, test real component interactions
- **Always**: Use factories, follow AAA pattern, ensure test isolation
