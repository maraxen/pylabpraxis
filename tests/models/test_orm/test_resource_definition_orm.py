"""Unit tests for ResourceDefinitionOrm."""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.resource import ResourceDefinitionOrm


@pytest.mark.asyncio
async def test_resource_definition_orm_creation_minimal(db_session: AsyncSession) -> None:
    """Test creating ResourceDefinitionOrm with minimal required fields."""
    resource_def = ResourceDefinitionOrm(
        name="test_plate",
        fqn="test.plate.CorningPlate96",
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Verify creation
    assert resource_def.accession_id is not None
    assert resource_def.name == "test_plate"
    assert resource_def.fqn == "test.plate.CorningPlate96"
    assert resource_def.is_consumable is False  # Default
    assert resource_def.resource_type is None


@pytest.mark.asyncio
async def test_resource_definition_orm_with_all_fields(db_session: AsyncSession) -> None:
    """Test ResourceDefinitionOrm with all fields populated."""
    plr_details = {
        "class": "Plate_96_Well",
        "module": "pylabrobot.resources.corning_costar",
    }
    rotation = {"x_deg": 0, "y_deg": 0, "z_deg": 90}

    resource_def = ResourceDefinitionOrm(
        name="corning_96_wellplate",
        fqn="pylabrobot.resources.corning_costar.Costar_96_CorningWellPlate_360uL_Vb",
        resource_type="plate",
        description="96-well plate from Corning",
        is_consumable=True,
        nominal_volume_ul=360.0,
        material="polypropylene",
        manufacturer="Corning",
        plr_definition_details_json=plr_details,
        size_x_mm=127.76,
        size_y_mm=85.48,
        size_z_mm=14.35,
        model="3650",
        rotation_json=rotation,
        ordering="Corning Cat #3650",
        plr_category="plate",
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Verify all fields
    assert resource_def.name == "corning_96_wellplate"
    assert resource_def.resource_type == "plate"
    assert resource_def.is_consumable is True
    assert resource_def.nominal_volume_ul == 360.0
    assert resource_def.material == "polypropylene"
    assert resource_def.manufacturer == "Corning"
    assert resource_def.plr_definition_details_json == plr_details
    assert resource_def.size_x_mm == 127.76
    assert resource_def.size_y_mm == 85.48
    assert resource_def.size_z_mm == 14.35
    assert resource_def.model == "3650"
    assert resource_def.rotation_json == rotation
    assert resource_def.ordering == "Corning Cat #3650"
    assert resource_def.plr_category == "plate"


@pytest.mark.asyncio
async def test_resource_definition_orm_persist_to_database(db_session: AsyncSession) -> None:
    """Test full persistence cycle for ResourceDefinitionOrm."""
    from praxis.backend.utils.uuid import uuid7

    resource_def_id = uuid7()
    resource_def = ResourceDefinitionOrm(
        accession_id=resource_def_id,
        name="persistence_test_plate",
        fqn="test.persistence.Plate",
        resource_type="plate",
        is_consumable=True,
        nominal_volume_ul=200.0,
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Query back
    result = await db_session.execute(
        select(ResourceDefinitionOrm).where(
            ResourceDefinitionOrm.accession_id == resource_def_id,
        ),
    )
    retrieved = result.scalars().first()

    # Verify persistence
    assert retrieved is not None
    assert retrieved.accession_id == resource_def_id
    assert retrieved.name == "persistence_test_plate"
    assert retrieved.fqn == "test.persistence.Plate"
    assert retrieved.resource_type == "plate"
    assert retrieved.is_consumable is True
    assert retrieved.nominal_volume_ul == 200.0


@pytest.mark.asyncio
async def test_resource_definition_orm_unique_fqn_constraint(db_session: AsyncSession) -> None:
    """Test that FQN must be unique."""
    # Create first resource definition
    resource_def1 = ResourceDefinitionOrm(
        name="plate_1",
        fqn="test.unique.Plate",
    )
    db_session.add(resource_def1)
    await db_session.flush()

    # Try to create another with same FQN
    resource_def2 = ResourceDefinitionOrm(
        name="plate_2",
        fqn="test.unique.Plate",  # Duplicate FQN
    )
    db_session.add(resource_def2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_resource_definition_orm_unique_name_constraint(db_session: AsyncSession) -> None:
    """Test that name must be unique."""
    # Create first resource definition
    resource_def1 = ResourceDefinitionOrm(
        name="unique_plate",
        fqn="test.unique.Plate1",
    )
    db_session.add(resource_def1)
    await db_session.flush()

    # Try to create another with same name
    resource_def2 = ResourceDefinitionOrm(
        name="unique_plate",  # Duplicate name
        fqn="test.unique.Plate2",
    )
    db_session.add(resource_def2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_resource_definition_orm_jsonb_fields(db_session: AsyncSession) -> None:
    """Test JSONB field handling."""
    plr_details = {
        "num_items_x": 12,
        "num_items_y": 8,
        "well_size_x": 9.0,
        "well_size_y": 9.0,
    }
    rotation = {"x_deg": 0, "y_deg": 0, "z_deg": 180}

    resource_def = ResourceDefinitionOrm(
        name="jsonb_test_plate",
        fqn="test.jsonb.Plate",
        plr_definition_details_json=plr_details,
        rotation_json=rotation,
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Query back to verify JSONB storage
    result = await db_session.execute(
        select(ResourceDefinitionOrm).where(
            ResourceDefinitionOrm.name == "jsonb_test_plate",
        ),
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.plr_definition_details_json == plr_details
    assert retrieved.plr_definition_details_json["num_items_x"] == 12
    assert retrieved.rotation_json == rotation
    assert retrieved.rotation_json["z_deg"] == 180


@pytest.mark.asyncio
async def test_resource_definition_orm_consumable_flag(db_session: AsyncSession) -> None:
    """Test is_consumable flag for different resource types."""
    # Consumable resource (tips, tubes)
    consumable = ResourceDefinitionOrm(
        name="tips_200ul",
        fqn="test.tips.Tips200uL",
        resource_type="tips",
        is_consumable=True,
    )
    db_session.add(consumable)
    await db_session.flush()

    # Non-consumable resource (plate carrier)
    non_consumable = ResourceDefinitionOrm(
        name="plate_carrier",
        fqn="test.carrier.PlateCarrier",
        resource_type="carrier",
        is_consumable=False,
    )
    db_session.add(non_consumable)
    await db_session.flush()

    # Verify
    assert consumable.is_consumable is True
    assert non_consumable.is_consumable is False


@pytest.mark.asyncio
async def test_resource_definition_orm_dimensions(db_session: AsyncSession) -> None:
    """Test physical dimension fields."""
    resource_def = ResourceDefinitionOrm(
        name="dimensioned_plate",
        fqn="test.dimensions.Plate",
        size_x_mm=127.76,
        size_y_mm=85.48,
        size_z_mm=14.35,
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Query back
    result = await db_session.execute(
        select(ResourceDefinitionOrm).where(
            ResourceDefinitionOrm.name == "dimensioned_plate",
        ),
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.size_x_mm == 127.76
    assert retrieved.size_y_mm == 85.48
    assert retrieved.size_z_mm == 14.35


@pytest.mark.asyncio
async def test_resource_definition_orm_with_volume(db_session: AsyncSession) -> None:
    """Test nominal_volume_ul field for volumetric resources."""
    resource_def = ResourceDefinitionOrm(
        name="tube_1_5ml",
        fqn="test.tube.Tube1500uL",
        resource_type="tube",
        nominal_volume_ul=1500.0,
        is_consumable=True,
    )
    db_session.add(resource_def)
    await db_session.flush()

    assert resource_def.nominal_volume_ul == 1500.0
    assert resource_def.resource_type == "tube"
