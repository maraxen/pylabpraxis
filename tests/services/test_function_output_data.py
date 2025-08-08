import datetime
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import all required ORM and Pydantic models from the top-level package
from praxis.backend.models import (
  DataOutputTypeEnum,
  DeckOrm,
  FunctionCallLogOrm,
  FunctionDataOutputCreate,
  FunctionDataOutputOrm,
  FunctionDataOutputUpdate,
  MachineOrm,
  ProtocolRunOrm,
  ResourceOrm,
  SearchFilters,
  SpatialContextEnum,
)

# Import the service functions being tested
from praxis.backend.services.function_output_data import (
  create_function_data_output,
  delete_function_data_output,
  list_function_data_outputs,
  read_function_data_output,
  update_function_data_output,
)

# --- Pytest Fixtures ---


@pytest.fixture
async def setup_dependencies(db: AsyncSession):
  """Fixture to create and commit all necessary dependency ORM objects."""
  protocol_run = ProtocolRunOrm(name="Test Run")
  db.add(protocol_run)
  await db.commit()
  await db.refresh(protocol_run)

  function_call_log = FunctionCallLogOrm(
    protocol_run_accession_id=protocol_run.accession_id,
    function_name="test_function",
  )
  machine = MachineOrm(name="Test Machine", fqn="machine.fqn")
  resource = ResourceOrm(
    name="Test Resource",
    resource_definition_name="test_resource_def",
  )
  deck = DeckOrm(
    name="Test Deck",
    deck_accession_id=uuid.uuid4(),
    fqn="deck.fqn",
  )

  db.add_all([function_call_log, machine, resource, deck])
  await db.commit()

  for obj in [function_call_log, machine, resource, deck]:
    await db.refresh(obj)

  return {
    "protocol_run_id": protocol_run.accession_id,
    "function_call_log_id": function_call_log.accession_id,
    "machine_id": machine.accession_id,
    "resource_id": resource.accession_id,
    "deck_id": deck.accession_id,
  }


@pytest.fixture
def base_data_output_create(setup_dependencies) -> FunctionDataOutputCreate:
  """Fixture to get a valid FunctionDataOutputCreate model."""
  return FunctionDataOutputCreate(
    function_call_log_accession_id=setup_dependencies["function_call_log_id"],
    protocol_run_accession_id=setup_dependencies["protocol_run_id"],
    data_type=DataOutputTypeEnum.GENERIC_MEASUREMENT,
    data_key="test_measurement",
    spatial_context=SpatialContextEnum.MACHINE_LEVEL,
    machine_accession_id=setup_dependencies["machine_id"],
    data_value_numeric=123.45,
    data_units="units",
    resource_accession_id=None,
    deck_accession_id=None,
    spatial_coordinates_json=None,
    data_value_json=None,
    data_value_text=None,
    file_path=None,
    file_size_bytes=None,
    data_quality_score=None,
    measurement_conditions_json=None,
    measurement_timestamp=None,
    sequence_in_function=None,
    derived_from_data_output_accession_id=None,
    processing_metadata_json=None,
  )


@pytest.fixture
async def existing_data_output(
  db: AsyncSession,
  base_data_output_create: FunctionDataOutputCreate,
) -> FunctionDataOutputOrm:
  """Fixture to create a data output record in the DB for read/update/delete tests."""
  return await create_function_data_output(db, base_data_output_create)


pytestmark = pytest.mark.asyncio


