"""Unit tests for ResourceDefinition Pydantic models."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.pydantic_internals.resource import (
    ResourceDefinitionBase,
    ResourceDefinitionCreate,
    ResourceDefinitionUpdate,
    ResourceDefinitionResponse,
)
from praxis.backend.models.orm.resource import ResourceDefinitionOrm


def test_resource_definition_base_minimal() -> None:
    """Test ResourceDefinitionBase with minimal fields."""
    resource_def = ResourceDefinitionBase()

    # Verify defaults
    assert resource_def.resource_type is None
    assert resource_def.description is None
    assert resource_def.is_consumable is True  # Default
    assert resource_def.nominal_volume_ul is None
    assert resource_def.material is None
    assert resource_def.manufacturer is None


def test_resource_definition_base_with_all_fields() -> None:
    """Test ResourceDefinitionBase with all fields populated."""
    plr_details = {
        "num_items_x": 12,
        "num_items_y": 8,
    }
    rotation = {"x_deg": 0, "y_deg": 0, "z_deg": 90}

    resource_def = ResourceDefinitionBase(
        resource_type="plate",
        description="96-well microplate",
        is_consumable=True,
        nominal_volume_ul=200.0,
        material="polystyrene",
        manufacturer="Corning",
        plr_definition_details_json=plr_details,
        size_x_mm=127.76,
        size_y_mm=85.48,
        size_z_mm=14.35,
        model="3650",
        plr_category="plate",
        rotation_json=rotation,
        ordering="Cat #3650",
    )

    assert resource_def.resource_type == "plate"
    assert resource_def.description == "96-well microplate"
    assert resource_def.is_consumable is True
    assert resource_def.nominal_volume_ul == 200.0
    assert resource_def.material == "polystyrene"
    assert resource_def.manufacturer == "Corning"
    assert resource_def.plr_definition_details_json == plr_details
    assert resource_def.size_x_mm == 127.76
    assert resource_def.model == "3650"
    assert resource_def.rotation_json == rotation


def test_resource_definition_create() -> None:
    """Test ResourceDefinitionCreate model."""
    resource_def = ResourceDefinitionCreate(
        name="test_plate",
        fqn="test.plate.TestPlate",
        resource_type="plate",
        is_consumable=True,
        nominal_volume_ul=300.0,
    )

    assert resource_def.name == "test_plate"
    assert resource_def.fqn == "test.plate.TestPlate"
    assert resource_def.resource_type == "plate"
    assert resource_def.is_consumable is True
    assert resource_def.nominal_volume_ul == 300.0


def test_resource_definition_update() -> None:
    """Test ResourceDefinitionUpdate model."""
    # Update requires fqn but other fields are optional
    update = ResourceDefinitionUpdate(fqn="test.update.Plate")

    assert update.fqn == "test.update.Plate"
    assert update.resource_type is None
    assert update.description is None

    # Can update specific fields
    update_partial = ResourceDefinitionUpdate(
        fqn="test.update.Plate2",
        description="Updated description",
        material="polypropylene",
        size_x_mm=130.0,
    )

    assert update_partial.fqn == "test.update.Plate2"
    assert update_partial.description == "Updated description"
    assert update_partial.material == "polypropylene"
    assert update_partial.size_x_mm == 130.0


def test_resource_definition_response_serialization_to_dict() -> None:
    """Test ResourceDefinitionResponse serialization to dict."""
    from praxis.backend.utils.uuid import uuid7

    resource_id = uuid7()
    response = ResourceDefinitionResponse(
        accession_id=resource_id,
        name="response_plate",
        fqn="test.response.Plate",
        resource_type="plate",
        is_consumable=True,
        nominal_volume_ul=200.0,
        material="polystyrene",
    )

    resource_dict = response.model_dump()

    assert resource_dict["accession_id"] == resource_id
    assert resource_dict["name"] == "response_plate"
    assert resource_dict["fqn"] == "test.response.Plate"
    assert resource_dict["resource_type"] == "plate"
    assert resource_dict["is_consumable"] is True
    assert resource_dict["nominal_volume_ul"] == 200.0
    assert resource_dict["material"] == "polystyrene"


def test_resource_definition_response_serialization_to_json() -> None:
    """Test ResourceDefinitionResponse serialization to JSON."""
    from praxis.backend.utils.uuid import uuid7

    response = ResourceDefinitionResponse(
        accession_id=uuid7(),
        name="json_plate",
        fqn="test.json.Plate",
        resource_type="plate",
    )

    json_str = response.model_dump_json()

    assert isinstance(json_str, str)
    assert "json_plate" in json_str
    assert "test.json.Plate" in json_str


def test_resource_definition_response_deserialization_from_dict() -> None:
    """Test creating ResourceDefinitionResponse from dict."""
    from praxis.backend.utils.uuid import uuid7

    resource_id = uuid7()
    resource_data = {
        "accession_id": resource_id,
        "name": "deserialized_plate",
        "fqn": "test.deserialized.Plate",
        "resource_type": "plate",
        "is_consumable": True,
        "nominal_volume_ul": 250.0,
    }

    response = ResourceDefinitionResponse(**resource_data)

    assert response.accession_id == resource_id
    assert response.name == "deserialized_plate"
    assert response.fqn == "test.deserialized.Plate"
    assert response.resource_type == "plate"
    assert response.nominal_volume_ul == 250.0


def test_resource_definition_response_roundtrip_serialization() -> None:
    """Test ResourceDefinitionResponse survives serialization round-trip."""
    from praxis.backend.utils.uuid import uuid7

    original = ResourceDefinitionResponse(
        accession_id=uuid7(),
        name="roundtrip_plate",
        fqn="test.roundtrip.Plate",
        resource_type="plate",
        is_consumable=True,
        nominal_volume_ul=300.0,
        size_x_mm=127.76,
        size_y_mm=85.48,
    )

    # Serialize to dict and back
    resource_dict = original.model_dump()
    restored = ResourceDefinitionResponse(**resource_dict)

    assert restored.accession_id == original.accession_id
    assert restored.name == original.name
    assert restored.fqn == original.fqn
    assert restored.resource_type == original.resource_type
    assert restored.nominal_volume_ul == original.nominal_volume_ul
    assert restored.size_x_mm == original.size_x_mm


@pytest.mark.asyncio
async def test_resource_definition_response_from_orm(db_session: AsyncSession) -> None:
    """Test converting ResourceDefinitionOrm to ResourceDefinitionResponse."""
    from praxis.backend.utils.uuid import uuid7

    plr_details = {"num_items": 96}
    rotation = {"x_deg": 0, "y_deg": 0, "z_deg": 0}

    # Create ORM instance
    resource_id = uuid7()
    orm_resource_def = ResourceDefinitionOrm(
        name="orm_test_plate",
        fqn="test.orm.Plate",
        resource_type="plate",
        description="Test plate from ORM",
        is_consumable=True,
        nominal_volume_ul=200.0,
        material="polystyrene",
        manufacturer="Test Corp",
        plr_definition_details_json=plr_details,
        size_x_mm=127.76,
        size_y_mm=85.48,
        size_z_mm=14.35,
        model="TEST-96",
        rotation_json=rotation,
        plr_category="plate",
    )
    orm_resource_def.accession_id = resource_id
    db_session.add(orm_resource_def)
    await db_session.flush()

    # Convert to Pydantic
    response = ResourceDefinitionResponse.model_validate(orm_resource_def)

    # Verify conversion
    assert response.accession_id == resource_id
    assert response.name == "orm_test_plate"
    assert response.fqn == "test.orm.Plate"
    assert response.resource_type == "plate"
    assert response.description == "Test plate from ORM"
    assert response.is_consumable is True
    assert response.nominal_volume_ul == 200.0
    assert response.material == "polystyrene"
    assert response.manufacturer == "Test Corp"
    assert response.plr_definition_details_json == plr_details
    assert response.size_x_mm == 127.76
    assert response.size_y_mm == 85.48
    assert response.size_z_mm == 14.35
    assert response.model == "TEST-96"
    assert response.rotation_json == rotation
    assert response.plr_category == "plate"


@pytest.mark.asyncio
async def test_resource_definition_response_from_orm_minimal(db_session: AsyncSession) -> None:
    """Test ORM-to-Pydantic conversion with minimal fields."""
    from praxis.backend.utils.uuid import uuid7

    resource_id = uuid7()
    orm_resource_def = ResourceDefinitionOrm(
        name="minimal_plate",
        fqn="test.minimal.Plate",
    )
    orm_resource_def.accession_id = resource_id

    db_session.add(orm_resource_def)
    await db_session.flush()

    # Convert to Pydantic
    response = ResourceDefinitionResponse.model_validate(orm_resource_def)

    # Verify
    assert response.accession_id == resource_id
    assert response.name == "minimal_plate"
    assert response.fqn == "test.minimal.Plate"
    assert response.resource_type is None
    assert response.description is None
    assert response.is_consumable is False  # ORM default


def test_resource_definition_jsonb_validation() -> None:
    """Test JSONB field validation in Pydantic models."""
    plr_details = {
        "num_items_x": 12,
        "num_items_y": 8,
        "well_spacing_x": 9.0,
        "well_spacing_y": 9.0,
    }

    resource_def = ResourceDefinitionCreate(
        name="jsonb_test",
        fqn="test.jsonb.Plate",
        plr_definition_details_json=plr_details,
    )

    assert resource_def.plr_definition_details_json == plr_details
    assert resource_def.plr_definition_details_json["num_items_x"] == 12


def test_resource_definition_consumable_types() -> None:
    """Test is_consumable flag for different resource types."""
    # Tips - consumable
    tips = ResourceDefinitionCreate(
        name="tips_200ul",
        fqn="test.tips.200uL",
        resource_type="tips",
        is_consumable=True,
    )
    assert tips.is_consumable is True

    # Plate carrier - not consumable
    carrier = ResourceDefinitionCreate(
        name="plate_carrier",
        fqn="test.carrier.PlateCarrier",
        resource_type="carrier",
        is_consumable=False,
    )
    assert carrier.is_consumable is False


def test_resource_definition_physical_dimensions() -> None:
    """Test physical dimension fields."""
    resource_def = ResourceDefinitionCreate(
        name="dimensioned_plate",
        fqn="test.dimensions.Plate",
        size_x_mm=127.76,
        size_y_mm=85.48,
        size_z_mm=14.35,
    )

    assert resource_def.size_x_mm == 127.76
    assert resource_def.size_y_mm == 85.48
    assert resource_def.size_z_mm == 14.35
