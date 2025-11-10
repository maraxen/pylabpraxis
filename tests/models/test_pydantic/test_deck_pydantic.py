"""Unit tests for Deck Pydantic models."""
import pytest
from pydantic import UUID7, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.pydantic_internals.deck import (
    DeckBase,
    DeckCreate,
    DeckUpdate,
    DeckResponse,
    DeckPositionDefinitionCreate,
    DeckPositionDefinitionResponse,
    PositioningConfig,
)
from praxis.backend.models.orm.deck import (
    DeckOrm,
    DeckDefinitionOrm,
    DeckPositionDefinitionOrm,
)
from praxis.backend.models.orm.resource import ResourceDefinitionOrm
from praxis.backend.models.enums import AssetType, ResourceStatusEnum


def test_deck_base_minimal() -> None:
    """Test creating a DeckBase with minimal required fields."""
    deck = DeckBase(
        name="test_deck",
        asset_type=AssetType.DECK,
    )

    assert deck.name == "test_deck"
    assert deck.asset_type == "DECK"
    assert deck.status == ResourceStatusEnum.UNKNOWN
    assert deck.machine_id is None
    assert deck.deck_type_id is None


def test_deck_base_with_all_fields() -> None:
    """Test creating a DeckBase with all fields populated."""
    from praxis.backend.utils.uuid import uuid7

    machine_id = uuid7()
    deck_type_id = uuid7()
    resource_def_id = uuid7()

    deck = DeckBase(
        name="full_deck",
        fqn="test.full.Deck",
        asset_type=AssetType.DECK,
        status=ResourceStatusEnum.AVAILABLE_ON_DECK,
        machine_id=machine_id,
        deck_type_id=deck_type_id,
        resource_definition_accession_id=resource_def_id,
    )

    assert deck.name == "full_deck"
    assert deck.fqn == "test.full.Deck"
    assert deck.asset_type == "DECK"
    assert deck.status == "available_on_deck"
    assert deck.machine_id == machine_id
    assert deck.deck_type_id == deck_type_id
    assert deck.resource_definition_accession_id == resource_def_id


def test_deck_create_inherits_from_base() -> None:
    """Test that DeckCreate inherits from DeckBase and ResourceCreate."""
    from praxis.backend.utils.uuid import uuid7

    resource_def_id = uuid7()

    deck = DeckCreate(
        name="create_deck",
        fqn="test.create.Deck",
        asset_type=AssetType.DECK,
        resource_definition_accession_id=resource_def_id,
    )

    assert deck.name == "create_deck"
    assert deck.fqn == "test.create.Deck"
    assert deck.asset_type == "DECK"
    assert deck.resource_definition_accession_id == resource_def_id
    assert deck.status == ResourceStatusEnum.UNKNOWN


def test_deck_update_all_fields_optional() -> None:
    """Test that DeckUpdate allows all fields to be optional."""
    # DeckUpdate inherits from ResourceUpdate which requires asset_type
    update = DeckUpdate(asset_type=AssetType.DECK)

    assert update.asset_type == "DECK"
    assert update.name is not None  # Auto-generated from UUID
    assert update.status == ResourceStatusEnum.UNKNOWN  # Default status

    # Can update specific fields
    update_partial = DeckUpdate(
        asset_type=AssetType.DECK,
        name="updated_deck",
        status=ResourceStatusEnum.AVAILABLE_ON_DECK,
    )
    assert update_partial.name == "updated_deck"
    assert update_partial.status == "available_on_deck"


def test_deck_response_serialization_to_dict() -> None:
    """Test that DeckResponse can be serialized to a dictionary."""
    from praxis.backend.utils.uuid import uuid7

    deck_id = uuid7()
    machine_id = uuid7()
    deck_type_id = uuid7()

    deck = DeckResponse(
        accession_id=deck_id,
        name="response_deck",
        fqn="test.response.Deck",
        asset_type=AssetType.DECK,
        status=ResourceStatusEnum.AVAILABLE_ON_DECK,
        machine_id=machine_id,
        deck_type_id=deck_type_id,
    )

    deck_dict = deck.model_dump()

    assert deck_dict["accession_id"] == deck_id
    assert deck_dict["name"] == "response_deck"
    assert deck_dict["fqn"] == "test.response.Deck"
    assert deck_dict["asset_type"] == "DECK"
    assert deck_dict["status"] == "available_on_deck"
    assert deck_dict["machine_id"] == machine_id
    assert deck_dict["deck_type_id"] == deck_type_id


def test_deck_response_serialization_to_json() -> None:
    """Test that DeckResponse can be serialized to JSON."""
    from praxis.backend.utils.uuid import uuid7

    deck_id = uuid7()

    deck = DeckResponse(
        accession_id=deck_id,
        name="json_deck",
        fqn="test.json.Deck",
        asset_type=AssetType.DECK,
    )

    json_str = deck.model_dump_json()

    assert isinstance(json_str, str)
    assert "json_deck" in json_str
    assert str(deck_id) in json_str


def test_deck_response_deserialization_from_dict() -> None:
    """Test creating DeckResponse from a dictionary."""
    from praxis.backend.utils.uuid import uuid7

    deck_id = uuid7()
    machine_id = uuid7()

    deck_data = {
        "accession_id": deck_id,
        "name": "deserialized_deck",
        "fqn": "test.deserialized.Deck",
        "asset_type": "RESOURCE",
        "status": "available_on_deck",
        "machine_id": machine_id,
    }

    deck = DeckResponse(**deck_data)

    assert deck.accession_id == deck_id
    assert deck.name == "deserialized_deck"
    assert deck.status == "available_on_deck"
    assert deck.machine_id == machine_id


