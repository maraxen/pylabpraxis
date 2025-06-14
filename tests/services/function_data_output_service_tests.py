# filepath: tests/services/function_data_output_service_tests.py
import datetime
import json
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from praxis.backend.utils.uuid import uuid7
from praxis.backend.models import (
  DataOutputTypeEnum,
  FunctionDataOutputCreate,
  FunctionDataOutputOrm,
  SpatialContextEnum,
  WellDataOutputCreate,
  WellDataOutputOrm,
)
import praxis.bac


class TestFunctionDataOutputService:
  """Test cases for function data output service operations."""

  @pytest.fixture
  def mock_db(self):
    """Mock async database session."""
    mock_db = MagicMock(spec=AsyncSession)
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.delete = AsyncMock()
    return mock_db

  @pytest.fixture
  def sample_function_data_output_create(self):
    """Sample FunctionDataOutputCreate data."""
    return FunctionDataOutputCreate(
      function_call_id=uuid4(),
      data_type=DataOutputTypeEnum.ABSORBANCE_READING,
      data_value_numeric=0.75,
      spatial_context=SpatialContextEnum.PLATE_WELL,
      spatial_coordinates={"row": 0, "column": 0},
      timestamp=datetime.datetime.now(),
      metadata_json={"wavelength": 450, "temperature": 25},
    )

  @pytest.fixture
  def sample_well_data_output_create(self):
    """Sample WellDataOutputCreate data."""
    return WellDataOutputCreate(
      function_call_id=uuid4(),
      plate_resource_id=uuid4(),
      well_row=0,
      well_column=0,
      data_type=DataOutputTypeEnum.ABSORBANCE_READING,
      data_value_numeric=0.85,
      timestamp=datetime.datetime.now(),
      metadata_json={"gain": 100, "integration_time": 1000},
    )

  @pytest.mark.asyncio
  async def test_create_function_data_output_success(
    self, mock_db, sample_function_data_output_create
  ):
    """Test successful creation of function data output."""
    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      # Mock the database query and result
      mock_result = MagicMock()
      mock_result.scalar_one_or_none.return_value = None
      mock_db.execute = AsyncMock(return_value=mock_result)

      # Call the service function
      result = await function_data_output_service.create_function_data_output(
        mock_db, sample_function_data_output_create
      )

      # Verify the result
      assert result is not None
      assert result.data_type == DataOutputTypeEnum.ABSORBANCE_READING
      assert result.data_value_numeric == 0.75
      assert result.spatial_context == SpatialContextEnum.PLATE_WELL

      # Verify database operations
      mock_db.add.assert_called_once()
      mock_db.commit.assert_called_once()
      mock_db.refresh.assert_called_once()

  @pytest.mark.asyncio
  async def test_create_well_data_output_success(
    self, mock_db, sample_well_data_output_create
  ):
    """Test successful creation of well data output."""
    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      # Mock the database query and result
      mock_result = MagicMock()
      mock_result.scalar_one_or_none.return_value = None
      mock_db.execute = AsyncMock(return_value=mock_result)

      # Call the service function
      result = await function_data_output_service.create_well_data_output(
        mock_db, sample_well_data_output_create
      )

      # Verify the result
      assert result is not None
      assert result.data_type == DataOutputTypeEnum.ABSORBANCE_READING
      assert result.data_value_numeric == 0.85
      assert result.well_row == 0
      assert result.well_column == 0

      # Verify database operations
      mock_db.add.assert_called_once()
      mock_db.commit.assert_called_once()
      mock_db.refresh.assert_called_once()

  @pytest.mark.asyncio
  async def test_get_function_data_output_success(self, mock_db):
    """Test successful retrieval of function data output."""
    output_id = uuid4()
    mock_orm = MagicMock(spec=FunctionDataOutputOrm)
    mock_orm.accession_id = output_id
    mock_orm.data_type = DataOutputTypeEnum.ABSORBANCE_READING

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalar_one_or_none.return_value = mock_orm
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.get_function_data_output(
        mock_db, output_id
      )

      assert result is not None
      assert result.accession_id == output_id
      mock_db.execute.assert_called_once()

  @pytest.mark.asyncio
  async def test_get_function_data_output_not_found(self, mock_db):
    """Test retrieval of non-existent function data output."""
    output_id = uuid4()

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalar_one_or_none.return_value = None
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.get_function_data_output(
        mock_db, output_id
      )

      assert result is None
      mock_db.execute.assert_called_once()

  @pytest.mark.asyncio
  async def test_get_function_data_outputs_with_filters(self, mock_db):
    """Test retrieval of function data outputs with filters."""
    function_call_id = uuid4()
    mock_orm_list = [
      MagicMock(spec=FunctionDataOutputOrm),
      MagicMock(spec=FunctionDataOutputOrm),
    ]

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalars.return_value.all.return_value = mock_orm_list
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.get_function_data_outputs(
        db=mock_db,
        function_call_id=function_call_id,
        data_type=DataOutputTypeEnum.ABSORBANCE_READING,
        skip=0,
        limit=10,
      )

      assert len(result) == 2
      mock_db.execute.assert_called_once()

  @pytest.mark.asyncio
  async def test_update_function_data_output_success(self, mock_db):
    """Test successful update of function data output."""
    output_id = uuid4()
    mock_orm = MagicMock(spec=FunctionDataOutputOrm)
    mock_orm.accession_id = output_id

    update_data = MagicMock()
    update_data.data_value_numeric = 0.95
    update_data.metadata_json = {"updated": True}

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalar_one_or_none.return_value = mock_orm
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.update_function_data_output(
        mock_db, output_id, update_data
      )

      assert result is not None
      mock_db.commit.assert_called_once()
      mock_db.refresh.assert_called_once()

  @pytest.mark.asyncio
  async def test_delete_function_data_output_success(self, mock_db):
    """Test successful deletion of function data output."""
    output_id = uuid4()
    mock_orm = MagicMock(spec=FunctionDataOutputOrm)

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalar_one_or_none.return_value = mock_orm
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.delete_function_data_output(
        mock_db, output_id
      )

      assert result is True
      mock_db.delete.assert_called_once_with(mock_orm)
      mock_db.commit.assert_called_once()

  @pytest.mark.asyncio
  async def test_delete_function_data_output_not_found(self, mock_db):
    """Test deletion of non-existent function data output."""
    output_id = uuid4()

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalar_one_or_none.return_value = None
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.delete_function_data_output(
        mock_db, output_id
      )

      assert result is False
      mock_db.delete.assert_not_called()


