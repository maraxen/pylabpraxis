"""Unit tests for MachineDefinition Pydantic models."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import MachineCategoryEnum
from praxis.backend.models.orm.machine import MachineDefinitionOrm
from praxis.backend.models.pydantic_internals.machine import (
    MachineDefinitionBase,
    MachineDefinitionCreate,
    MachineDefinitionResponse,
    MachineDefinitionUpdate,
)


def test_machine_definition_base_minimal() -> None:
    """Test MachineDefinitionBase with minimal fields."""
    machine_def = MachineDefinitionBase(fqn="test.minimal.Machine")

    # Verify defaults
    assert machine_def.fqn == "test.minimal.Machine"
    assert machine_def.machine_category is None
    assert machine_def.material is None
    assert machine_def.manufacturer is None
    assert machine_def.nominal_volume_ul is None
    assert machine_def.has_deck is None


def test_machine_definition_base_with_all_fields() -> None:
    """Test MachineDefinitionBase with all fields populated."""
    from praxis.backend.utils.uuid import uuid7

    plr_details = {
        "backend": "STAR",
        "num_channels": 8,
    }
    rotation = {"x_deg": 0, "y_deg": 0, "z_deg": 90}
    setup_method = {"method": "setup", "params": {"simulate": True}}
    resource_def_id = uuid7()
    deck_def_id = uuid7()

    machine_def = MachineDefinitionBase(
        fqn="test.full.Machine",
        machine_category=MachineCategoryEnum.LIQUID_HANDLER,
        nominal_volume_ul=1000.0,
        material="stainless_steel",
        manufacturer="Hamilton",
        plr_definition_details_json=plr_details,
        size_x_mm=1600.0,
        size_y_mm=900.0,
        size_z_mm=800.0,
        model="STAR",
        rotation_json=rotation,
        resource_definition_accession_id=resource_def_id,
        has_deck=True,
        deck_definition_accession_id=deck_def_id,
        setup_method_json=setup_method,
    )

    assert machine_def.fqn == "test.full.Machine"
    assert machine_def.machine_category == "LiquidHandler"  # Serialized to string
    assert machine_def.nominal_volume_ul == 1000.0
    assert machine_def.material == "stainless_steel"
    assert machine_def.manufacturer == "Hamilton"
    assert machine_def.plr_definition_details_json == plr_details
    assert machine_def.size_x_mm == 1600.0
    assert machine_def.model == "STAR"
    assert machine_def.rotation_json == rotation
    assert machine_def.has_deck is True
    assert machine_def.setup_method_json == setup_method


def test_machine_definition_create() -> None:
    """Test MachineDefinitionCreate model."""
    machine_def = MachineDefinitionCreate(
        name="test_liquid_handler",
        fqn="test.machine.LiquidHandler",
        machine_category=MachineCategoryEnum.LIQUID_HANDLER,
        manufacturer="Test Corp",
        has_deck=True,
    )

    assert machine_def.name == "test_liquid_handler"
    assert machine_def.fqn == "test.machine.LiquidHandler"
    assert machine_def.machine_category == "LiquidHandler"
    assert machine_def.manufacturer == "Test Corp"
    assert machine_def.has_deck is True


def test_machine_definition_update() -> None:
    """Test MachineDefinitionUpdate model."""
    # Update requires fqn but other fields are optional
    update = MachineDefinitionUpdate(fqn="test.update.Machine")

    assert update.fqn == "test.update.Machine"
    assert update.machine_category is None
    assert update.description is None

    # Can update specific fields
    update_partial = MachineDefinitionUpdate(
        fqn="test.update.Machine2",
        description="Updated description",
        manufacturer="Updated Corp",
        size_x_mm=1700.0,
        machine_category=MachineCategoryEnum.PLATE_READER,
    )

    assert update_partial.fqn == "test.update.Machine2"
    assert update_partial.description == "Updated description"
    assert update_partial.manufacturer == "Updated Corp"
    assert update_partial.size_x_mm == 1700.0
    assert update_partial.machine_category == "PlateReader"  # Serialized to string


def test_machine_definition_response_serialization_to_dict() -> None:
    """Test MachineDefinitionResponse serialization to dict."""
    from praxis.backend.utils.uuid import uuid7

    machine_id = uuid7()
    response = MachineDefinitionResponse(
        accession_id=machine_id,
        name="response_machine",
        fqn="test.response.Machine",
        machine_category=MachineCategoryEnum.LIQUID_HANDLER,
        manufacturer="Test Corp",
        has_deck=True,
    )

    machine_dict = response.model_dump()

    assert machine_dict["accession_id"] == machine_id
    assert machine_dict["name"] == "response_machine"
    assert machine_dict["fqn"] == "test.response.Machine"
    assert machine_dict["machine_category"] == "LiquidHandler"
    assert machine_dict["manufacturer"] == "Test Corp"
    assert machine_dict["has_deck"] is True


def test_machine_definition_response_serialization_to_json() -> None:
    """Test MachineDefinitionResponse serialization to JSON."""
    from praxis.backend.utils.uuid import uuid7

    response = MachineDefinitionResponse(
        accession_id=uuid7(),
        name="json_machine",
        fqn="test.json.Machine",
        machine_category=MachineCategoryEnum.INCUBATOR,
    )

    json_str = response.model_dump_json()

    assert isinstance(json_str, str)
    assert "json_machine" in json_str
    assert "test.json.Machine" in json_str


def test_machine_definition_response_deserialization_from_dict() -> None:
    """Test creating MachineDefinitionResponse from dict."""
    from praxis.backend.utils.uuid import uuid7

    machine_id = uuid7()
    machine_data = {
        "accession_id": machine_id,
        "name": "deserialized_machine",
        "fqn": "test.deserialized.Machine",
        "machine_category": MachineCategoryEnum.SHAKER,
        "manufacturer": "Test Corp",
    }

    response = MachineDefinitionResponse(**machine_data)

    assert response.accession_id == machine_id
    assert response.name == "deserialized_machine"
    assert response.fqn == "test.deserialized.Machine"
    assert response.machine_category == "Shaker"
    assert response.manufacturer == "Test Corp"


def test_machine_definition_response_roundtrip_serialization() -> None:
    """Test MachineDefinitionResponse survives serialization round-trip."""
    from praxis.backend.utils.uuid import uuid7

    original = MachineDefinitionResponse(
        accession_id=uuid7(),
        name="roundtrip_machine",
        fqn="test.roundtrip.Machine",
        machine_category=MachineCategoryEnum.THERMOCYCLER,
        manufacturer="Test Corp",
        size_x_mm=500.0,
        size_y_mm=400.0,
        has_deck=False,
    )

    # Serialize to dict and back
    machine_dict = original.model_dump()
    restored = MachineDefinitionResponse(**machine_dict)

    assert restored.accession_id == original.accession_id
    assert restored.name == original.name
    assert restored.fqn == original.fqn
    assert restored.machine_category == original.machine_category
    assert restored.manufacturer == original.manufacturer
    assert restored.size_x_mm == original.size_x_mm
    assert restored.has_deck == original.has_deck


@pytest.mark.asyncio
async def test_machine_definition_response_from_orm(db_session: AsyncSession) -> None:
    """Test converting MachineDefinitionOrm to MachineDefinitionResponse."""
    from praxis.backend.utils.uuid import uuid7

    plr_details = {"backend": "STAR", "channels": 8}
    rotation = {"x_deg": 0, "y_deg": 0, "z_deg": 0}
    setup_method = {"method": "setup"}

    # Create ORM instance
    orm_machine_def = MachineDefinitionOrm(
        name="orm_test_machine",
        fqn="test.orm.Machine",
        machine_category=MachineCategoryEnum.LIQUID_HANDLER,
        description="Test machine from ORM",
        material="aluminum",
        manufacturer="Test Corp",
        plr_definition_details_json=plr_details,
        size_x_mm=1600.0,
        size_y_mm=900.0,
        size_z_mm=800.0,
        model="TEST-LH",
        rotation_json=rotation,
        plr_category="liquid_handler",
        setup_method_json=setup_method,
    )

    db_session.add(orm_machine_def)
    await db_session.flush()

    # Convert to Pydantic
    response = MachineDefinitionResponse.model_validate(orm_machine_def)

    # Verify conversion
    assert response.accession_id == orm_machine_def.accession_id
    assert response.name == "orm_test_machine"
    assert response.fqn == "test.orm.Machine"
    assert response.machine_category == "LiquidHandler"
    assert response.description == "Test machine from ORM"
    assert response.material == "aluminum"
    assert response.manufacturer == "Test Corp"
    assert response.plr_definition_details_json == plr_details
    assert response.size_x_mm == 1600.0
    assert response.size_y_mm == 900.0
    assert response.size_z_mm == 800.0
    assert response.model == "TEST-LH"
    assert response.rotation_json == rotation
    assert response.plr_category == "liquid_handler"
    assert response.has_deck is None
    assert response.setup_method_json == setup_method


@pytest.mark.asyncio
async def test_machine_definition_response_from_orm_minimal(db_session: AsyncSession) -> None:
    """Test ORM-to-Pydantic conversion with minimal fields."""
    from praxis.backend.utils.uuid import uuid7

    orm_machine_def = MachineDefinitionOrm(
        name="minimal_machine",
        fqn="test.minimal.Machine",
    )

    db_session.add(orm_machine_def)
    await db_session.flush()

    # Convert to Pydantic
    response = MachineDefinitionResponse.model_validate(orm_machine_def)

    # Verify
    assert response.accession_id == orm_machine_def.accession_id
    assert response.name == "minimal_machine"
    assert response.fqn == "test.minimal.Machine"
    assert response.machine_category == "Unknown"  # ORM default
    assert response.description is None


def test_machine_definition_jsonb_validation() -> None:
    """Test JSONB field validation in Pydantic models."""
    plr_details = {
        "backend_class": "STAR",
        "num_channels": 8,
        "channel_spacing_mm": 9.0,
    }
    setup_method = {
        "method_name": "setup_with_config",
        "config_file": "robot_config.yaml",
    }

    machine_def = MachineDefinitionCreate(
        name="jsonb_test",
        fqn="test.jsonb.Machine",
        plr_definition_details_json=plr_details,
        setup_method_json=setup_method,
    )

    assert machine_def.plr_definition_details_json == plr_details
    assert machine_def.plr_definition_details_json["num_channels"] == 8
    assert machine_def.setup_method_json == setup_method


def test_machine_definition_category_types() -> None:
    """Test different machine category enum values."""
    categories = [
        MachineCategoryEnum.LIQUID_HANDLER,
        MachineCategoryEnum.PLATE_READER,
        MachineCategoryEnum.INCUBATOR,
        MachineCategoryEnum.SHAKER,
        MachineCategoryEnum.THERMOCYCLER,
    ]

    for category in categories:
        machine_def = MachineDefinitionCreate(
            name=f"test_{category.value}",
            fqn=f"test.category.{category.value}",
            machine_category=category,
        )
        assert machine_def.machine_category == category.value  # Serialized to string


def test_machine_definition_physical_dimensions() -> None:
    """Test physical dimension fields."""
    machine_def = MachineDefinitionCreate(
        name="dimensioned_machine",
        fqn="test.dimensions.Machine",
        size_x_mm=1600.0,
        size_y_mm=900.0,
        size_z_mm=800.0,
    )

    assert machine_def.size_x_mm == 1600.0
    assert machine_def.size_y_mm == 900.0
    assert machine_def.size_z_mm == 800.0


def test_machine_definition_with_deck_flag() -> None:
    """Test has_deck flag."""
    # Liquid handler with deck
    with_deck = MachineDefinitionCreate(
        name="liquid_handler_with_deck",
        fqn="test.deck.WithDeck",
        machine_category=MachineCategoryEnum.LIQUID_HANDLER,
        has_deck=True,
    )
    assert with_deck.has_deck is True

    # Pump without deck
    without_deck = MachineDefinitionCreate(
        name="pump_without_deck",
        fqn="test.deck.WithoutDeck",
        machine_category=MachineCategoryEnum.PUMP,
        has_deck=False,
    )
    assert without_deck.has_deck is False
