# Protocol Execution Architecture Refactoring

## Overview

The protocol execution system has been refactored to provide better separation of concerns, improved maintainability, and proper integration with async task processing. The new architecture separates discovery, code management, scheduling, and execution into distinct, focused modules.

## Architecture Components

### 1. **ProtocolCodeManager** (`protocol_code_manager.py`)
**Responsibility**: Protocol code preparation and loading for execution.

**Key Features**:
- Git repository management (clone, fetch, checkout specific commits)
- File system source handling
- Module import/reload management
- Protocol function loading and validation
- Temporary sys.path management

**Usage**:
```python
code_manager = ProtocolCodeManager()
func, pydantic_def = await code_manager.prepare_protocol_code(protocol_def_orm)
```

### 2. **ProtocolScheduler** (`scheduler.py`)
**Responsibility**: Resource analysis, reservation, and async execution queueing.

**Key Features**:
- Protocol resource requirement analysis
- Resource reservation and conflict detection
- Celery task queueing integration
- Schedule status tracking
- Resource cleanup on cancellation

**Usage**:
```python
scheduler = ProtocolScheduler(db_session_factory)
success = await scheduler.schedule_protocol_execution(protocol_run_orm, user_params, initial_state)
```

### 3. **Orchestrator** (`orchestrator.py`) - Refactored
**Responsibility**: Core protocol execution orchestration (now much leaner).

**Key Changes**:
- **Removed**: Git operations (moved to ProtocolCodeManager)
- **Removed**: Protocol discovery logic (handled by existing DiscoveryService)
- **Added**: Support for ProtocolCodeManager dependency injection
- **Added**: `execute_existing_protocol_run()` method for Celery integration
- **Focused on**: Asset acquisition, argument preparation, protocol execution, state management

**Usage**:
```python
orchestrator = Orchestrator(db_session_factory, asset_manager, workcell_runtime, protocol_code_manager)

# For immediate execution (creates new run)
result = await orchestrator.execute_protocol(protocol_name, user_params)

# For executing existing run (called by Celery workers)
result = await orchestrator.execute_existing_protocol_run(protocol_run_orm, user_params)
```

### 4. **Celery Tasks** (`celery_tasks.py`) - Enhanced
**Responsibility**: Async protocol execution in worker processes.

**Key Enhancements**:
- Proper integration with Orchestrator's `execute_existing_protocol_run()` method
- Better error handling and status updates
- Support for orchestrator dependency injection
- Fallback mode when orchestrator is not available

### 5. **ProtocolExecutionService** (`protocol_execution_service.py`) - New
**Responsibility**: High-level service tying everything together.

**Key Features**:
- Unified entry point for all protocol execution workflows
- Supports both immediate and scheduled execution
- Status monitoring and run management
- Protocol run cancellation
- Dependency injection for all components

**Usage**:
```python
service = ProtocolExecutionService(db_session_factory, asset_manager, workcell_runtime)

# Immediate execution (bypasses scheduler)
result = await service.execute_protocol_immediately(protocol_name, user_params)

# Scheduled execution (via Celery)
run = await service.schedule_protocol_execution(protocol_name, user_params)

# Status monitoring
status = await service.get_protocol_run_status(protocol_run_id)

# Cancellation
success = await service.cancel_protocol_run(protocol_run_id)
```

### 6. **AssetManager** (`asset_manager.py`)
**Responsibility**: Lifecycle and allocation management of physical laboratory assets.

**Key Features**:
- Machine and resource instance allocation and release
- Deck configuration management
- Live PyLabRobot object instantiation from database definitions
- Asset status tracking and conflict detection
- Integration with WorkcellRuntime for live object management

