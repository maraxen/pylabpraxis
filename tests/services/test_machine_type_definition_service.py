from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.machine import MachineDefinitionOrm
from praxis.backend.services.machine_type_definition import MachineTypeDefinitionService


@pytest.fixture
def machine_type_definition_service(db_session: AsyncSession) -> MachineTypeDefinitionService:
    return MachineTypeDefinitionService(db_session)

class MockMachineClass:

    """Mock Machine Class."""


@pytest.mark.asyncio
async def test_discover_and_synchronize_machine_types(
    db_session: AsyncSession,
    machine_type_definition_service: MachineTypeDefinitionService,
) -> None:
    """Test synchronization of machine types."""
    # Setup mock
    mock_classes = {
        "test.machine.MockMachine": MockMachineClass,
    }

    with patch("praxis.backend.services.machine_type_definition.get_machine_classes", return_value=mock_classes):
        # Run sync
        synced = await machine_type_definition_service.discover_and_synchronize_type_definitions()

        assert len(synced) == 1
        assert synced[0].fqn == "test.machine.MockMachine"
        assert synced[0].name == "MockMachineClass"

        # Verify in DB
        result = await db_session.execute(select(MachineDefinitionOrm).filter_by(fqn="test.machine.MockMachine"))
        db_obj = result.scalar_one()
        assert db_obj is not None

        # Run sync again (update)
        MockMachineClass.__doc__ = "Updated doc"
        synced_update = await machine_type_definition_service.discover_and_synchronize_type_definitions()
        assert len(synced_update) == 1
        assert synced_update[0].description == "Updated doc"
