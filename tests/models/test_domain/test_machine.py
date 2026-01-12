"""Unit tests for MachineOrm model."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import AssetType, MachineCategoryEnum, MachineStatusEnum
from praxis.backend.models.orm.machine import MachineOrm


@pytest.mark.asyncio
async def test_machine_orm_creation_with_defaults(db_session: AsyncSession) -> None:
    """Test creating a MachineOrm with default values."""
    from praxis.backend.utils.uuid import uuid7

    # Create a machine with only required fields
    machine_id = uuid7()
    machine = MachineOrm(
        name="test_machine",
        fqn="test.machine.Fqn",
        asset_type=AssetType.MACHINE,  # Must set explicitly for polymorphic identity
    )
    machine.accession_id = machine_id

    # Verify defaults are set
    assert machine.accession_id == machine_id
    assert machine.name == "test_machine"
    assert machine.fqn == "test.machine.Fqn"
    assert machine.asset_type == AssetType.MACHINE
    assert machine.status == MachineStatusEnum.OFFLINE
    assert machine.machine_category == MachineCategoryEnum.UNKNOWN
    assert machine.description is None
    assert machine.manufacturer is None
    assert machine.model is None
    assert machine.serial_number is None
    assert machine.connection_info is None
    assert machine.workcell_accession_id is None


@pytest.mark.asyncio
async def test_machine_orm_persist_to_database(db_session: AsyncSession) -> None:
    """Test that a MachineOrm can be persisted to the database."""
    from praxis.backend.utils.uuid import uuid7

    machine_id = uuid7()
    machine = MachineOrm(
        name="test_persistence",
        fqn="test.persistence.Machine",
        asset_type=AssetType.MACHINE,
        description="A test machine",
        manufacturer="Test Manufacturer",
        model="Model X",
        status=MachineStatusEnum.AVAILABLE,  # Changed from ONLINE
        machine_category=MachineCategoryEnum.LIQUID_HANDLER,
    )
    machine.accession_id = machine_id

    # Add to session and flush
    db_session.add(machine)
    await db_session.flush()

    # Query back from database
    result = await db_session.execute(
        select(MachineOrm).where(MachineOrm.accession_id == machine_id),
    )
    retrieved = result.scalars().first()

    # Verify persistence
    assert retrieved is not None
    assert retrieved.accession_id == machine_id
    assert retrieved.name == "test_persistence"
    assert retrieved.fqn == "test.persistence.Machine"
    assert retrieved.description == "A test machine"
    assert retrieved.manufacturer == "Test Manufacturer"
    assert retrieved.model == "Model X"
    assert retrieved.status == MachineStatusEnum.AVAILABLE
    assert retrieved.machine_category == MachineCategoryEnum.LIQUID_HANDLER


@pytest.mark.asyncio
async def test_machine_orm_unique_name_constraint(db_session: AsyncSession) -> None:
    """Test that machine names must be unique."""
    from sqlalchemy.exc import IntegrityError

    from praxis.backend.utils.uuid import uuid7

    # Create first machine
    machine1 = MachineOrm(
        name="unique_machine",
        fqn="test.machine.1",
        asset_type=AssetType.MACHINE,
    )
    machine1.accession_id = uuid7()
    db_session.add(machine1)
    await db_session.flush()

    # Try to create another with same name
    machine2 = MachineOrm(
        name="unique_machine",  # Duplicate name
        fqn="test.machine.2",
        asset_type=AssetType.MACHINE,
    )
    machine2.accession_id = uuid7()
    db_session.add(machine2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_machine_orm_unique_serial_number(db_session: AsyncSession) -> None:
    """Test that machine serial numbers must be unique."""
    from sqlalchemy.exc import IntegrityError

    from praxis.backend.utils.uuid import uuid7

    # Create first machine with serial number
    machine1 = MachineOrm(
        name="machine1",
        fqn="test.machine.1",
        asset_type=AssetType.MACHINE,
        serial_number="SN123456",
    )
    machine1.accession_id = uuid7()
    db_session.add(machine1)
    await db_session.flush()

    # Try to create another with same serial number
    machine2 = MachineOrm(
        name="machine2",
        fqn="test.machine.2",
        asset_type=AssetType.MACHINE,
        serial_number="SN123456",  # Duplicate serial
    )
    machine2.accession_id = uuid7()
    db_session.add(machine2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_machine_orm_with_workcell_relationship(db_session: AsyncSession) -> None:
    """Test creating a machine with a workcell relationship."""
    from praxis.backend.models.orm.workcell import WorkcellOrm
    from praxis.backend.utils.uuid import uuid7

    # Create a workcell first
    workcell_id = uuid7()
    workcell = WorkcellOrm(
        name="test_workcell",
    )
    workcell.accession_id = workcell_id
    db_session.add(workcell)
    await db_session.flush()

    # Create a machine and set workcell via attribute (not constructor)
    machine_id = uuid7()
    machine = MachineOrm(
        name="test_machine_in_workcell",
        fqn="test.machine.InWorkcell",
        asset_type=AssetType.MACHINE,
    )
    machine.accession_id = machine_id
    # Set workcell FK after instantiation
    machine.workcell = workcell

    db_session.add(machine)
    await db_session.flush()

    # Query back and verify relationship
    result = await db_session.execute(
        select(MachineOrm).where(MachineOrm.accession_id == machine_id),
    )
    retrieved_machine = result.scalars().first()

    assert retrieved_machine is not None
    assert retrieved_machine.workcell_accession_id == workcell_id


@pytest.mark.asyncio
async def test_machine_orm_status_enum_values(db_session: AsyncSession) -> None:
    """Test that machine status enum values are stored correctly."""
    from praxis.backend.utils.uuid import uuid7

    # Test each status
    statuses = [
        MachineStatusEnum.AVAILABLE,  # Changed from ONLINE
        MachineStatusEnum.OFFLINE,
        MachineStatusEnum.ERROR,
        MachineStatusEnum.MAINTENANCE,
    ]

    for status in statuses:
        machine = MachineOrm(
            name=f"machine_{status.value}",
            fqn=f"test.machine.{status.value}",
            asset_type=AssetType.MACHINE,
            status=status,
        )
        machine.accession_id = uuid7()
        db_session.add(machine)
        await db_session.flush()

        # Verify status was set correctly
        assert machine.status == status


@pytest.mark.asyncio
async def test_machine_orm_category_enum_values(db_session: AsyncSession) -> None:
    """Test that machine category enum values are stored correctly."""
    from praxis.backend.utils.uuid import uuid7

    # Test a few key categories
    categories = [
        MachineCategoryEnum.LIQUID_HANDLER,
        MachineCategoryEnum.PLATE_READER,
        MachineCategoryEnum.CENTRIFUGE,
        MachineCategoryEnum.UNKNOWN,
    ]

    for category in categories:
        machine = MachineOrm(
            name=f"machine_{category.value}",
            fqn=f"test.machine.{category.value}",
            asset_type=AssetType.MACHINE,
            machine_category=category,
        )
        machine.accession_id = uuid7()
        db_session.add(machine)
        await db_session.flush()

        # Verify category was set correctly
        assert machine.machine_category == category


@pytest.mark.asyncio
async def test_machine_orm_connection_info_json(db_session: AsyncSession) -> None:
    """Test that machine connection_info JSONB field works correctly."""
    from praxis.backend.utils.uuid import uuid7

    connection_data = {
        "backend": "hamilton",
        "address": "192.168.1.100",
        "port": 8080,
        "protocol": "http",
    }

    machine = MachineOrm(
        name="machine_with_connection",
        fqn="test.machine.WithConnection",
        asset_type=AssetType.MACHINE,
        connection_info=connection_data,
    )
    machine.accession_id = uuid7()

    db_session.add(machine)
    await db_session.flush()

    # Verify JSON was stored correctly
    assert machine.connection_info == connection_data
    assert machine.connection_info["backend"] == "hamilton"
    assert machine.connection_info["port"] == 8080
