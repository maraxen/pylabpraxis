"""Tests for the Well Data Output service layer."""

import uuid
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models import (
  DataOutputTypeEnum,
  FunctionCallLogOrm,
  FunctionDataOutputOrm,
  ProtocolRunOrm,
  ResourceOrm,
  SpatialContextEnum,
  WellDataOutputCreate,
  WellDataOutputOrm,
  WellDataOutputUpdate,
)
from praxis.backend.services import (
  create_well_data_output,
  create_well_data_outputs,
  create_well_data_outputs_from_flat_array,
  delete_well_data_output,
  read_well_data_output,
  read_well_data_outputs,
  update_well_data_output,
)

# --- Pytest Fixtures ---


@pytest.fixture
def mock_plate_parsing_helpers(mocker) -> None:
  """Mock the helper functions for plate parsing and dimension reading."""
  mocker.patch(
    "praxis.backend.services.function_output_data.parse_well_name",
    return_value=(0, 0),
  )
  mocker.patch(
    "praxis.backend.services.function_output_data.calculate_well_index",
    return_value=0,
  )
  mocker.patch(
    "praxis.backend.services.function_output_data.read_plate_dimensions",
    new_callable=AsyncMock,
    return_value={"rows": 8, "columns": 12},
  )


@pytest.fixture
async def plate_resource(db: AsyncSession) -> ResourceOrm:
  """Fixture for a plate ResourceOrm."""
  plate = ResourceOrm(name="TestPlateForWells", resource_definition_name="plate_def")
  db.add(plate)
  await db.commit()
  return plate


@pytest.fixture
async def func_data_output(
  db: AsyncSession,
  plate_resource: ResourceOrm,
) -> FunctionDataOutputOrm:
  """Fixture for a parent FunctionDataOutputOrm."""
  run = ProtocolRunOrm(name="Well Data Test Run")
  f_call = FunctionCallLogOrm(
    protocol_run_accession_id=run.accession_id,
    function_name="read_wells",
  )
  db.add_all([run, f_call])
  await db.commit()

  fdo = FunctionDataOutputOrm(
    accession_id=uuid.uuid4(),
    protocol_run_accession_id=run.accession_id,
    function_call_log_accession_id=f_call.accession_id,
    data_type=DataOutputTypeEnum.OPTICAL_DENSITY,
    data_key="od_600",
    spatial_context=SpatialContextEnum.WELL_SPECIFIC,
    resource_accession_id=plate_resource.accession_id,
  )
  db.add(fdo)
  await db.commit()
  return fdo


@pytest.fixture
async def existing_well_data(
  db: AsyncSession,
  func_data_output: FunctionDataOutputOrm,
  plate_resource: ResourceOrm,
  mock_plate_parsing_helpers,
) -> WellDataOutputOrm:
  """Fixture that creates a single WellDataOutputOrm for testing."""
  well_create = WellDataOutputCreate(
    function_data_output_accession_id=func_data_output.accession_id,
    plate_resource_accession_id=plate_resource.accession_id,
    well_name="A1",
    well_row=0,
    well_column=0,
    well_index=0,
    data_value=0.55,
  )
  return await create_well_data_output(db, well_create)


pytestmark = pytest.mark.asyncio


