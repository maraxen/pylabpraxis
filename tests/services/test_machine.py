import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums.asset import AssetType
from praxis.backend.models.orm.machine import MachineOrm, MachineStatusEnum
from praxis.backend.models.pydantic_internals.machine import MachineCreate, MachineUpdate
from praxis.backend.services.machine import MachineService
from praxis.backend.services.utils.crud_base import CRUDBase


@pytest.mark.asyncio
class TestMachineService:
    """Test suite for the machine data service layer."""

    @pytest.fixture
    def machine_service(self) -> MachineService:
        """Return a MachineService instance."""
        return MachineService(MachineOrm)

    @pytest.fixture
    def db_session(self) -> AsyncMock:
        """Return a mock AsyncSession."""
        db = AsyncMock(spec=AsyncSession)
        result_mock = MagicMock()
        db.execute.return_value = result_mock
        return db

    @patch("praxis.backend.services.machine._create_or_link_resource_counterpart_for_machine")
    @patch.object(CRUDBase, "create")
    async def test_create_machine_simple(
        self, mock_crud_create, mock_link_resource, machine_service, db_session
    ):
        """Test successful creation of a machine."""
        machine_id = uuid.UUID("018f5be1-7498-7245-8e77-336546a78f21")  # Valid UUIDv7
        machine_create = MachineCreate(
            name="Test Machine",
            fqn="test.fqn",
            asset_type=AssetType.MACHINE,
            accession_id=machine_id,
        )
        db_session.execute.return_value.scalar_one_or_none.return_value = None
        mock_crud_create.return_value = MagicMock(spec=MachineOrm, accession_id=machine_id)

        created_machine = await machine_service.create(db_session, obj_in=machine_create)

        db_session.execute.assert_called_once()
        mock_crud_create.assert_called_once()
        mock_link_resource.assert_called_once()
        assert created_machine.accession_id == machine_id

    async def test_create_machine_duplicate_name(self, machine_service, db_session):
        """Test creation fails with a duplicate name."""
        machine_id = uuid.UUID("018f5be1-7498-7245-8e77-336546a78f21")  # Valid UUIDv7
        machine_create = MachineCreate(
            name="Test Machine",
            fqn="test.fqn",
            asset_type=AssetType.MACHINE,
            accession_id=machine_id,
        )
        db_session.execute.return_value.scalar_one_or_none.return_value = MagicMock(
            spec=MachineOrm
        )

        with pytest.raises(ValueError, match="already exists"):
            await machine_service.create(db_session, obj_in=machine_create)

    async def test_read_machine(self, machine_service, db_session):
        """Test successful retrieval of a machine."""
        machine_id = uuid.uuid4()
        mock_orm = MagicMock(spec=MachineOrm)
        db_session.execute.return_value.scalars.return_value.first.return_value = mock_orm

        machine = await machine_service.get(db_session, accession_id=machine_id)

        db_session.execute.assert_called_once()
        assert machine is mock_orm

    async def test_read_non_existent_machine(self, machine_service, db_session):
        """Test retrieval of a non-existent machine returns None."""
        db_session.execute.return_value.scalars.return_value.first.return_value = None

        machine = await machine_service.get(db_session, accession_id=uuid.uuid4())

        assert machine is None

    @patch("praxis.backend.services.machine.synchronize_machine_resource_names")
    @patch.object(CRUDBase, "update")
    async def test_update_machine(self, mock_crud_update, mock_sync_names, machine_service, db_session):
        """Test successful update of a machine."""
        db_obj = MagicMock(spec=MachineOrm, name="Old Name")
        update_data = MachineUpdate(name="New Name", asset_type=AssetType.MACHINE)

        db_session.execute.return_value.scalar_one_or_none.return_value = None
        mock_crud_update.return_value = db_obj

        updated_machine = await machine_service.update(
            db_session, db_obj=db_obj, obj_in=update_data
        )

        mock_sync_names.assert_called_once()
        mock_crud_update.assert_called_once()
        assert updated_machine is db_obj

    async def test_delete_machine(self, machine_service, db_session):
        """Test successful deletion of a machine."""
        machine_id = uuid.uuid4()
        mock_orm = MagicMock(spec=MachineOrm)
        db_session.execute.return_value.scalars.return_value.first.return_value = mock_orm

        deleted_machine = await machine_service.remove(db_session, accession_id=machine_id)

        db_session.execute.assert_called_once()
        db_session.delete.assert_called_once_with(mock_orm)
        assert deleted_machine is mock_orm

    async def test_delete_non_existent_machine(self, machine_service, db_session):
        """Test deletion of a non-existent machine."""
        db_session.execute.return_value.scalars.return_value.first.return_value = None

        deleted_machine = await machine_service.remove(
            db_session, accession_id=uuid.uuid4()
        )

        db_session.delete.assert_not_called()
        assert deleted_machine is None

    async def test_update_machine_status(self, machine_service, db_session):
        """Test successfully updating a machine's status."""
        machine_id = uuid.uuid4()
        mock_orm = MagicMock(spec=MachineOrm, status=MachineStatusEnum.AVAILABLE)
        db_session.execute.return_value.scalars.return_value.first.return_value = mock_orm

        updated = await machine_service.update_machine_status(
            db=db_session,
            machine_accession_id=machine_id,
            new_status=MachineStatusEnum.IN_USE,
        )

        db_session.flush.assert_called_once()
        db_session.refresh.assert_called_once_with(mock_orm)
        assert updated.status == MachineStatusEnum.IN_USE

    async def test_update_status_of_non_existent_machine(self, machine_service, db_session):
        """Test updating the status of a non-existent machine returns None."""
        db_session.execute.return_value.scalars.return_value.first.return_value = None

        result = await machine_service.update_machine_status(
            db=db_session,
            machine_accession_id=uuid.uuid4(),
            new_status=MachineStatusEnum.AVAILABLE,
        )
        assert result is None
        db_session.flush.assert_not_called()
