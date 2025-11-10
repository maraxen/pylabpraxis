# Service Test Scaffolding Guide

This directory contains test scaffolds for existing service layer classes that need test coverage.

## Scaffolded Service Test Files (Ready for Implementation)

The following service test files have been scaffolded with test function signatures and TODO comments:

### 1. **test_machine_service.py** (~15 tests to implement)
- **Service**: `MachineService` in `praxis/backend/services/machine.py`
- **Key Features to Test**:
  - CRUD operations (create, get, get_multi, update, remove)
  - Duplicate name prevention
  - Status management
  - Resource counterpart linking (machine-resource relationship)
  - PLR state management (JSONB field)
  - Singleton pattern

### 2. **test_resource_service.py** (~15 tests to implement)
- **Service**: `ResourceService` in `praxis/backend/services/resource.py`
- **Key Features to Test**:
  - CRUD operations
  - Duplicate name prevention
  - Resource definition linking
  - Parent-child resource relationships
  - PLR state management (positions, volumes, etc.)
  - Singleton pattern

### 3. **test_deck_service.py** (~16 tests to implement)
- **Service**: `DeckService` in `praxis/backend/services/deck.py`
- **Key Features to Test**:
  - CRUD operations
  - Deck type definition linking
  - Parent machine relationship
  - Child resources on positions
  - 3-level inheritance (Deck → Resource → Asset)
  - PLR state management
  - Singleton pattern

## Reference Implementation

**test_user_service.py** (26 tests) - This is your complete reference implementation showing:
- How to test service CRUD operations
- How to verify database persistence
- How to test validation and error cases
- How to test domain-specific logic (authentication, password hashing)
- Proper use of async/await with database sessions
- Test organization and naming conventions

## Service Layer Testing Pattern

All services inherit from `CRUDBase` and follow these patterns:

### Standard CRUD Methods to Test

1. **create()**
   ```python
   @pytest.mark.asyncio
   async def test_service_create_entity(db_session: AsyncSession) -> None:
       # Create Pydantic *Create model
       create_data = EntityCreate(
           name="test_name",
           fqn="test.fqn",
           # ... other required fields
       )

       # Call service.create()
       entity = await service.create(db_session, obj_in=create_data)

       # Verify
       assert entity.name == "test_name"
       assert entity.accession_id is not None
   ```

2. **get()**
   ```python
   @pytest.mark.asyncio
   async def test_service_get_by_id(db_session: AsyncSession) -> None:
       # Create entity first
       created = await service.create(db_session, obj_in=create_data)

       # Retrieve by ID
       retrieved = await service.get(db_session, created.accession_id)

       # Verify
       assert retrieved is not None
       assert retrieved.accession_id == created.accession_id
   ```

3. **get_by_name()** (if service has this method)
   ```python
   entity = await service.get_by_name(db_session, "entity_name")
   assert entity is not None
   assert entity.name == "entity_name"
   ```

4. **get_multi()** with pagination
   ```python
   # Create multiple entities
   for i in range(5):
       await service.create(db_session, obj_in=create_data)

   # Get with filters
   filters = SearchFilters(skip=0, limit=10)
   entities = await service.get_multi(db_session, filters=filters)

   # Verify
   assert len(entities) >= 5
   ```

5. **update()**
   ```python
   # Create entity
   entity = await service.create(db_session, obj_in=create_data)

   # Update
   update_data = EntityUpdate(name="new_name")
   updated = await service.update(db_session, db_obj=entity, obj_in=update_data)

   # Verify
   assert updated.name == "new_name"
   ```

6. **remove()**
   ```python
   # Create entity
   entity = await service.create(db_session, obj_in=create_data)
   entity_id = entity.accession_id

   # Delete
   deleted = await service.remove(db_session, accession_id=entity_id)

   # Verify deleted
   assert deleted is not None
   retrieved = await service.get(db_session, entity_id)
   assert retrieved is None
   ```

### Testing Relationships

Many services manage entities with relationships:

```python
@pytest.mark.asyncio
async def test_service_with_related_entity(db_session: AsyncSession) -> None:
    # Create parent entity first
    parent = await parent_service.create(db_session, obj_in=parent_data)

    # Create child linked to parent
    child_data = ChildCreate(
        name="child",
        parent_id=parent.accession_id,
    )
    child = await child_service.create(db_session, obj_in=child_data)

    # Verify relationship
    assert child.parent_id == parent.accession_id
    # If relationship is bidirectional:
    await db_session.refresh(parent)
    assert child in parent.children
```

