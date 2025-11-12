# Fix for FunctionDataOutputFactory

## The Problem

Your factory has this code:
```python
@classmethod
def _build(cls, model_class, *args, **kwargs):
    """Build a FunctionDataOutputOrm instance."""
    accession_id = kwargs.pop("accession_id", None)
    protocol_run = kwargs.pop("protocol_run_id")  # ❌ WRONG NAME
    function_call_log = kwargs.pop("function_call_log_id")  # ❌ WRONG NAME
    instance = model_class(*args, **kwargs)  # ❌ Missing required fields!
```

The ORM expects:
- `protocol_run_accession_id` (not `protocol_run_id`)
- `function_call_log_accession_id` (not `function_call_log_id`)

Both are marked `kw_only=True`, so they MUST be passed as keyword arguments.

---

## The Solution

**Option 1: Use async helpers (RECOMMENDED)**

Don't use Factory Boy for async models. Use async helpers instead:

```python
# tests/factories_schedule.py (already exists)
async def create_function_data_output(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm | None = None,
    function_call_log: FunctionCallLogOrm | None = None,
    **kwargs: Any
) -> FunctionDataOutputOrm:
    """Create a function data output for testing."""
    if protocol_run is None:
        protocol_run = await create_protocol_run(db_session)

    if function_call_log is None:
        function_call_log = await create_function_call_log(
            db_session,
            protocol_run=protocol_run
        )

    if 'accession_id' not in kwargs:
        kwargs['accession_id'] = uuid7()

    output = FunctionDataOutputOrm(
        protocol_run_accession_id=protocol_run.accession_id,
        function_call_log_accession_id=function_call_log.accession_id,
        **kwargs
    )
    db_session.add(output)
    await db_session.flush()
    return output
```

**Usage in tests:**
```python
@pytest.mark.asyncio
async def test_function_data_output_creation(db_session: AsyncSession):
    """Test creating a FunctionDataOutputOrm instance."""
    # Use the async helper
    output = await create_function_data_output(
        db_session,
        data_key="test_output",
        data_value_numeric=42.0
    )

    assert output.accession_id is not None
    assert output.data_key == "test_output"
    assert output.data_value_numeric == 42.0
```

---

**Option 2: Fix the Factory (if you really want to use Factory Boy)**

```python
class FunctionDataOutputFactory(SQLAlchemyModelFactory):
    """Factory for FunctionDataOutputOrm."""

    class Meta:
        model = FunctionDataOutputOrm

    class Params:
        # Transient parameters (won't be passed to __init__)
        protocol_run_obj = factory.SubFactory(ProtocolRunFactory)
        function_call_log_obj = factory.SubFactory(FunctionCallLogFactory)

    # Generate the actual foreign key IDs from the transient objects
    accession_id = factory.LazyFunction(uuid7)
    protocol_run_accession_id = factory.LazyAttribute(
        lambda o: o.protocol_run_obj.accession_id
    )
    function_call_log_accession_id = factory.LazyAttribute(
        lambda o: o.function_call_log_obj.accession_id
    )

    # Other fields with sensible defaults
    data_key = factory.Faker("word")
    data_type = DataOutputTypeEnum.UNKNOWN
    spatial_context = SpatialContextEnum.GLOBAL
```

**Usage:**
```python
def test_with_factory(db_session):
    # Bind factory to session
    FunctionDataOutputFactory._meta.sqlalchemy_session = db_session

    # Build instance
    output = FunctionDataOutputFactory.build()

    # Add to session
    db_session.add(output)
    db_session.flush()
```

---

## Why This Happened

1. **kw_only=True**: These fields MUST be passed as keyword arguments
2. **Wrong field names**: The factory was using `_id` suffix when ORM uses `_accession_id`
3. **Missing fields**: After popping the wrong names, nothing was passed to __init__

---

## Recommended Approach

✅ **Use async helpers** (Option 1)

**Why:**
- Factory Boy is designed for sync ORMs
- Async SQLAlchemy has different session management
- Helpers are simpler and more explicit
- All your passing tests (31/31 schedule tests) use helpers, not factories!

❌ **Don't use Factory Boy for async models**

**Unless:**
- You have a specific need for Factory Boy's features
- You're willing to maintain complex _build()/_create() overrides
- You understand Factory Boy's async limitations

---

## Quick Fix Right Now

Replace your test with:

```python
from tests.factories_schedule import create_function_data_output

@pytest.mark.asyncio
async def test_function_data_output_orm_creation(db_session: AsyncSession):
    """Test creating a FunctionDataOutputOrm instance."""
    output = await create_function_data_output(
        db_session,
        data_key="test_key",
        data_value_numeric=123.45
    )

    assert output.accession_id is not None
    assert output.protocol_run_accession_id is not None
    assert output.function_call_log_accession_id is not None
    assert output.data_key == "test_key"
    assert output.data_value_numeric == 123.45
```

---

## Need Help?

1. Check `tests/factories_schedule.py` - it has `create_function_data_output()` ready to use!
2. Look at your passing schedule tests - they all use async helpers
3. Review `tests/models/test_orm/test_function_data_output_orm.py` - it already uses the ORM directly

**The pattern you've been using successfully (helpers) is the right one!**