class TestPlateVisualizationService:
  """Test cases for plate visualization functionality."""

  @pytest.fixture
  def mock_db(self):
    """Mock async database session."""
    mock_db = MagicMock(spec=AsyncSession)
    return mock_db

  @pytest.mark.asyncio
  async def test_get_plate_visualization_data_success(self, mock_db):
    """Test successful retrieval of plate visualization data."""
    plate_resource_id = uuid4()
    mock_well_data = [
      MagicMock(
        well_row=0,
        well_column=0,
        data_value_numeric=0.75,
        data_type=DataOutputTypeEnum.ABSORBANCE_READING,
      ),
      MagicMock(
        well_row=0,
        well_column=1,
        data_value_numeric=0.85,
        data_type=DataOutputTypeEnum.ABSORBANCE_READING,
      ),
    ]

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalars.return_value.all.return_value = mock_well_data
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.get_plate_visualization_data(
        db=mock_db,
        plate_resource_id=plate_resource_id,
        data_type=DataOutputTypeEnum.ABSORBANCE_READING,
      )

      assert result is not None
      assert result.plate_resource_id == plate_resource_id
      assert len(result.well_data) == 2
      assert result.data_range["min"] == 0.75
      assert result.data_range["max"] == 0.85
      mock_db.execute.assert_called_once()

  @pytest.mark.asyncio
  async def test_get_plate_visualization_data_no_data(self, mock_db):
    """Test retrieval of plate visualization data with no data."""
    plate_resource_id = uuid4()

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalars.return_value.all.return_value = []
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.get_plate_visualization_data(
        db=mock_db,
        plate_resource_id=plate_resource_id,
      )

      assert result is None
      mock_db.execute.assert_called_once()


class TestWellDataOutputService:
  """Test cases for well-specific data output operations."""

  @pytest.fixture
  def mock_db(self):
    """Mock async database session."""
    mock_db = MagicMock(spec=AsyncSession)
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.delete = AsyncMock()
    return mock_db

  @pytest.mark.asyncio
  async def test_get_well_data_outputs_with_filters(self, mock_db):
    """Test retrieval of well data outputs with spatial filters."""
    plate_resource_id = uuid4()
    mock_well_data = [
      MagicMock(spec=WellDataOutputOrm),
      MagicMock(spec=WellDataOutputOrm),
    ]

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalars.return_value.all.return_value = mock_well_data
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.get_well_data_outputs(
        db=mock_db,
        plate_resource_id=plate_resource_id,
        well_row=0,
        well_column=0,
        data_type=DataOutputTypeEnum.ABSORBANCE_READING,
        skip=0,
        limit=10,
      )

      assert len(result) == 2
      mock_db.execute.assert_called_once()

  @pytest.mark.asyncio
  async def test_update_well_data_output_success(self, mock_db):
    """Test successful update of well data output."""
    output_id = uuid4()
    mock_orm = MagicMock(spec=WellDataOutputOrm)
    mock_orm.accession_id = output_id

    update_data = MagicMock()
    update_data.data_value_numeric = 0.95

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalar_one_or_none.return_value = mock_orm
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.update_well_data_output(
        mock_db, output_id, update_data
      )

      assert result is not None
      mock_db.commit.assert_called_once()
      mock_db.refresh.assert_called_once()

  @pytest.mark.asyncio
  async def test_delete_well_data_output_success(self, mock_db):
    """Test successful deletion of well data output."""
    output_id = uuid4()
    mock_orm = MagicMock(spec=WellDataOutputOrm)

    with patch(
      "praxis.backend.services.function_data_output_service.sqlalchemy.select"
    ) as mock_select:
      mock_result = MagicMock()
      mock_result.scalar_one_or_none.return_value = mock_orm
      mock_db.execute = AsyncMock(return_value=mock_result)

      result = await function_data_output_service.delete_well_data_output(
        mock_db, output_id
      )

      assert result is True
      mock_db.delete.assert_called_once_with(mock_orm)
      mock_db.commit.assert_called_once()