def test_deck_response_roundtrip_serialization() -> None:
    """Test that DeckResponse survives serialization round-trip."""
    from praxis.backend.utils.uuid import uuid7

    original = DeckResponse(
        accession_id=uuid7(),
        name="roundtrip_deck",
        fqn="test.roundtrip.Deck",
        asset_type=AssetType.DECK,
        status=ResourceStatusEnum.AVAILABLE_ON_DECK,
        deck_type_id=uuid7(),
    )

    # Serialize to dict and back
    deck_dict = original.model_dump()
    restored = DeckResponse(**deck_dict)

    assert restored.accession_id == original.accession_id
    assert restored.name == original.name
    assert restored.fqn == original.fqn
    assert restored.asset_type == original.asset_type
    assert restored.status == original.status
    assert restored.deck_type_id == original.deck_type_id


@pytest.mark.asyncio
async def test_deck_response_from_orm(db_session: AsyncSession) -> None:
    """Test converting DeckOrm to DeckResponse."""
    from praxis.backend.utils.uuid import uuid7

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="orm_deck_resource_def",
        fqn="test.orm.DeckResourceDef",
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Create deck definition
    deck_def = DeckDefinitionOrm(
        name="orm_deck_def",
        fqn="test.orm.DeckDef",
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Create ORM deck
    deck_id = uuid7()
    orm_deck = DeckOrm(
        accession_id=deck_id,
        name="orm_test_deck",
        fqn="test.orm.Deck",
        asset_type=AssetType.DECK,
        status=ResourceStatusEnum.AVAILABLE_ON_DECK,
        deck_type_id=deck_def.accession_id,
    )
    orm_deck.resource_definition = resource_def
    orm_deck.deck_type = deck_def

    db_session.add(orm_deck)
    await db_session.flush()

    # Convert to Pydantic
    response = DeckResponse.model_validate(orm_deck)

    # Verify conversion
    assert response.accession_id == deck_id
    assert response.name == "orm_test_deck"
    assert response.fqn == "test.orm.Deck"
    assert response.asset_type == "DECK"
    assert response.status == "available_on_deck"
    assert response.deck_type_id == deck_def.accession_id
    assert response.resource_definition_accession_id == resource_def.accession_id


@pytest.mark.asyncio
async def test_deck_response_from_orm_minimal(db_session: AsyncSession) -> None:
    """Test ORM-to-Pydantic conversion with minimal fields."""
    from praxis.backend.utils.uuid import uuid7

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="minimal_deck_resource_def",
        fqn="test.minimal.DeckResourceDef",
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Create deck definition
    deck_def = DeckDefinitionOrm(
        name="minimal_deck_def",
        fqn="test.minimal.DeckDef",
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Create minimal deck
    deck_id = uuid7()
    orm_deck = DeckOrm(
        accession_id=deck_id,
        name="minimal_deck",
        fqn="test.minimal.Deck",
        asset_type=AssetType.DECK,
        deck_type_id=deck_def.accession_id,
    )
    orm_deck.resource_definition = resource_def
    orm_deck.deck_type = deck_def

    db_session.add(orm_deck)
    await db_session.flush()

    # Convert to Pydantic
    response = DeckResponse.model_validate(orm_deck)

    # Verify
    assert response.accession_id == deck_id
    assert response.name == "minimal_deck"
    assert response.status == "unknown"  # Default
    assert response.machine_id is None  # Optional


def test_positioning_config_model() -> None:
    """Test PositioningConfig Pydantic model."""
    config = PositioningConfig(
        method_name="slot_to_location",
        arg_name="slot",
        arg_type="str",
        params={"offset_x": 10.0, "offset_y": 5.0}
    )

    assert config.method_name == "slot_to_location"
    assert config.arg_name == "slot"
    assert config.arg_type == "str"
    assert config.params["offset_x"] == 10.0


def test_deck_position_definition_create() -> None:
    """Test DeckPositionDefinitionCreate model."""
    position = DeckPositionDefinitionCreate(
        nominal_x_mm=100.0,
        nominal_y_mm=200.0,
        nominal_z_mm=10.0,
        pylabrobot_position_type_name="Slot",
        accepts_plates=True,
        accepts_tips=False,
        notes="Position A1 for 96-well plates"
    )

    assert position.nominal_x_mm == 100.0
    assert position.nominal_y_mm == 200.0
    assert position.nominal_z_mm == 10.0
    assert position.pylabrobot_position_type_name == "Slot"
    assert position.accepts_plates is True
    assert position.accepts_tips is False
    assert position.notes == "Position A1 for 96-well plates"


def test_deck_position_definition_response() -> None:
    """Test DeckPositionDefinitionResponse model."""
    from praxis.backend.utils.uuid import uuid7

    deck_type_id = uuid7()

    position = DeckPositionDefinitionResponse(
        nominal_x_mm=100.0,
        nominal_y_mm=200.0,
        nominal_z_mm=10.0,
        deck_type_accession_id=deck_type_id,
    )

    assert position.nominal_x_mm == 100.0
    assert position.nominal_y_mm == 200.0
    assert position.nominal_z_mm == 10.0
    assert position.deck_type_accession_id == deck_type_id


def test_deck_position_definition_with_compatible_resources() -> None:
    """Test DeckPositionDefinitionCreate with compatible_resource_fqns."""
    compatible_resources = {
        "plates": ["corning_96_wellplate", "greiner_96_wellplate"],
        "tips": []
    }

    position = DeckPositionDefinitionCreate(
        nominal_x_mm=100.0,
        nominal_y_mm=200.0,
        nominal_z_mm=10.0,
        compatible_resource_fqns=compatible_resources,
        accepts_plates=True,
    )

    assert position.compatible_resource_fqns == compatible_resources
    assert "plates" in position.compatible_resource_fqns
    assert len(position.compatible_resource_fqns["plates"]) == 2
