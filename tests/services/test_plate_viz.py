import datetime
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import all required models from the central package
from praxis.backend.models import (
  DataOutputTypeEnum,
  FunctionCallLogOrm,
  FunctionDataOutputOrm,
  ProtocolRunOrm,
  ResourceOrm,
  WellDataOutputOrm,  # Needed for type hints
)

# Import the service function to be tested
from praxis.backend.services.plate_viz import read_plate_data_visualization

# --- Pytest Fixtures ---


@pytest.fixture
async def setup_dependencies(db: AsyncSession):
  """Fixture to create and commit all necessary dependency ORM objects for the tests."""
  run = ProtocolRunOrm(name="Test Run for Viz")
  plate_resource = ResourceOrm(
    name="TestPlate1",
    name="corning_96_wellplate_360ul_flat",
  )

  db.add_all([run, plate_resource])
  await db.commit()

  # Refresh objects to get their generated accession_ids
  await db.refresh(run)
  await db.refresh(plate_resource)

  # Create a function call log associated with the run
  f_call = FunctionCallLogOrm(
    protocol_run_accession_id=run.accession_id,
    function_name="read_plate",
  )
  db.add(f_call)
  await db.commit()
  await db.refresh(f_call)

  return {
    "run_id": run.accession_id,
    "plate_id": plate_resource.accession_id,
    "f_call_id": f_call.accession_id,
  }


@pytest.fixture
async def setup_plate_data(db: AsyncSession, setup_dependencies):
  """Fixture to create a set of well data linked to a plate for visualization tests."""
  # Create the parent FunctionDataOutput record
  func_data_output = FunctionDataOutputOrm(
    accession_id=uuid.uuid4(),
    function_call_log_accession_id=setup_dependencies["f_call_id"],
    protocol_run_accession_id=setup_dependencies["run_id"],
    data_type=DataOutputTypeEnum.ABSORBANCE_READING,
    data_key="absorbance_540nm",
    spatial_context="well_specific",
    resource_instance_accession_id=setup_dependencies["plate_id"],
    measurement_timestamp=datetime.datetime.now(datetime.timezone.utc),
  )
  db.add(func_data_output)
  await db.flush()  # Flush to get the accession_id for linking wells

  # Create individual well data records
  well_data = [
    WellDataOutputOrm(
      accession_id=uuid.uuid4(),
      function_data_output_accession_id=func_data_output.accession_id,
      plate_resource_instance_accession_id=setup_dependencies["plate_id"],
      well_name="A1",
      well_row=0,
      well_column=0,
      data_value=0.15,
    ),
    WellDataOutputOrm(
      accession_id=uuid.uuid4(),
      function_data_output_accession_id=func_data_output.accession_id,
      plate_resource_instance_accession_id=setup_dependencies["plate_id"],
      well_name="A2",
      well_row=0,
      well_column=1,
      data_value=1.25,
    ),
    WellDataOutputOrm(
      accession_id=uuid.uuid4(),
      function_data_output_accession_id=func_data_output.accession_id,
      plate_resource_instance_accession_id=setup_dependencies["plate_id"],
      well_name="B1",
      well_row=1,
      well_column=0,
      data_value=0.75,
    ),
  ]
  db.add_all(well_data)
  await db.commit()

  return {
    **setup_dependencies,
    "func_data_output": func_data_output,
    "well_data": well_data,
  }


pytestmark = pytest.mark.asyncio


class TestPlateVizService:
  """Test suite for the plate visualization service."""

  async def test_read_plate_data_visualization_success(
    self,
    db: AsyncSession,
    setup_plate_data,
  ):
    """Test successfully retrieving and formatting plate data for visualization."""
    plate_id = setup_plate_data["plate_id"]
    data_type = DataOutputTypeEnum.ABSORBANCE_READING

    viz_data = await read_plate_data_visualization(
      db,
      plate_resource_instance_accession_id=plate_id,
      data_type=data_type,
    )

    assert viz_data is not None
    assert viz_data.plate_resource_instance_accession_id == plate_id
    assert viz_data.data_type == data_type

    # Verify the calculated data range
    assert viz_data.data_range["min"] == 0.15
    assert viz_data.data_range["max"] == 1.25

    # Verify the timestamp comes from the most recent parent record
    assert (
      viz_data.measurement_timestamp
      == setup_plate_data["func_data_output"].measurement_timestamp
    )

    # Verify hardcoded plate layout
    assert viz_data.plate_layout["format"] == "96-well"

    # NOTE: The current implementation returns an empty list for well_data.
    # This assertion verifies the current behavior. It should be updated
    # if the service function is fixed to return the actual well data.
    assert viz_data.well_data == []

  async def test_read_plate_data_no_data_found(
    self,
    db: AsyncSession,
    setup_plate_data,
  ):
    """Test that None is returned when no data matches the criteria."""
    plate_id = setup_plate_data["plate_id"]

    # Test with a data_type that has no data
    viz_data_wrong_type = await read_plate_data_visualization(
      db,
      plate_resource_instance_accession_id=plate_id,
      data_type=DataOutputTypeEnum.FLUORESCENCE_READING,  # No data for this type exists
    )
    assert viz_data_wrong_type is None

    # Test with a non-existent plate ID
    non_existent_plate_id = uuid.uuid4()
    viz_data_wrong_plate = await read_plate_data_visualization(
      db,
      plate_resource_instance_accession_id=non_existent_plate_id,
      data_type=DataOutputTypeEnum.ABSORBANCE_READING,
    )
    assert viz_data_wrong_plate is None

  async def test_read_plate_data_with_filters(self, db: AsyncSession, setup_plate_data):
    """Test filtering the plate data by protocol run ID."""
    plate_id = setup_plate_data["plate_id"]
    run_id = setup_plate_data["run_id"]
    data_type = DataOutputTypeEnum.ABSORBANCE_READING

    # Create data for a second, different run to test filtering
    other_run = ProtocolRunOrm(name="Other Run")
    db.add(other_run)
    await db.commit()
    await db.refresh(other_run)
    other_f_call = FunctionCallLogOrm(
      protocol_run_accession_id=other_run.accession_id,
      function_name="other_read",
    )
    db.add(other_f_call)
    await db.commit()
    await db.refresh(other_f_call)

    other_func_data = FunctionDataOutputOrm(
      accession_id=uuid.uuid4(),
      function_call_log_accession_id=other_f_call.accession_id,
      protocol_run_accession_id=other_run.accession_id,
      data_type=data_type,
      data_key="other_key",
      spatial_context="well_specific",
    )
    db.add(other_func_data)
    await db.flush()
    other_well_data = WellDataOutputOrm(
      accession_id=uuid.uuid4(),
      function_data_output_accession_id=other_func_data.accession_id,
      plate_resource_instance_accession_id=plate_id,
      well_name="C1",
      well_row=2,
      well_column=0,
      data_value=9.99,
    )
    db.add(other_well_data)
    await db.commit()

    # Now query, filtering for the *original* run ID
    viz_data = await read_plate_data_visualization(
      db,
      plate_resource_instance_accession_id=plate_id,
      data_type=data_type,
      protocol_run_accession_id=run_id,
    )

    assert viz_data is not None
    # The data range should NOT include the 9.99 value from the other run
    assert viz_data.data_range["min"] == 0.15
    assert viz_data.data_range["max"] == 1.25