**Usage**:
```python
asset_manager = AssetManager(db_session, workcell_runtime)

# Acquire assets for protocol execution
live_obj, orm_id, asset_type = await asset_manager.acquire_asset(
    protocol_run_accession_id=run_id,
    asset_requirement=asset_req_model
)

# Release assets after protocol completion
await asset_manager.release_machine(machine_orm_id, MachineStatusEnum.AVAILABLE)
await asset_manager.release_resource(resource_orm_id, ResourceStatusEnum.AVAILABLE_IN_STORAGE)
```

### 7. **AssetLockManager** (`asset_lock_manager.py`)
**Responsibility**: Redis-based distributed asset locking for concurrent protocol scheduling.

**Key Features**:
- Atomic asset reservation operations using Redis locks
- Distributed lock coordination across multiple workers
- Asset conflict resolution and deadlock prevention
- Lock timeout and retry mechanisms
- Protocol run reservation tracking

**Usage**:
```python
lock_manager = AssetLockManager(redis_url="redis://localhost:6379/0")
await lock_manager.initialize()

# Acquire distributed lock for asset
reservation_id = await lock_manager.acquire_asset_lock(
    asset_type="machine",
    asset_name="liquid_handler_1",
    protocol_run_id=run_id,
    timeout_seconds=3600
)

# Release lock when done
await lock_manager.release_asset_lock(reservation_id)
```

### 8. **WorkcellRuntime** (`workcell_runtime.py`)
**Responsibility**: Management of live PyLabRobot objects for active workcell configurations.

**Key Features**:
- Dynamic instantiation of PyLabRobot machines and resources from database definitions
- Live object lifecycle management (initialization, setup, teardown)
- State serialization and recovery for backup/restore operations
- Integration with database models for asset status synchronization
- Support for multiple workcell configurations

**Usage**:
```python
workcell_runtime = WorkcellRuntime(db_session_factory, "main_workcell", "workcell_state.json")

# Initialize machines and resources
await workcell_runtime.initialize_machine(machine_orm)
await workcell_runtime.initialize_resource(resource_orm)

# Get live objects
live_machine = workcell_runtime.get_live_machine(machine_orm.accession_id)
live_resource = workcell_runtime.get_live_resource(resource_orm.accession_id)

# Backup and restore state
state_snapshot = workcell_runtime.get_state_snapshot()
workcell_runtime.apply_state_snapshot(state_snapshot)
```

### 9. **Workcell** (`workcell.py`)
**Responsibility**: In-memory container for live PyLabRobot objects and WorkcellView proxy.

**Key Features**:
- Dynamic container organized by machine and resource categories
- State serialization/deserialization for backups
- WorkcellView proxy for secure protocol access to assets
- Asset filtering based on protocol requirements
- Rolling backup management

**Key Classes**:
- **Workcell**: Main container for live objects
- **WorkcellView**: Secure proxy for protocol access

**Usage**:
```python
# Main workcell container
workcell = Workcell("main_workcell", "state.json", backup_interval=60)

# Secure view for protocols
workcell_view = WorkcellView(
    parent_workcell=workcell,
    protocol_name="my_protocol",
    required_assets=[asset_req_1, asset_req_2]
)

# Protocol can only access its required assets
liquid_handler = workcell_view.liquid_handlers.get("lh_1")
```

### 10. **PraxisRunContext** (`run_context.py`)
**Responsibility**: Context object for protocol run execution tracking and state management.

**Key Features**:
- Run identification and session management
- Call sequence tracking for nested protocol functions
- State object integration
- Function call logging coordination
- Context propagation for nested calls

**Usage**:
```python
# Create run context
run_context = PraxisRunContext(
    run_accession_id=run_id,
    canonical_state=praxis_state,
    current_db_session=db_session,
    current_call_log_db_accession_id=None
)

# Create context for nested call
nested_context = run_context.create_context_for_nested_call(parent_call_log_id)

# Serialize function arguments
serialized_args = serialize_arguments(args, kwargs)
```

### 11. **Protocol Decorators** (`decorators.py`)
**Responsibility**: Decorator infrastructure for protocol function definition and execution.

