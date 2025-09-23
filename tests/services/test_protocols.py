import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock, AsyncMock

from praxis.backend.services.protocols import ProtocolRunService
from praxis.backend.models.orm.protocol import ProtocolRunOrm

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_db_session():
    """Fixture for a mock SQLAlchemy async session."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.scalar_one_or_none = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def protocol_run_service():
    """Fixture for the ProtocolRunService."""
    return ProtocolRunService(ProtocolRunOrm)


from praxis.backend.models.pydantic_internals.protocol import ProtocolRunCreate
from praxis.backend.utils.uuid import uuid7

@pytest.fixture
def valid_protocol_run_create() -> ProtocolRunCreate:
    """Fixture for a valid protocol run creation model."""
    return ProtocolRunCreate(
        name="Test Protocol Run",
        top_level_protocol_definition_accession_id=uuid7(),
    )

from unittest.mock import patch

class TestProtocolRunService:
    """Test suite for the ProtocolRunService."""

    @patch("praxis.backend.services.protocols.select")
    @patch("praxis.backend.services.protocols.joinedload")
    async def test_get_multi(self, mock_joinedload, mock_select, protocol_run_service, mock_db_session):
        """Test getting multiple protocol runs."""
        from praxis.backend.models.pydantic_internals.filters import SearchFilters

        # Mock the select call to return a mock object
        mock_query = MagicMock()
        mock_select.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.order_by.return_value = mock_query

        # Configure the mock for the execute call
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        await protocol_run_service.get_multi(db=mock_db_session, filters=SearchFilters())

        mock_db_session.execute.assert_called_once()

    @patch("praxis.backend.services.protocols.select")
    @patch("praxis.backend.services.protocols.joinedload")
    @patch("praxis.backend.services.protocols.selectinload")
    async def test_get_by_name(self, mock_selectinload, mock_joinedload, mock_select, protocol_run_service, mock_db_session):
        """Test getting a protocol run by name."""
        # Mock the select call to return a mock object
        mock_query = MagicMock()
        mock_select.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query

        # Configure the mock for the execute call
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

        await protocol_run_service.get_by_name(db=mock_db_session, name="test_protocol")

        mock_db_session.execute.assert_called_once()

    @patch("praxis.backend.services.protocols.select")
    async def test_update_protocol_run_status(self, mock_select, protocol_run_service, mock_db_session):
        """Test updating the status of a protocol run."""
        from praxis.backend.models.enums.protocol import ProtocolRunStatusEnum

        # Mock the select call to return a mock object
        mock_query = MagicMock()
        mock_select.return_value = mock_query
        mock_query.filter.return_value = mock_query

        # Configure the mock for the execute call
        mock_result = MagicMock()
        mock_run = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_run
        mock_db_session.execute.return_value = mock_result

        await protocol_run_service.update_protocol_run_status(
            db=mock_db_session,
            protocol_run_accession_id=uuid.uuid4(),
            new_status=ProtocolRunStatusEnum.RUNNING,
        )

        assert mock_run.status == ProtocolRunStatusEnum.RUNNING
