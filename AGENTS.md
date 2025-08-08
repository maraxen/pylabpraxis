# AGENTS.md

This file contains instructions and guidelines for AI agents working on the PyLabPraxis codebase.

## Project Overview

PyLabPraxis is a comprehensive Python-based platform for laboratory automation built on top of PyLabRobot. It provides a FastAPI backend with PostgreSQL/Redis persistence, Celery task management, and a service-oriented architecture for managing laboratory workflows.

## Architecture Guidelines

### Core Principles

- **Separation of Concerns**: API layer, service layer, and data layer are clearly separated
- **Type Safety**: Heavy use of Pydantic models and type hints throughout
- **Async Operations**: Long-running lab operations use Celery for asynchronous execution
- **State Management**: Multi-layered state management with Redis, PostgreSQL, and in-memory objects

### Key Architectural Patterns

1. **Service Layer Pattern**: All business logic is in `praxis/backend/services/`
   - `CRUDBase` for standard CRUD operations
   - `DiscoverableTypeServiceBase` for PyLabRobot type discovery
   - `@handle_db_transaction` decorator for transaction management

2. **Repository Pattern**: Database interactions abstracted through service layer
3. **Factory Pattern**: Used for API router generation (`crud_router_factory`)

## Directory Structure

```
praxis/
├── backend/
│   ├── api/           # FastAPI routers and endpoints
│   ├── core/          # Core business logic (Orchestrator, AssetManager, etc.)
│   ├── models/        # Pydantic and SQLAlchemy ORM models
│   ├── services/      # Service layer for business logic
│   └── utils/         # Utility functions and decorators
├── frontend/          # Frontend code (if applicable)
└── tests/             # Test files mirroring backend structure
```

## Development Guidelines

### Code Quality Standards

- **Ruff**: Address critical issues (F, E, B categories) first
- **Pyright**: Target <40 issues across codebase
- **pytest**: Comprehensive test coverage required
- **Type Hints**: All functions must have proper type annotations

### Database Interactions

- Always use service layer, never direct SQLAlchemy in API/core
- Use `@handle_db_transaction` decorator for write operations
- Handle `IntegrityError` → `ValueError` conversion in services

### State Management

Understanding the multi-layered state system is crucial:

1. **PraxisState (Redis)**: Run-specific JSON-serializable data
2. **In-Memory Objects**: Rich Pydantic models for live state
3. **Database (PostgreSQL)**: Persistent configuration and history
4. **WorkcellRuntime**: Live PyLabRobot object states

### API Development

- Use `crud_router_factory` for standard CRUD endpoints
- Pydantic models for request/response validation
- Proper error handling with appropriate HTTP status codes

## Key Components

### Core Services (`praxis/backend/core/`)

- **Orchestrator**: Central execution coordinator
- **AssetManager**: Physical asset lifecycle management
- **WorkcellRuntime**: Live PyLabRobot object management
- **ProtocolScheduler**: Async execution scheduling
- **AssetLockManager**: Distributed asset locking

### Service Layer (`praxis/backend/services/`)

- Inherits from `CRUDBase` or `DiscoverableTypeServiceBase`
- Uses `@handle_db_transaction` for database operations
- Provides business logic abstraction

### Models (`praxis/backend/models/`)

- **ORM Models**: SQLAlchemy for database schema
- **Pydantic Models**: API validation and in-memory state structure
- **Unified Asset Model**: All assets inherit from base `Asset` model

## Asset Management

Post-2025-06 refactor, all assets use unified model:

- Common fields: `accession_id`, `name`, `fqn`, `asset_type`, `location`, `plr_state`
- Standardized relationships between asset types
- Remove references to legacy fields/classes

## Type Definition Discovery

Critical system for hardware capability awareness:

- `ResourceTypeDefinitionService`: Discovers PyLabRobot resources
- `MachineTypeDefinitionService`: Discovers PyLabRobot machines
- `DeckTypeDefinitionService`: Discovers PyLabRobot decks
- `DiscoveryService`: Orchestrates all type discovery

## Testing Strategy

### Test Requirements

1. Each component file must have corresponding test file
2. Comprehensive coverage of business logic
3. Integration tests for database operations
4. Mock external dependencies (hardware, Redis, etc.)

### Test Structure

```
tests/
├── backend/
│   ├── api/
│   ├── core/
│   ├── services/
│   └── models/
```

## Common Patterns to Follow

### Service Implementation

```python
class ExampleService(CRUDBase[ExampleOrm, ExampleCreate, ExampleUpdate]):
    @handle_db_transaction
    def create_with_validation(self, db: Session, obj_in: ExampleCreate) -> ExampleOrm:
        # Custom validation logic
        return super().create(db, obj_in=obj_in)
```

### API Router

```python
from praxis.backend.utils.crud_router_factory import crud_router_factory

router = crud_router_factory(
    service_class=ExampleService,
    create_schema=ExampleCreate,
    update_schema=ExampleUpdate,
    response_schema=ExampleResponse,
    prefix="/examples"
)
```

### Error Handling

- Service layer raises `ValueError` for business logic errors
- API layer converts to appropriate `HTTPException`
- Use `@handle_db_transaction` for automatic rollback

## Restrictions

### Do Not Edit

- Files in `praxis/backend/commons/` directory
- Legacy/deprecated model classes (post-asset-refactor)

### File Handling

- Wrap paths with spaces in quotes
- Use proper path handling for cross-platform compatibility

## Development Workflow

### Before Making Changes

1. Run `pyright` to check current type issues
2. Run `ruff check` for linting issues
3. Ensure tests pass with `pytest`

### After Making Changes

1. Update/add tests for new functionality
2. Verify type safety with `pyright`
3. Check code style with `ruff`
4. Update documentation if needed

## Integration Points

### PyLabRobot Integration

- All hardware interactions go through `WorkcellRuntime`
- Type definitions discovered via specialized services
- Live object state managed in-memory

### Database Integration

- PostgreSQL for persistent data
- Redis for run-specific state and Celery
- Service layer abstracts all database operations

### Task Management

- Celery for async operations
- Redis as broker and result backend
- Protocol execution runs as Celery tasks

## Troubleshooting Common Issues

### Type Errors

- Ensure all Pydantic models have proper imports
- Check for circular import issues
- Verify generic type parameters in service classes

### Database Issues

- Check transaction handling in service methods
- Verify foreign key relationships in ORM models
- Ensure proper session management

### State Management

- Distinguish between PraxisState (Redis) and in-memory objects
- Verify state persistence points in workflow
- Check asset locking mechanisms

## References

- `README.md`: Comprehensive project documentation
- `GEMINI.md`: Additional agent-specific instructions
- `OVERVIEW.md`: High-level architecture overview
- Component docstrings: Detailed implementation guidance

---

**Last Updated**: August 2025
**Target Python Version**: 3.11+
**Key Dependencies**: FastAPI, SQLAlchemy, Pydantic v2, Celery, Redis, PostgreSQL

---

# NOTES FROM MODEL

As agentic models complete work, they should append notes to this section, formatted as below.

## Previous work summary

## TITLE (DATETIME MMHHDDMMYYYY)

Notes on work that was completed, obstacles, and work remaining.

Once this section exceeds 250 lines, models should summarize the work detailed, remove it, and write the summary under the section titled previous work summary.