**Key Features**:
- `@protocol_function` decorator for marking protocol functions
- Automatic parameter and asset requirement analysis
- Function call logging and monitoring
- Run control integration (pause/resume/cancel)
- State management and context passing
- Protocol registry management

**Usage**:
```python
@protocol_function(
    name="my_protocol",
    version="1.0.0",
    description="Example protocol",
    parameters=[
        ParameterMetadataModel(name="volume", type_hint_str="float", optional=False),
    ],
    assets=[
        AssetRequirementModel(name="lh", optional=False),
    ]
)
async def my_protocol(
    volume: float,
    lh: LiquidHandler,
    state: PraxisState,
    __praxis_run_context__: PraxisRunContext,
    __function_db_accession_id__: uuid.UUID,
) -> dict[str, Any]:
    # Protocol implementation
    await lh.aspirate(volume)
    return {"success": True}
```

## Execution Workflows

### Immediate Execution
```
ProtocolExecutionService.execute_protocol_immediately()
  ↓
Orchestrator.execute_protocol()
  ↓
ProtocolCodeManager.prepare_protocol_code()
  ↓
AssetManager.acquire_asset()
  ↓
[Protocol Function Execution]
  ↓
AssetManager.release_assets()
```

### Scheduled Execution
```
ProtocolExecutionService.schedule_protocol_execution()
  ↓
ProtocolScheduler.schedule_protocol_execution()
  ↓ (analyzes resources, reserves them)
ProtocolScheduler._queue_execution_task()
  ↓ (queues Celery task)
execute_protocol_run_task.delay()
  ↓ (async execution in worker)
_execute_protocol_async()
  ↓
Orchestrator.execute_existing_protocol_run()
  ↓
[Same execution flow as immediate]
```

## Component Dependencies and Data Flow

### Core Dependencies
```
ProtocolExecutionService
├── ProtocolScheduler
│   ├── AssetLockManager (Redis)
│   └── Celery Tasks
├── Orchestrator
│   ├── ProtocolCodeManager
│   ├── AssetManager
│   │   ├── WorkcellRuntime
│   │   └── Workcell
│   └── PraxisRunContext
└── Database Session Factory
```

### Data Flow Overview
1. **Protocol Definition**: Stored in database via DiscoveryService
2. **Execution Request**: Comes through ProtocolExecutionService
3. **Scheduling**: ProtocolScheduler analyzes resources and queues execution
4. **Resource Locking**: AssetLockManager coordinates distributed locks
5. **Code Preparation**: ProtocolCodeManager loads protocol code
6. **Asset Acquisition**: AssetManager acquires live objects from WorkcellRuntime
7. **Execution**: Orchestrator coordinates protocol function execution
8. **State Management**: PraxisRunContext tracks execution state
9. **Cleanup**: Assets released, locks freed, status updated

### Inter-Component Communication
- **Synchronous**: Direct method calls for immediate operations
- **Asynchronous**: Celery tasks for background execution
- **Database**: Shared state via SQLAlchemy models
- **Redis**: Distributed coordination via AssetLockManager
- **File System**: Protocol code via ProtocolCodeManager

## Advanced Features

### Resource Conflict Resolution
The system uses a multi-layered approach to handle resource conflicts:

1. **Database-level**: Asset status tracking in ResourceOrm and MachineOrm
2. **Redis-level**: Distributed locks via AssetLockManager for atomic reservations
3. **Scheduler-level**: Resource requirement analysis and pre-execution validation
4. **Runtime-level**: Live object state management in WorkcellRuntime

### Protocol State Management
- **PraxisState**: Protocol-specific state that persists across function calls
- **WorkcellRuntime**: Live object state with backup/restore capabilities
- **Database**: Persistent protocol run status and results
- **Context**: Execution context for nested function calls and logging

### Error Handling and Recovery
- **Protocol-level**: Structured error handling with specific exception types
- **Asset-level**: Automatic asset release on execution failure
- **State-level**: Workcell state rollback to last known good state
- **Scheduling-level**: Resource reservation cleanup on cancellation
- **Task-level**: Celery task retry and failure handling

