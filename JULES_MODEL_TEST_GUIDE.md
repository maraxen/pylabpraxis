# Model Testing Guide: Addressing Schema Mismatches

## Jules - Response to Your Feedback

I've reviewed the actual ORM models and identified several schema issues that explain why you're spending so much time debugging. Here's a comprehensive guide to help you complete the remaining tests efficiently.

## Key Schema Issues Identified

### 1. **AssetReservationOrm - Critical Issue** ⚠️
**Problem**: Line 201 in `praxis/backend/models/orm/schedule.py`:
```python
protocol_run_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("protocol_runs.accession_id"),
    nullable=False,
    unique=True,  # ⚠️ THIS IS WRONG - prevents multiple reservations per run!
    index=True,
    ...
)
```

**Impact**: This `unique=True` constraint means each protocol run can only have ONE asset reservation, which doesn't make sense for a reservation system. A protocol run should be able to reserve multiple assets (multiple plates, machines, etc.).

**Workaround for Tests**:
- Only create ONE AssetReservationOrm per ProtocolRunOrm in your tests
- Or use different ProtocolRunOrm instances for each reservation
- Document this limitation in test comments

**Long-term Fix**: This should be changed to `unique=False` in the schema.

### 2. **Field Attribute Patterns - Common Issues**

#### `kw_only=True` Fields
Many fields use `kw_only=True`, which means they **must** be passed as keyword arguments:

```python
# ❌ This will fail:
reservation = AssetReservationOrm(
    uuid7(),  # positional arg for protocol_run_accession_id
    uuid7(),  # positional arg for schedule_entry_accession_id
)

# ✅ This works:
reservation = AssetReservationOrm(
    protocol_run_accession_id=uuid7(),  # keyword arg required!
    schedule_entry_accession_id=uuid7(),
    asset_name="test_asset",
    redis_lock_key="lock:test",
)
```

#### `init=False` Relationships
Relationships with `init=False` cannot be set in the constructor:

```python
# ❌ This will fail:
reservation = AssetReservationOrm(
    protocol_run=my_protocol_run,  # init=False, can't pass here
    ...
)

# ✅ This works:
reservation = AssetReservationOrm(
    protocol_run_accession_id=my_protocol_run.accession_id,
    ...
)
reservation.protocol_run = my_protocol_run  # Set after creation
db_session.add(reservation)
await db_session.flush()
```

#### `server_default` vs `default`
Fields with `server_default` get their value from the database:

```python
# scheduled_at has server_default=func.now()
entry = ScheduleEntryOrm(
    protocol_run_accession_id=run_id,
)
db_session.add(entry)
await db_session.flush()  # Database sets scheduled_at here
await db_session.refresh(entry)  # Load it into Python object
assert entry.scheduled_at is not None  # Now it's populated
```

## Model-Specific Test Patterns

### ScheduleEntryOrm

```python
@pytest.mark.asyncio
async def test_schedule_entry_orm_creation_minimal(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm,
) -> None:
    """Test creating ScheduleEntryOrm with minimal fields."""
    from praxis.backend.utils.uuid import uuid7

    entry = ScheduleEntryOrm(
        protocol_run_accession_id=protocol_run.accession_id,
        # status defaults to QUEUED
        # priority defaults to 1
        # scheduled_at set by server_default
    )
    entry.protocol_run = protocol_run  # Set relationship

    db_session.add(entry)
    await db_session.flush()
    await db_session.refresh(entry)

    # Verify defaults
    assert entry.status == ScheduleStatusEnum.QUEUED
    assert entry.priority == 1
    assert entry.scheduled_at is not None  # Set by database
    assert entry.required_asset_count == 0
    assert entry.retry_count == 0
    assert entry.max_retries == 3
```

### AssetReservationOrm