### Testing JSONB Fields (PLR State)

Services like Machine, Resource, and Deck manage PLR state in JSONB fields:

```python
@pytest.mark.asyncio
async def test_service_plr_state_management(db_session: AsyncSession) -> None:
    # Create entity
    entity = await service.create(db_session, obj_in=create_data)

    # Update with PLR state
    plr_state = {
        "position": {"x": 100.0, "y": 200.0, "z": 50.0},
        "resources": ["plate_001", "tip_rack_002"],
        "metadata": {"calibrated": True, "last_check": "2024-11-10"},
    }
    update_data = EntityUpdate(plr_state=plr_state)
    updated = await service.update(db_session, db_obj=entity, obj_in=update_data)

    # Verify JSONB storage
    assert updated.plr_state == plr_state
    assert updated.plr_state["position"]["x"] == 100.0
    assert updated.plr_state["resources"] == ["plate_001", "tip_rack_002"]
```

### Testing Validation and Errors

Test that services properly validate and handle errors:

```python
@pytest.mark.asyncio
async def test_service_create_duplicate_name(db_session: AsyncSession) -> None:
    # Create first entity
    create_data1 = EntityCreate(name="duplicate")
    await service.create(db_session, obj_in=create_data1)

    # Try to create duplicate
    create_data2 = EntityCreate(name="duplicate")  # Same name

    # Should raise error (ValueError or IntegrityError depending on service)
    with pytest.raises((ValueError, IntegrityError)):
        await service.create(db_session, obj_in=create_data2)
```

## Implementation Checklist

For each test file:

1. ✅ **Understand the service**
   - Read the service file in `praxis/backend/services/`
   - Identify which methods it has
   - Note domain-specific logic beyond basic CRUD

2. ✅ **Understand the models**
   - Read the ORM model (what fields are required/optional)
   - Read the Pydantic models (Create, Update schemas)
   - Check for relationships to other models

3. ✅ **Implement tests**
   - Start with create/get/update/remove (basic CRUD)
   - Add tests for domain-specific methods
   - Test relationships if applicable
   - Test validation and error cases
   - Test JSONB fields if applicable

4. ✅ **Run tests**
   ```bash
   # Run all tests for one service
   python -m pytest praxis/backend/services/tests/test_machine_service.py -v

   # Run specific test
   python -m pytest praxis/backend/services/tests/test_machine_service.py::test_machine_service_create_machine -v
   ```

5. ✅ **Verify coverage**
   - Each service should have ~15-20 tests
   - Cover happy paths and error cases
   - Test all public methods
   - Test relationships and JSONB fields

## Key Differences from ORM Tests

Service tests are different from ORM model tests:

| ORM Tests | Service Tests |
|-----------|---------------|
| Test model fields and constraints | Test business logic and workflows |
| Direct ORM instantiation | Use Pydantic Create/Update models |
| Test SQLAlchemy relationships | Test service methods that manage relationships |
| Focus on persistence | Focus on validation, transactions, side effects |
| No decorator handling | Services use `@handle_db_transaction` decorator |

## Common Patterns in Services

### 1. Services check for duplicates
```python
# In service.create()
existing = await db.execute(select(Model).filter(Model.name == obj_in.name))
if existing.scalar_one_or_none():
    raise ValueError("Already exists")
```

### 2. Services manage related entities
```python
# MachineService creates resource counterpart
await _create_or_link_resource_counterpart_for_machine(...)
```

### 3. Services use eager loading
```python
# In service.get()
stmt = select(Model).options(
    selectinload(Model.related_entities)
)
```

### 4. Services flush and refresh
```python
await db.flush()  # Write to DB
await db.refresh(entity)  # Get updated fields (timestamps, computed columns)
```

## Tips for Success

1. **Start simple**: Implement basic CRUD tests first, then add complexity
2. **Follow test_user_service.py**: It has all the patterns you need
3. **Check service implementation**: Some services have custom validation or logic
4. **Test relationships carefully**: Create parent entities first, then children
5. **Use fixtures**: Create reusable fixtures for commonly needed entities
6. **Read error messages**: If a test fails, the error tells you what's wrong

## Questions?

- Check `test_user_service.py` for working examples
- Look at the service file to understand what methods exist
- Review ORM model tests to understand the data model
- Check existing service implementations for patterns

Good luck! 🚀