### Monitoring and Observability
- **Execution Logs**: Comprehensive logging at all levels
- **Status Tracking**: Real-time protocol run status updates
- **Performance Metrics**: Execution timing and resource utilization
- **Health Checks**: System component health monitoring
- **Audit Trail**: Complete execution history and state changes

## Key Benefits

### 1. **Separation of Concerns**
- **Discovery**: Handled by existing DiscoveryService
- **Code Management**: ProtocolCodeManager
- **Scheduling**: ProtocolScheduler
- **Execution**: Orchestrator (now focused)
- **Integration**: ProtocolExecutionService

### 2. **Better Testability**
- Each component has clear responsibilities
- Dependency injection enables easy mocking
- Components can be tested in isolation

### 3. **Improved Maintainability**
- Git operations centralized in ProtocolCodeManager
- Scheduler logic separated from execution logic
- Clear interfaces between components

### 4. **Scalability**
- Proper Celery integration for async execution
- Resource management and conflict detection
- Support for multiple concurrent executions

### 5. **Flexibility**
- Supports both immediate and scheduled execution
- Pluggable components via dependency injection
- Easy to extend with new scheduling strategies

## Migration Notes

### For Existing Code
1. **Direct Orchestrator usage**: Should migrate to ProtocolExecutionService
2. **Custom Git operations**: Should use ProtocolCodeManager
3. **Manual scheduling**: Should use ProtocolScheduler

### For Tests
1. **Orchestrator tests**: May need updates due to simplified interface
2. **New component tests**: Should be added for ProtocolCodeManager and ProtocolScheduler
3. **Integration tests**: Should use ProtocolExecutionService

### For Configuration
1. **Celery setup**: Ensure proper initialization with orchestrator context
2. **Dependency injection**: Update service initialization to provide all components
3. **Database sessions**: Ensure proper session factory propagation

## Example Integration

```python
# Application initialization
async def setup_protocol_execution():
    db_session_factory = create_async_session_factory()
    asset_manager = AssetManager(db_session_factory, workcell_runtime)
    workcell_runtime = WorkcellRuntime()

    # Initialize the high-level service
    execution_service = ProtocolExecutionService(
        db_session_factory=db_session_factory,
        asset_manager=asset_manager,
        workcell_runtime=workcell_runtime,
    )

    # Initialize Celery context with orchestrator
    from praxis.backend.core.celery_tasks import initialize_celery_context
    initialize_celery_context(
        db_session_factory=db_session_factory,
        orchestrator=execution_service.orchestrator
    )

    return execution_service

# Usage in API endpoints
async def execute_protocol_endpoint(protocol_name: str, params: dict):
    execution_service = get_execution_service()

    # For immediate execution
    result = await execution_service.execute_protocol_immediately(protocol_name, params)

    # For scheduled execution
    run = await execution_service.schedule_protocol_execution(protocol_name, params)

    return {"run_id": str(run.accession_id), "status": "scheduled"}
```

This refactored architecture provides a solid foundation for reliable, scalable protocol execution while maintaining clean separation of concerns and enabling easy testing and maintenance.

## Testing Strategy

### Unit Testing
Each core component should have comprehensive unit tests covering:

**ProtocolCodeManager**:
- Git operations (clone, fetch, checkout)
- Module import/reload functionality
- Error handling for invalid repositories/commits
- Temporary sys.path management

**ProtocolScheduler**:
- Resource requirement analysis
- Resource reservation logic
- Celery task queueing
- Schedule status tracking

**AssetManager**:
- Asset acquisition and release
- Conflict detection and resolution
- Integration with WorkcellRuntime
- Error handling for unavailable assets

**WorkcellRuntime**:
- PyLabRobot object instantiation
- State serialization/deserialization
- Live object lifecycle management
- Error recovery mechanisms

