from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import DataOutputTypeEnum
from praxis.backend.models.domain.outputs import PlateDataVisualization
from praxis.backend.models.domain.resource import Resource, ResourceDefinition
from praxis.backend.services.plate_viz import read_plate_data_visualization
from praxis.backend.utils.uuid import uuid7


@pytest.fixture
def mock_db_session():
  """Fixture for a mocked SQLAlchemy async session."""
  return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
@patch("praxis.backend.services.plate_viz.resource_service", new_callable=AsyncMock)
async def test_read_plate_data_visualization_with_geometry(
  mock_resource_service: AsyncMock,
  mock_db_session: AsyncMock,
) -> None:
  """Test reading plate data visualization with custom geometry."""
  plate_id = uuid7()
  data_type = DataOutputTypeEnum.GENERIC_MEASUREMENT

  # Case 1: Plate with defined geometry (384-well)
  resource_def_384 = MagicMock(spec=ResourceDefinition)
  resource_def_384.properties_json = {"num_items_x": 24, "num_items_y": 16}
  
  resource_384 = MagicMock(spec=Resource)
  resource_384.accession_id = plate_id
  resource_384.name = "Test 384 Plate"
  resource_384.resource_definition = resource_def_384

  mock_resource_service.get.return_value = resource_384

  # Mock DB response for well data (at least one entry to return something)
  mock_well_data = MagicMock()
  mock_well_data.data_value = 10.0
  mock_well_data.function_data_output.measurement_timestamp = datetime.now()

  mock_result = MagicMock()
  mock_result.scalars.return_value.all.return_value = [mock_well_data]
  mock_db_session.execute.return_value = mock_result

  result_384 = await read_plate_data_visualization(
    db=mock_db_session,
    plate_resource_accession_id=plate_id,
    data_type=data_type,
  )

  assert result_384 is not None
  assert result_384.plate_layout["rows"] == 16
  assert result_384.plate_layout["columns"] == 24
  assert result_384.plate_layout["total_wells"] == 384
  assert result_384.plate_layout["format"] == "384-well"


@pytest.mark.asyncio
@patch("praxis.backend.services.plate_viz.resource_service", new_callable=AsyncMock)
async def test_read_plate_data_visualization_fallback(
  mock_resource_service: AsyncMock,
  mock_db_session: AsyncMock,
) -> None:
  """Test fallback to 96-well when geometry is missing."""
  plate_id = uuid7()
  data_type = DataOutputTypeEnum.GENERIC_MEASUREMENT

  # Case 2: Fallback (no definition or no properties)
  resource_def_96 = MagicMock(spec=ResourceDefinition)
  resource_def_96.properties_json = None
  
  resource_96 = MagicMock(spec=Resource)
  resource_96.accession_id = plate_id
  resource_96.name = "Test 96 Plate"
  resource_96.resource_definition = resource_def_96

  mock_resource_service.get.return_value = resource_96

  # Mock DB response
  mock_well_data = MagicMock()
  mock_well_data.data_value = 10.0
  mock_well_data.function_data_output.measurement_timestamp = datetime.now()

  mock_result = MagicMock()
  mock_result.scalars.return_value.all.return_value = [mock_well_data]
  mock_db_session.execute.return_value = mock_result

  result_96 = await read_plate_data_visualization(
    db=mock_db_session,
    plate_resource_accession_id=plate_id,
    data_type=data_type,
  )

  assert result_96 is not None
  assert result_96.plate_layout["rows"] == 8
  assert result_96.plate_layout["columns"] == 12
  assert result_96.plate_layout["format"] == "96-well"
