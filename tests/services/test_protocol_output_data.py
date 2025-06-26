import datetime
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import all required models from the central package
from praxis.backend.models import (
  DataOutputTypeEnum,
  FunctionCallLogOrm,
  FunctionDataOutputOrm,
  MachineOrm,
  ProtocolRunOrm,
  ResourceOrm,
  SpatialContextEnum,
)

# Import the service function to be tested
from praxis.backend.services.protocol_output_data import (
  read_protocol_run_data_summary,
)

# --- Pytest Fixtures ---


@pytest.fixture
async def setup_summary_data(db: AsyncSession):
  """Fixture to create a rich set of data outputs for a single protocol run,
  enabling a thorough test of the summary aggregation function.
  """
  # Create parent entities
  run = ProtocolRunOrm(name="Summary Test Run")
  f_call = FunctionCallLogOrm(
    protocol_run_accession_id=run.accession_id,
    function_name="complex_assay",
  )
  machine = MachineOrm(
    user_friendly_name=f"SummaryMachine_{uuid.uuid4()}",
    python_fqn="machine.fqn",
  )
  resource = ResourceOrm(
    user_assigned_name="SummaryResource",
    name="summary_resource_def",
  )

  db.add_all([run, f_call, machine, resource])
  await db.commit()
  for obj in [run, f_call, machine, resource]:
    await db.refresh(obj)

  # Create a diverse set of FunctionDataOutputOrm records for the same run
  timestamp1 = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
    minutes=10,
  )
  timestamp2 = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
    minutes=5,
  )

  data_outputs = [
    # 1. Numeric data with machine and resource
    FunctionDataOutputOrm(
      accession_id=uuid.uuid4(),
      protocol_run_accession_id=run.accession_id,
      function_call_log_accession_id=f_call.accession_id,
      data_type=DataOutputTypeEnum.ABSORBANCE_READING,
      data_key="abs_1",
      spatial_context=SpatialContextEnum.MACHINE_LEVEL,
      machine_accession_id=machine.accession_id,
      resource_instance_accession_id=resource.accession_id,
      data_value_numeric=0.5,
      measurement_timestamp=timestamp1,
    ),
    # 2. File data with machine
    FunctionDataOutputOrm(
      accession_id=uuid.uuid4(),
      protocol_run_accession_id=run.accession_id,
      function_call_log_accession_id=f_call.accession_id,
      data_type=DataOutputTypeEnum.PLATE_IMAGE,
      data_key="img_1",
      spatial_context=SpatialContextEnum.PLATE_LEVEL,
      machine_accession_id=machine.accession_id,
      file_path="/path/to/img1.png",
      file_size_bytes=1024,
      measurement_timestamp=timestamp1,
    ),
    # 3. Text data with only a resource
    FunctionDataOutputOrm(
      accession_id=uuid.uuid4(),
      protocol_run_accession_id=run.accession_id,
      function_call_log_accession_id=f_call.accession_id,
      data_type=DataOutputTypeEnum.ERROR_LOG,
      data_key="error_1",
      spatial_context=SpatialContextEnum.GLOBAL,
      resource_instance_accession_id=resource.accession_id,
      data_value_text="An error occurred",
      measurement_timestamp=timestamp2,
    ),
    # 4. Another numeric data point with the same data type as #1
    FunctionDataOutputOrm(
      accession_id=uuid.uuid4(),
      protocol_run_accession_id=run.accession_id,
      function_call_log_accession_id=f_call.accession_id,
      data_type=DataOutputTypeEnum.ABSORBANCE_READING,
      data_key="abs_2",
      spatial_context=SpatialContextEnum.MACHINE_LEVEL,
      machine_accession_id=machine.accession_id,
      resource_instance_accession_id=resource.accession_id,
      data_value_numeric=0.6,
      measurement_timestamp=timestamp2,
    ),
  ]
  db.add_all(data_outputs)
  await db.commit()

  return {
    "run_id": run.accession_id,
    "machine_id": machine.accession_id,
    "resource_id": resource.accession_id,
    "timestamps": {timestamp1, timestamp2},
  }


pytestmark = pytest.mark.asyncio


class TestProtocolOutputDataService:
  """Test suite for protocol output data aggregation services."""

  async def test_read_protocol_run_data_summary_with_data(
    self,
    db: AsyncSession,
    setup_summary_data,
  ):
    """Test retrieving a data summary for a protocol run with diverse data outputs."""
    run_id = setup_summary_data["run_id"]

    summary = await read_protocol_run_data_summary(db, run_id)

    assert summary is not None
    assert summary.protocol_run_accession_id == run_id

    # 1. Test total count
    assert summary.total_data_outputs == 4

    # 2. Test unique data types
    assert set(summary.data_types) == {"absorbance_reading", "plate_image", "error_log"}

    # 3. Test unique machines and resource
    assert summary.machines_used == [setup_summary_data["machine_id"]]
    assert summary.resource_with_data == [setup_summary_data["resource_id"]]

    # 4. Test file attachments
    assert len(summary.file_attachments) == 1
    assert summary.file_attachments[0]["file_path"] == "/path/to/img1.png"
    assert summary.file_attachments[0]["file_size_bytes"] == 1024
    assert summary.file_attachments[0]["data_type"] == "plate_image"

    # 5. Test data timeline aggregation
    assert len(summary.data_timeline) == 3  # 2 events at timestamp1, 1 at timestamp2
    timeline_events = {
      (event["data_type"], event["count"]) for event in summary.data_timeline
    }
    assert ("absorbance_reading", 1) in timeline_events
    assert ("plate_image", 1) in timeline_events
    assert ("error_log", 1) in timeline_events
    # Check that another absorbance reading was added to the summary at a different timestamp
    assert (
      len(
        [
          event
          for event in summary.data_timeline
          if event["data_type"] == "absorbance_reading"
        ],
      )
      == 2
    )

  async def test_read_protocol_run_data_summary_for_empty_run(self, db: AsyncSession):
    """Test retrieving a data summary for a protocol run with no data outputs."""
    # Create a run with no associated data
    empty_run = ProtocolRunOrm(name="Empty Run")
    db.add(empty_run)
    await db.commit()
    await db.refresh(empty_run)

    summary = await read_protocol_run_data_summary(db, empty_run.accession_id)

    assert summary is not None
    assert summary.protocol_run_accession_id == empty_run.accession_id
    assert summary.total_data_outputs == 0
    assert summary.data_types == []
    assert summary.machines_used == []
    assert summary.resource_with_data == []
    assert summary.data_timeline == []
    assert summary.file_attachments == []