### Integration Testing
Test component interactions and data flow:

**Scheduler + AssetLockManager**:
- Distributed resource locking
- Concurrent protocol scheduling
- Deadlock detection and resolution
- Lock timeout handling

**Orchestrator + AssetManager + WorkcellRuntime**:
- End-to-end protocol execution
- Asset lifecycle in protocol context
- State management and rollback
- Error propagation and cleanup

**Celery + Orchestrator Integration**:
- Async task execution
- Error handling in worker processes
- Status synchronization
- Task cancellation and cleanup

### Performance Testing
Validate system performance under load:

**Concurrent Execution**:
- Multiple simultaneous protocol runs
- Resource contention handling
- System resource utilization
- Celery worker scaling

**Long-running Protocols**:
- Memory usage over time
- State backup/restore performance
- Asset lock timeout handling
- Database connection management

## Deployment Considerations

### Infrastructure Requirements
**Database**:
- PostgreSQL (recommended) or compatible SQLAlchemy-supported database
- Connection pooling for concurrent access
- Regular backups for protocol run history

**Redis**:
- Redis server for Celery broker and AssetLockManager
- Persistence configuration for lock recovery
- High availability setup for production

**Celery Workers**:
- Dedicated worker processes for protocol execution
- Proper resource limits and monitoring
- Auto-scaling based on queue depth
- Health check endpoints

### Configuration Management
**Environment Variables**:
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Asset Lock Manager
ASSET_LOCK_TIMEOUT_SECONDS=3600
ASSET_LOCK_RETRY_DELAY_MS=100

# Protocol Code Manager
PROTOCOL_GIT_TIMEOUT_SECONDS=300
PROTOCOL_MODULE_RELOAD_ENABLED=true
```

**Service Initialization**:
```python
# Production setup
async def setup_production_services():
    # Database setup with connection pooling
    db_session_factory = create_async_session_factory(
        database_url=os.getenv("DATABASE_URL"),
        pool_size=20,
        max_overflow=30
    )

    # Redis-based asset lock manager
    asset_lock_manager = AssetLockManager(
        redis_url=os.getenv("REDIS_URL"),
        lock_timeout_seconds=int(os.getenv("ASSET_LOCK_TIMEOUT_SECONDS", "3600"))
    )
    await asset_lock_manager.initialize()

    # WorkcellRuntime with persistent state
    workcell_runtime = WorkcellRuntime(
        db_session_factory=db_session_factory,
        workcell_name="production_workcell",
        workcell_save_file="/data/workcell_state.json"
    )

    # AssetManager with lock manager integration
    asset_manager = AssetManager(
        db_session_factory=db_session_factory,
        workcell_runtime=workcell_runtime,
        asset_lock_manager=asset_lock_manager
    )

    # Scheduler with Redis coordination
    scheduler = ProtocolScheduler(
        db_session_factory=db_session_factory,
        redis_url=os.getenv("REDIS_URL"),
        asset_lock_manager=asset_lock_manager
    )

    # Complete execution service
    execution_service = ProtocolExecutionService(
        db_session_factory=db_session_factory,
        asset_manager=asset_manager,
        workcell_runtime=workcell_runtime,
        scheduler=scheduler
    )

    # Initialize Celery context
    initialize_celery_context(
        db_session_factory=db_session_factory,
        orchestrator=execution_service.orchestrator
    )

    return execution_service
