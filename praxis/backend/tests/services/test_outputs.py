import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.outputs import FunctionDataOutputOrm
from praxis.backend.models.pydantic_internals.outputs import FunctionDataOutputCreate
from praxis.backend.services.outputs import FunctionDataOutputCRUDService
from praxis.backend.models.enums.outputs import DataOutputTypeEnum, SpatialContextEnum
from praxis.backend.utils.uuid import uuid7


@pytest.fixture
def mock_db_session():
    """Fixture for a mocked SQLAlchemy async session."""
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
class TestFunctionDataOutputCRUDService:
    """Test suite for the FunctionDataOutputCRUDService."""

    @pytest.fixture
    def service(self):
        """Fixture for the FunctionDataOutputCRUDService instance."""
        return FunctionDataOutputCRUDService(FunctionDataOutputOrm)

    @patch("praxis.backend.services.outputs.FunctionDataOutputOrm", autospec=True)
    async def test_create_output_success(self, mock_output_orm, service, mock_db_session):
        """Test successful creation of a FunctionDataOutput."""
        output_create_data = FunctionDataOutputCreate(
            protocol_run_accession_id=uuid7(),
            function_call_log_accession_id=uuid7(),
            data_key="test_key",
            data_type=DataOutputTypeEnum.GENERIC_MEASUREMENT,
            data_value=123.45,
            spatial_context=SpatialContextEnum.GLOBAL,
        )

        mock_instance = mock_output_orm.return_value
        mock_instance.accession_id = uuid7()

        mock_db_session.add.return_value = None
        mock_db_session.flush.return_value = None
        mock_db_session.refresh.return_value = None

        created_output = await service.create(db=mock_db_session, obj_in=output_create_data)

        mock_output_orm.assert_called_once()
        mock_db_session.add.assert_called_once_with(mock_instance)
        mock_db_session.flush.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once_with(mock_instance)
        assert created_output == mock_instance

    async def test_get_output_success(self, service, mock_db_session):
        """Test successfully retrieving an existing output by its ID."""
        output_id = uuid7()
        expected_output = MagicMock(spec=FunctionDataOutputOrm)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_output
        mock_db_session.execute.return_value = mock_result

        retrieved_output = await service.get(db=mock_db_session, accession_id=output_id)

        assert retrieved_output == expected_output
        mock_db_session.execute.assert_awaited_once()

    async def test_get_output_not_found(self, service, mock_db_session):
        """Test retrieving a non-existent output."""
        output_id = uuid7()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        retrieved_output = await service.get(db=mock_db_session, accession_id=output_id)

        assert retrieved_output is None
        mock_db_session.execute.assert_awaited_once()
