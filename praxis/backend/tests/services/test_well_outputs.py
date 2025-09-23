import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from praxis.backend.services.well_outputs import WellDataOutputCRUDService
from praxis.backend.models.pydantic_internals.outputs import WellDataOutputCreate, WellDataOutputUpdate
from praxis.backend.models.orm.outputs import WellDataOutputOrm
from praxis.backend.utils.uuid import uuid7

@pytest.fixture
def mock_db_session():
    """Fixture for a mock database session."""
    session = AsyncMock(spec=AsyncSession)

    mock_result = MagicMock()
    session.execute.return_value = mock_result

    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_scalars.all.return_value = []

    mock_result.scalar_one_or_none.return_value = None

    return session

@pytest.fixture
def well_output_crud_service():
    """Fixture for a WellDataOutputCRUDService instance."""
    return WellDataOutputCRUDService(WellDataOutputOrm)

@pytest.mark.asyncio
@patch("praxis.backend.services.well_outputs.parse_well_name", return_value=(0, 0))
@patch("praxis.backend.services.well_outputs.read_plate_dimensions", return_value={"columns": 12})
@patch("praxis.backend.services.well_outputs.calculate_well_index", return_value=0)
@patch("praxis.backend.services.well_outputs.WellDataOutputOrm")
async def test_create_well_data_output_success(
    MockWellDataOutputOrm,
    mock_calculate_well_index,
    mock_read_plate_dimensions,
    mock_parse_well_name,
    well_output_crud_service,
    mock_db_session,
):
    """Test successful creation of a well data output."""
    well_data_output_create = WellDataOutputCreate(
        function_data_output_accession_id=uuid7(),
        plate_resource_accession_id=uuid7(),
        well_name="A1",
        well_row=0,
        well_column=0,
        data_value=1.23
    )

    result = await well_output_crud_service.create(mock_db_session, obj_in=well_data_output_create)

    assert result is not None
    mock_db_session.add.assert_called_once()
    mock_db_session.flush.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)
    MockWellDataOutputOrm.assert_called_once()

@pytest.mark.asyncio
@patch("praxis.backend.services.well_outputs.parse_well_name", side_effect=ValueError("Invalid well name"))
async def test_create_well_data_output_invalid_well_name(
    mock_parse_well_name,
    well_output_crud_service,
    mock_db_session,
):
    """Test error handling when creating an output with an invalid well name."""
    well_data_output_create = WellDataOutputCreate(
        function_data_output_accession_id=uuid7(),
        plate_resource_accession_id=uuid7(),
        well_name="Z99",
        well_row=0,
        well_column=0,
        data_value=1.23
    )

    with pytest.raises(ValueError, match="Invalid well name"):
        await well_output_crud_service.create(mock_db_session, obj_in=well_data_output_create)

@pytest.mark.asyncio
@patch("praxis.backend.services.well_outputs.select")
@patch("praxis.backend.services.well_outputs.joinedload")
async def test_get_well_data_output(mock_joinedload, mock_select, well_output_crud_service, mock_db_session):
    """Test retrieval of a single well data output."""
    output_id = uuid7()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = MagicMock()

    await well_output_crud_service.get(mock_db_session, accession_id=output_id)

    mock_select.assert_called_once()
    mock_db_session.execute.assert_called_once()

@pytest.mark.asyncio
@patch("praxis.backend.services.well_outputs.select")
@patch("praxis.backend.services.well_outputs.joinedload")
@patch("praxis.backend.services.well_outputs.apply_search_filters")
async def test_get_multi_well_data_outputs(mock_apply_search_filters, mock_joinedload, mock_select, well_output_crud_service, mock_db_session):
    """Test retrieval of multiple well data outputs."""
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [MagicMock(), MagicMock()]

    mock_filters = MagicMock()
    mock_filters.limit = 10
    mock_filters.offset = 0
    mock_filters.sort_by = None
    mock_filters.sort_order = 'asc'

    result = await well_output_crud_service.get_multi(mock_db_session, filters=mock_filters)

    assert len(result) == 2
    mock_select.assert_called_once()
    mock_apply_search_filters.assert_called_once()
    mock_db_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_well_data_output(well_output_crud_service, mock_db_session):
    """Test updating a well data output."""
    db_obj = MagicMock()
    update_data = WellDataOutputUpdate(data_value=4.56)

    updated_obj = await well_output_crud_service.update(mock_db_session, db_obj=db_obj, obj_in=update_data)

    assert updated_obj.data_value == 4.56
    mock_db_session.flush.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(db_obj)

@pytest.mark.asyncio
@patch("praxis.backend.services.well_outputs.delete")
async def test_remove_well_data_output(mock_delete, well_output_crud_service, mock_db_session):
    """Test deleting a well data output."""
    output_id = uuid7()
    with patch.object(well_output_crud_service, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MagicMock()
        await well_output_crud_service.remove(db=mock_db_session, accession_id=output_id)

        mock_delete.assert_called_once()
        mock_db_session.execute.assert_called_once()
        mock_get.assert_called_once_with(mock_db_session, accession_id=output_id)