```

### Monitoring and Alerting
**Metrics to Track**:
- Protocol execution success/failure rates
- Average execution times by protocol type
- Resource utilization and conflicts
- Celery queue depths and worker health
- Database connection pool usage
- Redis memory usage and lock counts

**Log Aggregation**:
- Centralized logging for all components
- Structured logs with correlation IDs
- Error tracking and alerting
- Performance metrics collection

## Troubleshooting Guide

### Common Issues and Solutions

**Protocol Execution Failures**:
```
Issue: Protocol fails with AssetAcquisitionError
Diagnosis: Check asset availability and lock status
Solution:
1. Verify asset is not in use by another protocol
2. Check AssetLockManager for stale locks
3. Restart asset lock manager if needed
4. Review asset status in database
```

**Celery Task Issues**:
```
Issue: Tasks queued but not executing
Diagnosis: Check Celery worker status and connectivity
Solution:
1. Verify Redis broker connectivity
2. Check worker process health
3. Review task routing configuration
4. Restart Celery workers if needed
```

**Resource Conflicts**:
```
Issue: Multiple protocols competing for same resource
Diagnosis: Examine resource reservation logs
Solution:
1. Check AssetLockManager reservation status
2. Review protocol resource requirements
3. Implement resource pooling if appropriate
4. Adjust scheduling priorities
```

**State Management Issues**:
```
Issue: Protocol state not persisting correctly
Diagnosis: Check PraxisState and WorkcellRuntime logs
Solution:
1. Verify database connectivity
2. Check state serialization/deserialization
3. Review backup file permissions
4. Validate state schema consistency
```

### Debug Commands
```bash
# Check Celery worker status
celery -A praxis.backend.core.celery_tasks inspect active

# View Redis asset locks
redis-cli --scan --pattern "praxis:asset_lock:*"

# Check database protocol run status
psql -c "SELECT accession_id, status, created_at FROM protocol_runs ORDER BY created_at DESC LIMIT 10;"

# View workcell runtime state
cat /data/workcell_state.json | jq .

# Monitor system resources
htop
iotop
```

### Recovery Procedures
**Asset Lock Recovery**:
1. Identify stale locks in Redis
2. Verify corresponding protocol run status
3. Force release locks for failed/cancelled runs
4. Update database asset status if needed

**State Recovery**:
1. Stop all protocol execution
2. Restore workcell state from backup
3. Reconcile database asset status
4. Resume normal operations

**Database Recovery**:
1. Check protocol run consistency
2. Update stale running status to failed
3. Release associated asset reservations
4. Clear orphaned call logs

This comprehensive architecture documentation provides the foundation for understanding, deploying, and maintaining the refactored protocol execution system.
### Standardized API Filtering

To ensure consistency and ease of use, PyLabPraxis employs a standardized filtering mechanism for all `GET` list endpoints (e.g., `/machines/`, `/resources/`, `/protocols/runs/`). This approach combines generic, reusable filters with entity-specific ones.

1.  **Generic Filters (`SearchFilters`)**:
    -   A common Pydantic model, `praxis.backend.models.filters.SearchFilters`, defines standard filtering parameters that apply across most entities. These include:
        -   `limit`: For pagination.
        -   `offset`: For pagination.
        -   `date_range_start` / `date_range_end`: For filtering by creation/update timestamps.
        -   `property_filters`: For key-value filtering on JSON fields.
        -   Common relationship IDs like `protocol_run_accession_id`, `machine_accession_id`, `resource_accession_id`, and `parent_accession_id`.
    -   In API endpoints, these are automatically populated from query parameters using FastAPI's dependency injection: `filters: SearchFilters = Depends()`.

2.  **Entity-Specific Filters**:
    -   Filters that are unique to a specific entity (e.g., `status` for machines, `data_types` for data outputs) are defined as separate `Query()` parameters in the API endpoint signature.
    -   This keeps the `SearchFilters` model clean and generic while providing clear, self-documenting parameters for specific filtering needs.

3.  **Service and Query Builder Integration**:
    -   The API endpoint passes both the generic `filters` object and any specific filter arguments to the corresponding service layer method.
    -   The service method then uses helper functions from `praxis.backend.services.utils.query_builder` (like `apply_pagination`, `apply_date_range_filters`) to build the SQLAlchemy query from the `SearchFilters` object.
    -   Specific filters are applied directly within the service method, creating a clean separation between generic and specific query logic.
