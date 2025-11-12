# Test Scaffolding Guide for Jules

This directory contains test scaffolding for ORM models that need implementation.

## Scaffolded Test Files (Ready for Implementation)

The following test files have been scaffolded with fixtures, test function signatures, and TODO comments:

### 1. **test_schedule_entry_orm.py** (~13 tests to implement)
- **Model**: `ScheduleEntryOrm` - Tracks scheduled protocol runs
- **Key Features to Test**:
  - Status transitions (QUEUED, ANALYZING_ASSETS, WAITING_FOR_ASSETS, READY, RUNNING, etc.)
  - Priority-based ordering
  - Timestamp tracking (scheduled_at, asset_analysis_completed_at, assets_reserved_at, etc.)
  - JSONB fields (asset_requirements_json, user_params_json, initial_state_json)
  - Celery integration (celery_task_id, celery_queue_name)
  - Retry logic (retry_count, max_retries, last_error_message)
  - Relationship to ProtocolRunOrm

### 2. **test_asset_reservation_orm.py** (~14 tests to implement)
- **Model**: `AssetReservationOrm` - Tracks asset reservations for protocol runs
- **Key Features to Test**:
  - Status transitions (PENDING, RESERVED, ACTIVE, RELEASED, EXPIRED, FAILED)
  - Redis lock fields (redis_lock_key, redis_lock_value, lock_timeout_seconds)
  - Asset type tracking (AssetType enum)
  - Timing fields (reserved_at, released_at)
  - Relationships to ProtocolRunOrm, ScheduleEntryOrm, AssetOrm
  - Queries by status, asset, and active reservations

### 3. **test_function_data_output_orm.py** (~20 tests to implement)
- **Model**: `FunctionDataOutputOrm` - Captures data outputs from protocol function calls
- **Key Features to Test**:
  - Data type enum (MEASUREMENT, IMAGE, FILE, METADATA, LOG, etc.)
  - Spatial context enum (GLOBAL, WELL, PLATE, DECK, POSITION, etc.)
  - Multiple data value fields:
    - `data_value_numeric` - For measurements
    - `data_value_json` - For structured data (JSONB)
    - `data_value_text` - For text data
    - `data_value_binary` - For binary data (images, etc.)
  - JSONB fields (spatial_coordinates_json, metadata_json)
  - File path references
  - Relationships to ProtocolRunOrm, FunctionCallLogOrm, ResourceOrm, MachineOrm, DeckOrm
  - Queries by data type, protocol run, resource, machine

## How to Implement Tests

### Pattern to Follow

Each test file already has:
1. ✅ Proper imports
2. ✅ Fixtures for parent models (with relationship-based FK assignment)
3. ✅ Test function signatures with descriptive docstrings
4. ✅ TODO comments explaining what to verify

### Implementation Steps

For each test function:

1. **Remove `pass` statement**
2. **Follow the TODO comment** - It tells you exactly what to test
3. **Use the established patterns** from completed test files:
   ```python
   # Example pattern from completed tests:
   from praxis.backend.utils.uuid import uuid7

   # Create instance
   instance_id = uuid7()
   instance = ModelOrm(
       accession_id=instance_id,
       required_field=value,
       # ... other fields
   )

   # Set relationships (CRITICAL for FK persistence)
   instance.parent_relationship = parent_fixture

   # Add and flush
   db_session.add(instance)
   await db_session.flush()

   # Verify fields
   assert instance.field_name == expected_value
   ```

4. **For JSONB fields**, test complex nested structures:
   ```python
   jsonb_data = {
       "key": "value",
       "nested": {"count": 42, "items": [1, 2, 3]},
   }
   instance.jsonb_field = jsonb_data
   await db_session.flush()

   # Verify nested access
   assert instance.jsonb_field["nested"]["count"] == 42
   ```

5. **For relationship tests**, verify bidirectional navigation:
   ```python
   # Forward: child to parent
   assert child.parent_id == parent.id
   assert child.parent == parent

   # Backward: parent to children
   assert len(parent.children) >= 1
   assert child in parent.children
   ```

6. **For query tests**, create multiple instances and filter:
   ```python
   result = await db_session.execute(
       select(ModelOrm).where(ModelOrm.status == StatusEnum.ACTIVE)
   )
   instances = result.scalars().all()
   assert len(instances) >= expected_count
   ```

### Reference Examples

Look at these completed test files for patterns:

- **Simple model**: `test_user_orm.py`
- **Model with JSONB**: `test_parameter_definition_orm.py` (constraints_json, ui_hint_json)
- **Model with enums**: `test_protocol_run_orm.py` (status transitions)
- **Model with relationships**: `test_function_call_log_orm.py` (nested parent-child)
- **Model with timing**: `test_function_call_log_orm.py` (start_time, end_time)

### Testing Checklist

For each test file, ensure you test:
- ✅ Creation with minimal fields (defaults)
- ✅ Creation with all fields
- ✅ Persistence cycle (create, flush, query back)
- ✅ Enum values (if applicable)
- ✅ JSONB fields (if applicable)
- ✅ Relationships to parent models
- ✅ Query patterns (by status, by parent, etc.)
- ✅ String representation (__repr__)

## Running Tests

### Run all tests for a file:
```bash
python -m pytest tests/models/test_orm/test_schedule_entry_orm.py -v
```

### Run specific test:
```bash
python -m pytest tests/models/test_orm/test_schedule_entry_orm.py::test_schedule_entry_orm_creation_minimal -v
```

### Run without database (will skip DB tests):
```bash
python -m pytest tests/models/test_orm/test_schedule_entry_orm.py -k "not database" -v
```

## Notes

- **Database connection**: Some tests require PostgreSQL. If DB is not available, focus on non-DB tests first.
- **Relationship-based FK assignment**: ALWAYS set both the FK field AND the relationship object for SQLAlchemy MappedAsDataclass models.
- **Fixtures**: All necessary fixtures are already created in each file. They handle parent model creation correctly.
- **Enum serialization**: In Pydantic tests, enums serialize to their string values (e.g., `"ACTIVE"` not `StatusEnum.ACTIVE`).

## Questions?

- Check existing completed test files for patterns
- Look for similar field types in other tests
- All scaffolded tests have detailed TODO comments explaining what to verify

Good luck! 🚀