class TestWellDataOutputService:

  """Test suite for the Well Data Output service layer."""

  async def test_create_and_read_well_data_output(
    self,
    db: AsyncSession,
    func_data_output: FunctionDataOutputOrm,
    plate_resource: ResourceOrm,
    mock_plate_parsing_helpers,
  ) -> None:
    """Test creating a single well data record and reading it back."""
    well_create = WellDataOutputCreate(
      function_data_output_accession_id=func_data_output.accession_id,
      plate_resource_accession_id=plate_resource.accession_id,
      well_name="B2",
      well_row=0,  # Mocked to return 0
      well_column=0,  # Mocked to return 0
      well_index=0,  # Mocked to return 0
      data_value=0.99,
    )
    created_well = await create_well_data_output(db, well_create)

    assert created_well is not None
    assert created_well.well_name == "B2"
    assert created_well.data_value == 0.99
    # Verify mocked helpers were used
    assert created_well.well_row == 0  # From mock parse_well_name
    assert created_well.well_index == 0  # From mock calculate_well_index

    read_well = await read_well_data_output(db, created_well.accession_id)
    assert read_well is not None
    assert read_well.well_name == "B2"  # TODO: decide if we want an error if name is unaligned with position

  async def test_create_well_data_outputs_batch(
    self,
    db: AsyncSession,
    func_data_output: FunctionDataOutputOrm,
    plate_resource: ResourceOrm,
    mock_plate_parsing_helpers,
  ) -> None:
    """Test creating a batch of well data outputs from a dictionary."""
    well_data_dict = {"A1": 0.1, "A2": 0.2, "H12": 1.2}
    created_wells = await create_well_data_outputs(
      db,
      func_data_output.accession_id,
      plate_resource.accession_id,
      well_data_dict,
    )
    assert len(created_wells) == 3

    well_names = {w.well_name for w in created_wells}
    assert well_names == {"A1", "A2", "H12"}

  async def test_create_well_data_from_flat_array(
    self,
    db: AsyncSession,
    func_data_output: FunctionDataOutputOrm,
    plate_resource: ResourceOrm,
    mocker,
  ) -> None:
    """Test creating well data from a flat array, relying on plate dimensions."""
    # Mock only the dimension reader for this test
    mocker.patch(
      "praxis.backend.services.function_output_data.read_plate_dimensions",
      new_callable=AsyncMock,
      return_value={"rows": 2, "columns": 2},  # A 2x2 plate for simplicity
    )

    data_array = [0.1, 0.2, 0.3, 0.4]
    created_wells = await create_well_data_outputs_from_flat_array(
      db,
      func_data_output.accession_id,
      plate_resource.accession_id,
      data_array,
    )
    assert len(created_wells) == 4

    # Check a specific well to ensure mapping is correct
    well_c2 = next(w for w in created_wells if w.well_index == 3)  # Index 3 should be row 1, col 1 (B2)
    assert well_c2.well_name == "B2"
    assert well_c2.data_value == 0.4

  async def test_create_from_flat_array_fails_if_no_dims(
    self,
    db: AsyncSession,
    func_data_output: FunctionDataOutputOrm,
    plate_resource: ResourceOrm,
    mocker,
  ) -> None:
    """Test that creating from a flat array fails if plate dimensions are not found."""
    mocker.patch(
      "praxis.backend.services.function_output_data.read_plate_dimensions",
      new_callable=AsyncMock,
      return_value=None,
    )

    with pytest.raises(ValueError, match="Could not determine plate dimensions"):
      await create_well_data_outputs_from_flat_array(
        db,
        func_data_output.accession_id,
        plate_resource.accession_id,
        [0.1, 0.2],
      )

  async def test_update_well_data_output(
    self,
    db: AsyncSession,
    existing_well_data: WellDataOutputOrm,
  ) -> None:
    """Test updating an existing well data record."""
    update_model = WellDataOutputUpdate(
      data_value=0.66,
      metadata_json={"source": "update_test"},
    )
    updated_well = await update_well_data_output(
      db,
      existing_well_data.accession_id,
      update_model,
    )

    assert updated_well is not None
    assert updated_well.data_value == 0.66
    assert updated_well.well_name == "A1"  # Ensure other fields are untouched

  async def test_read_well_data_outputs_with_filters(
    self,
    db: AsyncSession,
    existing_well_data: WellDataOutputOrm,
  ) -> None:
    """Test the filtering capabilities of the read_well_data_outputs function."""
    # existing_well_data is in row 0, col 0

    # Filter by plate
    results = await read_well_data_outputs(
      db,
      plate_resource_id=existing_well_data.plate_resource_accession_id,
    )
    assert len(results) == 1
    assert results[0].accession_id == existing_well_data.accession_id

    # Filter by well coordinates
    results = await read_well_data_outputs(db, well_row=0, well_column=0)
    assert len(results) == 1

    # Filter with non-matching coordinates
    results = await read_well_data_outputs(db, well_row=1)
    assert len(results) == 0

  async def test_delete_well_data_output(
    self,
    db: AsyncSession,
    existing_well_data: WellDataOutputOrm,
  ) -> None:
    """Test deleting a well data output record."""
    well_id = existing_well_data.accession_id
    result = await delete_well_data_output(db, well_id)
    assert result is True

    # Verify it's gone
    assert await read_well_data_output(db, well_id) is None