class TestFunctionDataOutputService:

  """Test suite for the Function Data Output service layer."""

  async def test_create_function_data_output(
    self,
    db: AsyncSession,
    base_data_output_create: FunctionDataOutputCreate,
  ) -> None:
    """Test successful creation of a function data output."""
    created_output = await create_function_data_output(db, base_data_output_create)
    assert created_output is not None
    assert created_output.accession_id is not None
    assert created_output.data_key == "test_measurement"
    assert created_output.data_value_numeric == 123.45
    assert created_output.protocol_run_accession_id == base_data_output_create.protocol_run_accession_id

  async def test_read_function_data_output(
    self,
    db: AsyncSession,
    existing_data_output: FunctionDataOutputOrm,
  ) -> None:
    """Test reading a function data output by its ID."""
    read_output = await read_function_data_output(db, existing_data_output.accession_id)
    assert read_output is not None
    assert read_output.accession_id == existing_data_output.accession_id
    assert read_output.data_key == existing_data_output.data_key
    assert read_output.protocol_run is not None

  async def test_read_non_existent_output(self, db: AsyncSession) -> None:
    """Test that reading a non-existent output returns None."""
    non_existent_id = uuid.uuid4()
    assert await read_function_data_output(db, non_existent_id) is None

  async def test_update_function_data_output(
    self,
    db: AsyncSession,
    existing_data_output: FunctionDataOutputOrm,
  ) -> None:
    """Test updating a function data output record."""
    update_model = FunctionDataOutputUpdate(
      data_quality_score=0.95,
      processing_metadata_json={"filter": "applied"},
      measurement_conditions_json=None,
    )
    updated_output = await update_function_data_output(
      db,
      existing_data_output.accession_id,
      update_model,
    )

    assert updated_output is not None
    assert updated_output.data_quality_score == 0.95
    assert updated_output.processing_metadata_json == {"filter": "applied"}
    assert updated_output.data_key == existing_data_output.data_key

  async def test_delete_function_data_output(
    self,
    db: AsyncSession,
    existing_data_output: FunctionDataOutputOrm,
  ) -> None:
    """Test deleting a function data output record."""
    output_id = existing_data_output.accession_id

    result = await delete_function_data_output(db, output_id)
    assert result is True

    assert await read_function_data_output(db, output_id) is None

  async def test_delete_non_existent_output(self, db: AsyncSession) -> None:
    """Test that deleting a non-existent output returns False."""
    non_existent_id = uuid.uuid4()
    result = await delete_function_data_output(db, non_existent_id)
    assert result is False

  async def test_list_function_data_outputs_with_filters(
    self,
    db: AsyncSession,
    setup_dependencies,
  ) -> None:
    """Test the extensive filtering capabilities of the list function."""
    common_args = {
      "function_call_log_accession_id": setup_dependencies["function_call_log_id"],
      "protocol_run_accession_id": setup_dependencies["protocol_run_id"],
      "machine_accession_id": None,
      "resource_accession_id": None,
      "deck_accession_id": None,
      "spatial_coordinates_json": None,
      "data_value_json": None,
      "data_value_text": None,
      "file_path": None,
      "file_size_bytes": None,
      "data_units": None,
      "measurement_timestamp": None,
      "sequence_in_function": None,
      "derived_from_data_output_accession_id": None,
      "processing_metadata_json": None,
      "measurement_conditions_json": None,
    }

    # Entry 1: Numeric, high quality
    await create_function_data_output(
      db,
      FunctionDataOutputCreate(
        **common_args,
        data_type=DataOutputTypeEnum.ABSORBANCE_READING,
        data_key="abs1",
        spatial_context=SpatialContextEnum.WELL_SPECIFIC,
        data_value_numeric=0.8,
        data_quality_score=0.99,
        measurement_timestamp=datetime.datetime.now(datetime.timezone.utc),
      ),
    )

    # Entry 2: File, low quality
    await create_function_data_output(
      db,
      FunctionDataOutputCreate(
        **common_args,
        data_type=DataOutputTypeEnum.PLATE_IMAGE,
        data_key="img1",
        spatial_context=SpatialContextEnum.PLATE_LEVEL,
        file_path="/path/to/img.png",
        data_quality_score=0.5,
        data_value_numeric=None,
        measurement_timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1),
      ),
    )

    # Entry 3: Numeric, no quality score
    await create_function_data_output(
      db,
      FunctionDataOutputCreate(
        **common_args,
        data_type=DataOutputTypeEnum.TEMPERATURE_READING,
        data_key="temp1",
        spatial_context=SpatialContextEnum.MACHINE_LEVEL,
        data_value_numeric=37.0,
        data_quality_score=None,
      ),
    )

    # FIX: Provide all optional arguments to the SearchFilters constructor.
    # Test filter by data type
    filters = SearchFilters(
      protocol_run_accession_id=None,
      function_call_log_accession_id=None,
      data_types=[DataOutputTypeEnum.PLATE_IMAGE],
      spatial_contexts=None,
      machine_accession_id=None,
      resource_accession_id=None,
      date_range_start=None,
      date_range_end=None,
      has_numeric_data=None,
      has_file_data=None,
      min_quality_score=None,
    )
    results = await list_function_data_outputs(db, filters)
    assert len(results) == 1
    assert results[0].data_type == DataOutputTypeEnum.PLATE_IMAGE

    # Test filter by has_numeric_data
    filters = SearchFilters(
      protocol_run_accession_id=None,
      function_call_log_accession_id=None,
      data_types=None,
      spatial_contexts=None,
      machine_accession_id=None,
      resource_accession_id=None,
      date_range_start=None,
      date_range_end=None,
      has_numeric_data=True,
      has_file_data=None,
      min_quality_score=None,
    )
    results = await list_function_data_outputs(db, filters)
    assert len(results) == 2

    # Test filter by min_quality_score
    filters = SearchFilters(
      protocol_run_accession_id=None,
      function_call_log_accession_id=None,
      data_types=None,
      spatial_contexts=None,
      machine_accession_id=None,
      resource_accession_id=None,
      date_range_start=None,
      date_range_end=None,
      has_numeric_data=None,
      has_file_data=None,
      min_quality_score=0.9,
    )
    results = await list_function_data_outputs(db, filters)
    assert len(results) == 1
    assert results[0].data_quality_score == 0.99