```python
@pytest.mark.asyncio
async def test_asset_reservation_orm_creation_minimal(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm,
    schedule_entry: ScheduleEntryOrm,
    machine_asset: MachineOrm,
) -> None:
    """Test creating AssetReservationOrm with minimal fields.

    NOTE: Due to unique constraint on protocol_run_accession_id,
    each protocol run can only have ONE reservation. This appears
    to be a schema bug - typically runs would reserve multiple assets.
    """
    from praxis.backend.utils.uuid import uuid7

    reservation = AssetReservationOrm(
        # All kw_only fields must be keyword args:
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine_asset.accession_id,
        asset_name=machine_asset.name,
        redis_lock_key=f"lock:asset:{machine_asset.accession_id}",
        # Optional fields with defaults:
        # asset_type defaults to AssetType.ASSET
        # status defaults to PENDING
        # lock_timeout_seconds defaults to 3600
    )

    # Set relationships AFTER creation (they have init=False):
    reservation.protocol_run = protocol_run
    reservation.schedule_entry = schedule_entry
    reservation.asset = machine_asset

    db_session.add(reservation)
    await db_session.flush()
    await db_session.refresh(reservation)

    # Verify defaults
    assert reservation.status == AssetReservationStatusEnum.PENDING
    assert reservation.asset_type == AssetType.ASSET
    assert reservation.lock_timeout_seconds == 3600
    assert reservation.reserved_at is not None  # Set by server_default
    assert reservation.redis_lock_value is None
```

### FunctionDataOutputOrm

```python
@pytest.mark.asyncio
async def test_function_data_output_orm_creation_minimal(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm,
    function_call_log: FunctionCallLogOrm,
) -> None:
    """Test creating FunctionDataOutputOrm with minimal fields."""
    from praxis.backend.utils.uuid import uuid7

    output = FunctionDataOutputOrm(
        # Required kw_only fields:
        protocol_run_accession_id=protocol_run.accession_id,
        function_call_log_accession_id=function_call_log.accession_id,
        # Fields with defaults:
        # data_type defaults to DataOutputTypeEnum.UNKNOWN
        # data_key defaults to ""
        # spatial_context defaults to SpatialContextEnum.GLOBAL
        # measurement_timestamp defaults to func.now()
    )

    # Set relationships:
    output.protocol_run = protocol_run
    output.function_call_log = function_call_log

    db_session.add(output)
    await db_session.flush()
    await db_session.refresh(output)

    # Verify defaults
    assert output.data_type == DataOutputTypeEnum.UNKNOWN
    assert output.data_key == ""
    assert output.spatial_context == SpatialContextEnum.GLOBAL
    assert output.measurement_timestamp is not None
    # All optional FKs should be None:
    assert output.resource_accession_id is None
    assert output.machine_accession_id is None
    assert output.deck_accession_id is None
```

## Better Testing Approach Going Forward

### 1. **Generate Test Stubs from Actual Schema**

Instead of manually creating test scaffolds, we could create a script that:
- Reads the ORM model definitions
- Extracts field information (required, defaults, kw_only, etc.)
- Generates accurate test stubs

**Example Script** (pseudocode):
```python
def generate_test_stubs(model_class):
    """Generate test stubs based on actual model definition."""
    fields = inspect_model_fields(model_class)

    # Identify required fields
    required_kw = [f for f in fields if f.kw_only and not f.has_default]
    required_pos = [f for f in fields if not f.kw_only and not f.has_default]

    # Generate minimal test case
    return f"""
@pytest.mark.asyncio
async def test_{model_name}_creation_minimal(db_session, ...fixtures):
    obj = {model_class.__name__}(
        {generate_required_args(required_kw)}
    )
    ...
"""
```

### 2. **Use Factories for Complex Models**

For models with many dependencies, create factory functions:

```python
# tests/factories.py
async def create_asset_reservation(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm | None = None,
    schedule_entry: ScheduleEntryOrm | None = None,
    asset: MachineOrm | None = None,
    **kwargs
) -> AssetReservationOrm:
    """Factory for creating AssetReservationOrm with sensible defaults."""
    from praxis.backend.utils.uuid import uuid7

    # Create dependencies if not provided
    if not protocol_run:
        protocol_run = await create_protocol_run(db_session)
    if not schedule_entry:
        schedule_entry = await create_schedule_entry(db_session, protocol_run)
    if not asset:
        asset = await create_machine(db_session)

    reservation = AssetReservationOrm(
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=asset.accession_id,
        asset_name=asset.name,
        redis_lock_key=kwargs.get('redis_lock_key', f"lock:{uuid7()}"),
        **kwargs
    )

    reservation.protocol_run = protocol_run
    reservation.schedule_entry = schedule_entry
    reservation.asset = asset

    db_session.add(reservation)
    await db_session.flush()
    await db_session.refresh(reservation)

    return reservation
```

### 3. **Schema Validation Tests**

