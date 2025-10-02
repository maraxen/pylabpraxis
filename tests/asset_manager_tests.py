import inspect
from typing import Any
from unittest.mock import ANY, MagicMock, patch
import uuid

import pytest

# Classes to test
from praxis.backend.core.asset_manager import AssetAcquisitionError, AssetManager
from praxis.backend.core.protocols.asset_lock_manager import IAssetLockManager
from praxis.backend.services.deck import DeckService
from praxis.backend.services.machine import MachineService
from praxis.backend.services.resource import ResourceService
from praxis.backend.services.resource_type_definition import (
    ResourceTypeDefinitionService,
)


# Enums
from praxis.backend.models.enums import (
    MachineCategoryEnum as PraxisDeviceCategoryEnum,
    MachineStatusEnum,
    ResourceCategoryEnum,
    ResourceStatusEnum,
)
from praxis.backend.models.orm.deck import (
    DeckDefinitionOrm as DeckLayoutOrm,
    DeckPositionDefinitionOrm as DeckSlotOrm,
)
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.resource import ResourceDefinitionOrm, ResourceOrm
from praxis.backend.core.run_context import Deck as ProtocolDeck

# Dependent ORM-like Mocks
ManagedDeviceOrmMock = MagicMock
ResourceOrmMock = MagicMock
ResourceDefinitionOrmMock = MagicMock
AssetRequirementModelMock = MagicMock


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def mock_workcell_runtime():
    m = MagicMock()
    m.initialize_machine.return_value = MagicMock(name="live_mock_machine")
    m.create_or_get_resource.return_value = MagicMock(name="live_mock_resource")
    return m


@pytest.fixture
def mock_deck_service():
    return MagicMock(spec=DeckService)


@pytest.fixture
def mock_machine_service():
    return MagicMock(spec=MachineService)


@pytest.fixture
def mock_resource_service():
    return MagicMock(spec=ResourceService)


@pytest.fixture
def mock_resource_type_definition_service():
    return MagicMock(spec=ResourceTypeDefinitionService)


@pytest.fixture
def mock_asset_lock_manager():
    return MagicMock(spec=IAssetLockManager)


@pytest.fixture
def asset_manager(
    mock_db_session: MagicMock,
    mock_workcell_runtime: MagicMock,
    mock_deck_service: MagicMock,
    mock_machine_service: MagicMock,
    mock_resource_service: MagicMock,
    mock_resource_type_definition_service: MagicMock,
    mock_asset_lock_manager: MagicMock,
):
    return AssetManager(
        db_session=mock_db_session,
        workcell_runtime=mock_workcell_runtime,
        deck_service=mock_deck_service,
        machine_service=mock_machine_service,
        resource_service=mock_resource_service,
        resource_type_definition_service=mock_resource_type_definition_service,
        asset_lock_manager=mock_asset_lock_manager,
    )


@pytest.mark.asyncio
class TestAssetManagerAcquireDevice:
    async def test_acquire_machine_success(
        self,
        asset_manager: AssetManager,
        mock_machine_service: MagicMock,
        mock_workcell_runtime: MagicMock,
        mock_resource_type_definition_service: MagicMock,
    ) -> None:
        mock_resource_type_definition_service.get_by_name.return_value = None
        mock_machine_orm = MachineOrm(
            accession_id=uuid.uuid4(), name="Device1", fqn="SomeDeviceClass"
        )
        mock_machine_service.get_multi.return_value = [mock_machine_orm]
        updated_mock_machine_orm = MachineOrm(
            accession_id=uuid.uuid4(),
            name="Device1",
            fqn="SomeDeviceClass",
            status=MachineStatusEnum.IN_USE,
        )
        mock_machine_service.update_machine_status.return_value = updated_mock_machine_orm

        live_machine, orm_accession_id, dev_type = await asset_manager.acquire_machine(
            protocol_run_accession_id=uuid.uuid4(),
            requested_asset_name_in_protocol="dev_in_proto",
            fqn_constraint="SomeDeviceClass",
        )

        assert mock_machine_service.get_multi.called
        mock_workcell_runtime.initialize_machine.assert_called_once_with(mock_machine_orm)
        assert mock_machine_service.update_machine_status.called
        assert live_machine is not None
        assert orm_accession_id is not None
        assert dev_type == "machine"

    async def test_acquire_machine_no_machine_found(
        self,
        asset_manager: AssetManager,
        mock_machine_service: MagicMock,
        mock_resource_type_definition_service: MagicMock,
    ) -> None:
        mock_machine_service.get_multi.return_value = []
        mock_resource_type_definition_service.get_by_name.return_value = None
        with pytest.raises(AssetAcquisitionError):
            await asset_manager.acquire_machine(
                uuid.uuid4(), "dev", "SomeDeviceClass"
            )

    async def test_acquire_machine_backend_init_fails(
        self,
        asset_manager: AssetManager,
        mock_machine_service: MagicMock,
        mock_workcell_runtime: MagicMock,
        mock_resource_type_definition_service: MagicMock,
    ) -> None:
        mock_resource_type_definition_service.get_by_name.return_value = None
        mock_machine_orm = MachineOrm(
            accession_id=uuid.uuid4(), name="Device1", fqn="SomeDeviceClass"
        )
        mock_machine_service.get_multi.return_value = [mock_machine_orm]
        mock_workcell_runtime.initialize_machine.return_value = None

        with pytest.raises(AssetAcquisitionError):
            await asset_manager.acquire_machine(
                uuid.uuid4(), "dev", "SomeDeviceClass"
            )

    async def test_acquire_machine_db_status_update_fails_after_init(
        self,
        asset_manager: AssetManager,
        mock_machine_service: MagicMock,
        mock_workcell_runtime: MagicMock,
        mock_resource_type_definition_service: MagicMock,
    ) -> None:
        mock_resource_type_definition_service.get_by_name.return_value = None
        mock_machine_orm = MachineOrm(
            accession_id=uuid.uuid4(), name="Device1", fqn="SomeDeviceClass"
        )
        mock_machine_service.get_multi.return_value = [mock_machine_orm]
        mock_machine_service.update_machine_status.return_value = None

        with pytest.raises(AssetAcquisitionError):
            await asset_manager.acquire_machine(
                uuid.uuid4(), "dev", "SomeDeviceClass"
            )