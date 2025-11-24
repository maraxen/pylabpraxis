"""Unit tests for MachineDefinitionOrm."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from praxis.backend.models.orm.machine import MachineDefinitionOrm
from praxis.backend.models.enums import MachineCategoryEnum


@pytest.mark.asyncio
async def test_machine_definition_orm_creation_minimal(db_session: AsyncSession) -> None:
    """Test creating MachineDefinitionOrm with minimal required fields."""
    machine_def = MachineDefinitionOrm(
        name="test_liquid_handler",
        fqn="test.machine.LiquidHandler",
    )
    db_session.add(machine_def)
    await db_session.flush()

    # Verify creation
    assert machine_def.accession_id is not None
    assert machine_def.name == "test_liquid_handler"
    assert machine_def.fqn == "test.machine.LiquidHandler"
    assert machine_def.machine_category == MachineCategoryEnum.UNKNOWN  # Default
    assert machine_def.material is None


@pytest.mark.asyncio
async def test_machine_definition_orm_with_all_fields(db_session: AsyncSession) -> None:
    """Test MachineDefinitionOrm with all fields populated."""
    plr_details = {
        "backend_class": "STAR",
        "module": "pylabrobot.liquid_handling.backends.hamilton",
    }
    rotation = {"x_deg": 0, "y_deg": 0, "z_deg": 0}
    setup_method = {
        "method_name": "setup",
        "params": {"simulate": True}
    }

    machine_def = MachineDefinitionOrm(
        name="hamilton_star",
        fqn="pylabrobot.liquid_handling.backends.hamilton.STAR",
        machine_category=MachineCategoryEnum.LIQUID_HANDLER,
        description="Hamilton STAR liquid handler",
        material="stainless_steel",
        manufacturer="Hamilton",
        plr_definition_details_json=plr_details,
        size_x_mm=1600.0,
        size_y_mm=900.0,
        size_z_mm=800.0,
        model="STAR",
        rotation_json=rotation,
        plr_category="liquid_handler",
        has_deck=True,
        setup_method_json=setup_method,
    )
    db_session.add(machine_def)
    await db_session.flush()

    # Verify all fields
    assert machine_def.name == "hamilton_star"
    assert machine_def.machine_category == MachineCategoryEnum.LIQUID_HANDLER
    assert machine_def.description == "Hamilton STAR liquid handler"
    assert machine_def.material == "stainless_steel"
    assert machine_def.manufacturer == "Hamilton"
    assert machine_def.plr_definition_details_json == plr_details
    assert machine_def.size_x_mm == 1600.0
    assert machine_def.size_y_mm == 900.0
    assert machine_def.size_z_mm == 800.0
    assert machine_def.model == "STAR"
    assert machine_def.rotation_json == rotation
    assert machine_def.plr_category == "liquid_handler"
    assert machine_def.has_deck is True
    assert machine_def.setup_method_json == setup_method


@pytest.mark.asyncio
async def test_machine_definition_orm_persist_to_database(db_session: AsyncSession) -> None:
    """Test full persistence cycle for MachineDefinitionOrm."""
    from praxis.backend.utils.uuid import uuid7

    machine_def_id = uuid7()
    machine_def = MachineDefinitionOrm(
        accession_id=machine_def_id,
        name="persistence_test_machine",
        fqn="test.persistence.Machine",
        machine_category=MachineCategoryEnum.PLATE_READER,
        manufacturer="Test Corp",
    )
    db_session.add(machine_def)
    await db_session.flush()

    # Query back
    result = await db_session.execute(
        select(MachineDefinitionOrm).where(
            MachineDefinitionOrm.accession_id == machine_def_id
        )
    )
    retrieved = result.scalars().first()

    # Verify persistence
    assert retrieved is not None
    assert retrieved.accession_id == machine_def_id
    assert retrieved.name == "persistence_test_machine"
    assert retrieved.fqn == "test.persistence.Machine"
    assert retrieved.machine_category == MachineCategoryEnum.PLATE_READER
    assert retrieved.manufacturer == "Test Corp"


@pytest.mark.asyncio
async def test_machine_definition_orm_unique_fqn_constraint(db_session: AsyncSession) -> None:
    """Test that FQN must be unique."""
    # Create first machine definition
    machine_def1 = MachineDefinitionOrm(
        name="machine_1",
        fqn="test.unique.Machine",
    )
    db_session.add(machine_def1)
    await db_session.flush()

    # Try to create another with same FQN
    machine_def2 = MachineDefinitionOrm(
        name="machine_2",
        fqn="test.unique.Machine",  # Duplicate FQN
    )
    db_session.add(machine_def2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_machine_definition_orm_unique_name_constraint(db_session: AsyncSession) -> None:
    """Test that name must be unique."""
    # Create first machine definition
    machine_def1 = MachineDefinitionOrm(
        name="unique_machine",
        fqn="test.unique.Machine1",
    )
    db_session.add(machine_def1)
    await db_session.flush()

    # Try to create another with same name
    machine_def2 = MachineDefinitionOrm(
        name="unique_machine",  # Duplicate name
        fqn="test.unique.Machine2",
    )
    db_session.add(machine_def2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_machine_definition_orm_machine_categories(db_session: AsyncSession) -> None:
    """Test different machine category types."""
    categories = [
        (MachineCategoryEnum.LIQUID_HANDLER, "liquid_handler"),
        (MachineCategoryEnum.PLATE_READER, "plate_reader"),
        (MachineCategoryEnum.INCUBATOR, "incubator"),
        (MachineCategoryEnum.SHAKER, "shaker"),
        (MachineCategoryEnum.THERMOCYCLER, "thermocycler"),
    ]

    for category, name_suffix in categories:
        machine_def = MachineDefinitionOrm(
            name=f"test_{name_suffix}",
            fqn=f"test.machine.{category.value}",
            machine_category=category,
        )
        db_session.add(machine_def)
        await db_session.flush()

        # Verify category was set correctly
        assert machine_def.machine_category == category


@pytest.mark.asyncio
async def test_machine_definition_orm_jsonb_fields(db_session: AsyncSession) -> None:
    """Test JSONB field handling."""
    plr_details = {
        "backend": "STAR",
        "channels": 8,
        "min_volume_ul": 0.5,
        "max_volume_ul": 1000.0,
    }
    rotation = {"x_deg": 0, "y_deg": 90, "z_deg": 180}
    setup_method = {
        "method": "setup_with_robot_config",
        "config_path": "/path/to/config.yaml"
    }

    machine_def = MachineDefinitionOrm(
        name="jsonb_test_machine",
        fqn="test.jsonb.Machine",
        plr_definition_details_json=plr_details,
        rotation_json=rotation,
        setup_method_json=setup_method,
    )
    db_session.add(machine_def)
    await db_session.flush()

    # Query back to verify JSONB storage
    result = await db_session.execute(
        select(MachineDefinitionOrm).where(
            MachineDefinitionOrm.name == "jsonb_test_machine"
        )
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.plr_definition_details_json == plr_details
    assert retrieved.plr_definition_details_json["channels"] == 8
    assert retrieved.rotation_json == rotation
    assert retrieved.rotation_json["y_deg"] == 90
    assert retrieved.setup_method_json == setup_method
    assert retrieved.setup_method_json["method"] == "setup_with_robot_config"


@pytest.mark.asyncio
async def test_machine_definition_orm_dimensions(db_session: AsyncSession) -> None:
    """Test physical dimension fields."""
    machine_def = MachineDefinitionOrm(
        name="dimensioned_machine",
        fqn="test.dimensions.Machine",
        size_x_mm=1600.0,
        size_y_mm=900.0,
        size_z_mm=800.0,
    )
    db_session.add(machine_def)
    await db_session.flush()

    # Query back
    result = await db_session.execute(
        select(MachineDefinitionOrm).where(
            MachineDefinitionOrm.name == "dimensioned_machine"
        )
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.size_x_mm == 1600.0
    assert retrieved.size_y_mm == 900.0
    assert retrieved.size_z_mm == 800.0


@pytest.mark.asyncio
async def test_machine_definition_orm_with_deck_flag(db_session: AsyncSession) -> None:
    """Test has_deck flag for machines with/without decks."""
    # Machine with deck (liquid handler)
    with_deck = MachineDefinitionOrm(
        name="machine_with_deck",
        fqn="test.deck.MachineWithDeck",
        machine_category=MachineCategoryEnum.LIQUID_HANDLER,
        has_deck=True,
    )
    db_session.add(with_deck)
    await db_session.flush()

    # Machine without deck (pump)
    without_deck = MachineDefinitionOrm(
        name="machine_without_deck",
        fqn="test.deck.MachineWithoutDeck",
        machine_category=MachineCategoryEnum.PUMP,
        has_deck=False,
    )
    db_session.add(without_deck)
    await db_session.flush()

    # Verify
    assert with_deck.has_deck is True
    assert without_deck.has_deck is False