Add tests that validate the schema matches expectations:

```python
@pytest.mark.asyncio
async def test_asset_reservation_allows_multiple_per_run(db_session):
    """Verify multiple reservations can be created for same protocol run.

    CURRENTLY FAILS due to unique constraint - this test documents the issue.
    """
    protocol_run = await create_protocol_run(db_session)
    schedule_entry = await create_schedule_entry(db_session, protocol_run)

    asset1 = await create_machine(db_session, name="machine1")
    asset2 = await create_machine(db_session, name="machine2")

    # Should be able to reserve multiple assets for same run
    reservation1 = await create_asset_reservation(
        db_session, protocol_run, schedule_entry, asset1
    )

    # This currently fails due to unique constraint:
    with pytest.raises(IntegrityError):
        reservation2 = await create_asset_reservation(
            db_session, protocol_run, schedule_entry, asset2
        )
```

## Immediate Actions for Jules

### For test_function_data_output_orm.py:

1. **Check the conftest changes you made** - share them with me so I can verify they're correct
2. **Use this pattern for creating outputs**:

```python
@pytest.fixture
async def function_call_log(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> FunctionCallLogOrm:
    """Create a FunctionCallLogOrm for testing."""
    from praxis.backend.utils.uuid import uuid7
    from datetime import datetime, timezone

    call_log = FunctionCallLogOrm(
        accession_id=uuid7(),
        protocol_run_accession_id=protocol_run.accession_id,
        function_protocol_definition_accession_id=protocol_definition.accession_id,
        sequence_in_run=0,
        start_time=datetime.now(timezone.utc),
    )
    # Set relationships:
    call_log.protocol_run = protocol_run
    call_log.executed_function_definition = protocol_definition

    db_session.add(call_log)
    await db_session.flush()
    await db_session.refresh(call_log)

    return call_log
```

3. **For FunctionDataOutputOrm tests**, remember:
   - All optional FK fields (resource, machine, deck) default to None
   - Use `kw_only=True` for protocol_run_accession_id and function_call_log_accession_id
   - measurement_timestamp is set automatically
   - Set relationships AFTER creation

4. **Common FunctionDataOutputOrm patterns**:

```python
# Minimal numeric measurement:
output = FunctionDataOutputOrm(
    protocol_run_accession_id=protocol_run.accession_id,
    function_call_log_accession_id=function_call_log.accession_id,
    data_type=DataOutputTypeEnum.MEASUREMENT,
    data_key="absorbance_580nm",
    data_value_numeric=0.456,
)

# With spatial context (well-specific):
output = FunctionDataOutputOrm(
    protocol_run_accession_id=protocol_run.accession_id,
    function_call_log_accession_id=function_call_log.accession_id,
    data_type=DataOutputTypeEnum.MEASUREMENT,
    spatial_context=SpatialContextEnum.WELL,
    resource_accession_id=plate_resource.accession_id,
    spatial_coordinates_json={"well": "A1", "row": 0, "col": 0},
    data_value_numeric=0.456,
)

# With JSONB data:
output = FunctionDataOutputOrm(
    protocol_run_accession_id=protocol_run.accession_id,
    function_call_log_accession_id=function_call_log.accession_id,
    data_type=DataOutputTypeEnum.METADATA,
    data_value_json={
        "wavelength_nm": 580,
        "temperature_c": 37,
        "readings": [0.1, 0.2, 0.3],
    },
)
```

## Questions to Ask

Before spending more time debugging, please share:

1. **What specific errors are you seeing in test_function_data_output_orm.py?**
   - Copy/paste the actual error messages
   - Which specific tests are failing?

2. **What changes did you make to tests/conftest.py?**
   - Share the diff so I can verify they're correct

3. **For the tests you got passing (ScheduleEntry, AssetReservation)**:
   - Did you encounter the unique constraint issue on AssetReservationOrm?
   - What workarounds did you use?

## Summary

The main issues are:
1. **Schema bugs** (AssetReservationOrm unique constraint)
2. **Field attributes** (kw_only, init=False, server_default)
3. **Relationship patterns** (must be set after creation)

**Recommendation**:
- Finish FunctionDataOutput tests using the patterns above
- Document any schema issues you find
- Consider creating a factory pattern for complex models
- We can create a schema validation test suite to catch these issues earlier

Let me know the specific errors you're seeing and I'll provide targeted fixes!
