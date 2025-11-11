"""Unit tests for Deck-related ORM models."""
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from praxis.backend.models.orm.asset import AssetOrm
from praxis.backend.models.orm.deck import (
    DeckOrm,
    DeckDefinitionOrm,
    DeckPositionDefinitionOrm,
)
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.resource import ResourceOrm, ResourceDefinitionOrm
from praxis.backend.models.enums import AssetType, ResourceStatusEnum


@pytest_asyncio.fixture
async def deck_definition(db_session: AsyncSession) -> DeckDefinitionOrm:
    """Create a DeckDefinitionOrm for testing."""
    deck_def = DeckDefinitionOrm(
        name="test_deck_definition_fixture",
        fqn="test.deck.DefinitionFixture",
    )
    db_session.add(deck_def)
    await db_session.flush()
    return deck_def


@pytest_asyncio.fixture
async def resource_definition(db_session: AsyncSession) -> ResourceDefinitionOrm:
    """Create a ResourceDefinitionOrm for testing."""
    res_def = ResourceDefinitionOrm(
        name="test_resource_definition_fixture",
        fqn="test.resource.DefinitionFixture",
    )
    db_session.add(res_def)
    await db_session.flush()
    return res_def


@pytest_asyncio.fixture
async def deck(
    db_session: AsyncSession,
    deck_definition: DeckDefinitionOrm,
    resource_definition: ResourceDefinitionOrm,
) -> DeckOrm:
    """Create a complete DeckOrm instance for testing."""
    from praxis.backend.utils.uuid import uuid7

    deck = DeckOrm(
        accession_id=uuid7(),
        name="test_deck_fixture",
        fqn="test.deck.Fixture",
        asset_type=AssetType.DECK,
        deck_type_id=deck_definition.accession_id,
        resource_definition_accession_id=resource_definition.accession_id,
    )
    deck.deck_type = deck_definition
    deck.resource_definition = resource_definition
    db_session.add(deck)
    await db_session.flush()
    return deck


@pytest.mark.asyncio
async def test_deck_definition_orm_creation(db_session: AsyncSession) -> None:
    """Test creating a DeckDefinitionOrm with minimal fields."""
    from praxis.backend.utils.uuid import uuid7

    # Create deck definition
    deck_def = DeckDefinitionOrm(
        name="test_deck_definition",
        fqn="test.deck.Definition",
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Verify defaults
    assert deck_def.accession_id is not None
    assert deck_def.name == "test_deck_definition"
    assert deck_def.fqn == "test.deck.Definition"
    assert deck_def.default_size_x_mm is None
    assert deck_def.default_size_y_mm is None
    assert deck_def.default_size_z_mm is None


@pytest.mark.asyncio
async def test_deck_definition_orm_with_jsonb_fields(db_session: AsyncSession) -> None:
    """Test DeckDefinitionOrm with JSONB fields."""
    positioning_config = {
        "method_name": "slot_to_location",
        "arg_name": "slot",
        "arg_type": "str"
    }

    constructor_args = {
        "rails": 54,
        "size_x": 1360.0,
        "size_y": 653.0
    }

    deck_def = DeckDefinitionOrm(
        name="hamilton_star_deck",
        fqn="pylabrobot.liquid_handling.backends.hamilton.STARDeck",
        positioning_config_json=positioning_config,
        serialized_constructor_args_json=constructor_args,
        default_size_x_mm=1360.0,
        default_size_y_mm=653.0,
        default_size_z_mm=100.0,
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Verify JSONB fields stored correctly
    assert deck_def.positioning_config_json == positioning_config
    assert deck_def.serialized_constructor_args_json == constructor_args
    assert deck_def.positioning_config_json["method_name"] == "slot_to_location"
    assert deck_def.serialized_constructor_args_json["rails"] == 54


@pytest.mark.asyncio
async def test_deck_position_definition_orm_creation(db_session: AsyncSession) -> None:
    """Test creating a DeckPositionDefinitionOrm."""
    from praxis.backend.utils.uuid import uuid7

    # Create deck definition first
    deck_def = DeckDefinitionOrm(
        name="test_deck_for_positions",
        fqn="test.deck.ForPositions",
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Create position definition
    position = DeckPositionDefinitionOrm(
        name="position_a1",
        deck_type_id=deck_def.accession_id,
        position_accession_id="A1",
        nominal_x_mm=100.0,
        nominal_y_mm=200.0,
        nominal_z_mm=10.0,
        accepts_plates=True,
        accepts_tips=False,
        deck_type=deck_def,  # Also set relationship
    )
    db_session.add(position)
    await db_session.flush()

    # Verify
    assert position.accession_id is not None
    assert position.position_accession_id == "A1"
    assert position.nominal_x_mm == 100.0
    assert position.nominal_y_mm == 200.0
    assert position.nominal_z_mm == 10.0
    assert position.accepts_plates is True
    assert position.accepts_tips is False


@pytest.mark.asyncio
async def test_deck_position_definition_orm_unique_constraint(db_session: AsyncSession) -> None:
    """Test unique constraint on (deck_type_id, position_accession_id)."""
    from praxis.backend.utils.uuid import uuid7
    from sqlalchemy.exc import IntegrityError

    # Create deck definition
    deck_def = DeckDefinitionOrm(
        name="unique_constraint_deck",
        fqn="test.deck.UniqueConstraint",
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Create first position
    position1 = DeckPositionDefinitionOrm(
        name="unique_position_a1",
        deck_type_id=deck_def.accession_id,
        position_accession_id="A1",
        nominal_x_mm=100.0,
        nominal_y_mm=200.0,
        nominal_z_mm=10.0,
        deck_type=deck_def,
    )
    db_session.add(position1)
    await db_session.flush()

    # Try to create duplicate position on same deck
    position2 = DeckPositionDefinitionOrm(
        name="unique_position_a1_duplicate",
        deck_type_id=deck_def.accession_id,
        position_accession_id="A1",  # Duplicate
        nominal_x_mm=150.0,
        nominal_y_mm=250.0,
        nominal_z_mm=10.0,
        deck_type=deck_def,
    )
    db_session.add(position2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_deck_orm_creation_with_defaults(db_session: AsyncSession) -> None:
    """Test creating a DeckOrm with minimal required fields."""
    from praxis.backend.utils.uuid import uuid7

    # Create resource definition for deck
    resource_def = ResourceDefinitionOrm(
        name="deck_resource_def",
        fqn="test.deck.ResourceDef",
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Create deck definition
    deck_def = DeckDefinitionOrm(
        name="test_deck_def",
        fqn="test.deck.TypeDef",
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Create deck with required fields
    deck_id = uuid7()
    deck = DeckOrm(
        accession_id=deck_id,
        name="test_deck",
        fqn="test.deck.Instance",
        asset_type=AssetType.DECK,
        deck_type_id=deck_def.accession_id,  # Required kw_only FK
    )
    # Set FKs via relationships (workaround for MappedAsDataclass FK issue)
    deck.resource_definition = resource_def
    deck.deck_type = deck_def

    db_session.add(deck)
    await db_session.flush()

    # Verify defaults
    assert deck.accession_id == deck_id
    assert deck.name == "test_deck"
    assert deck.fqn == "test.deck.Instance"
    assert deck.asset_type == AssetType.DECK
    assert deck.status == ResourceStatusEnum.UNKNOWN
    assert deck.resource_definition == resource_def
    assert deck.deck_type == deck_def
    assert deck.parent_machine_accession_id is None


@pytest.mark.asyncio
async def test_deck_orm_persist_to_database(db_session: AsyncSession) -> None:
    """Test full persistence cycle for DeckOrm."""
    from praxis.backend.utils.uuid import uuid7

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="persist_deck_resource_def",
        fqn="test.deck.PersistResourceDef",
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Create deck definition
    deck_def = DeckDefinitionOrm(
        name="persist_deck_def",
        fqn="test.deck.PersistDef",
        default_size_x_mm=1360.0,
        default_size_y_mm=653.0,
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Create deck
    deck_id = uuid7()
    deck = DeckOrm(
        accession_id=deck_id,
        name="test_persistence_deck",
        fqn="test.deck.Persistence",
        asset_type=AssetType.DECK,
        status=ResourceStatusEnum.AVAILABLE_ON_DECK,
        deck_type_id=deck_def.accession_id,
    )
    deck.resource_definition = resource_def
    deck.deck_type = deck_def

    db_session.add(deck)
    await db_session.flush()

    # Query back
    result = await db_session.execute(
        select(DeckOrm).where(DeckOrm.accession_id == deck_id)
    )
    retrieved = result.scalars().first()

    # Verify persistence
    assert retrieved is not None
    assert retrieved.accession_id == deck_id
    assert retrieved.name == "test_persistence_deck"
    assert retrieved.status == ResourceStatusEnum.AVAILABLE_ON_DECK
    assert retrieved.resource_definition_accession_id == resource_def.accession_id
    assert retrieved.deck_type_id == deck_def.accession_id


@pytest.mark.asyncio
async def test_deck_orm_unique_name_constraint(db_session: AsyncSession) -> None:
    """Test that deck names must be unique (inherited from Asset)."""
    from praxis.backend.utils.uuid import uuid7
    from sqlalchemy.exc import IntegrityError

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="unique_deck_resource_def",
        fqn="test.deck.UniqueResourceDef",
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Create deck definition
    deck_def = DeckDefinitionOrm(
        name="unique_deck_def",
        fqn="test.deck.UniqueDef",
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Create first deck
    deck1 = DeckOrm(
        accession_id=uuid7(),
        name="unique_deck",
        fqn="test.deck.1",
        asset_type=AssetType.DECK,
        deck_type_id=deck_def.accession_id,
    )
    deck1.resource_definition = resource_def
    deck1.deck_type = deck_def
    db_session.add(deck1)
    await db_session.flush()

    # Try to create another with same name
    deck2 = DeckOrm(
        accession_id=uuid7(),
        name="unique_deck",  # Duplicate
        fqn="test.deck.2",
        asset_type=AssetType.DECK,
        deck_type_id=deck_def.accession_id,
    )
    deck2.resource_definition = resource_def
    deck2.deck_type = deck_def
    db_session.add(deck2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_deck_orm_with_parent_machine(db_session: AsyncSession) -> None:
    """Test DeckOrm with parent machine relationship."""
    from praxis.backend.utils.uuid import uuid7
    from praxis.backend.models.orm.machine import MachineOrm

    # Create machine
    machine_id = uuid7()
    machine = MachineOrm(
        accession_id=machine_id,
        name="test_machine_for_deck",
        fqn="test.machine.ForDeck",
        asset_type=AssetType.MACHINE,
    )
    db_session.add(machine)
    await db_session.flush()

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="machine_deck_resource_def",
        fqn="test.deck.MachineDeckResourceDef",
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Create deck definition
    deck_def = DeckDefinitionOrm(
        name="machine_deck_def",
        fqn="test.deck.MachineDeckDef",
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Create deck with parent machine
    deck_id = uuid7()
    deck = DeckOrm(
        accession_id=deck_id,
        name="deck_on_machine",
        fqn="test.deck.OnMachine",
        asset_type=AssetType.DECK,
        deck_type_id=deck_def.accession_id,
    )
    deck.resource_definition = resource_def
    deck.deck_type = deck_def
    deck.parent_machine = machine

    db_session.add(deck)
    await db_session.flush()

    # Query back and verify
    result = await db_session.execute(
        select(DeckOrm).where(DeckOrm.accession_id == deck_id)
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.parent_machine_accession_id == machine_id


@pytest.mark.asyncio
async def test_deck_orm_with_resources(db_session: AsyncSession) -> None:
    """Test DeckOrm with resources placed on it."""
    from praxis.backend.utils.uuid import uuid7
    from praxis.backend.models.orm.resource import ResourceOrm

    # Create deck resource definition
    deck_resource_def = ResourceDefinitionOrm(
        name="deck_with_resources_def",
        fqn="test.deck.WithResourcesDef",
    )
    db_session.add(deck_resource_def)
    await db_session.flush()

    # Create deck definition
    deck_def = DeckDefinitionOrm(
        name="deck_for_resources",
        fqn="test.deck.ForResources",
    )
    db_session.add(deck_def)
    await db_session.flush()

    # Create deck
    deck_id = uuid7()
    deck = DeckOrm(
        accession_id=deck_id,
        name="deck_with_resources",
        fqn="test.deck.WithResources",
        asset_type=AssetType.DECK,
        deck_type_id=deck_def.accession_id,
    )
    deck.resource_definition = deck_resource_def
    deck.deck_type = deck_def
    db_session.add(deck)
    await db_session.flush()

    # Create resource definition for plate
    plate_def = ResourceDefinitionOrm(
        name="plate_def",
        fqn="test.resource.PlateDef",
    )
    db_session.add(plate_def)
    await db_session.flush()

    # Create resource on deck
    resource_id = uuid7()
    resource = ResourceOrm(
        accession_id=resource_id,
        name="plate_on_deck",
        fqn="test.resource.PlateOnDeck",
        asset_type=AssetType.DECK,
        current_deck_position_name="A1",
    )
    resource.resource_definition = plate_def
    resource.deck = deck
    db_session.add(resource)
    await db_session.flush()

    # Query back and verify relationship
    result = await db_session.execute(
        select(DeckOrm).where(DeckOrm.accession_id == deck_id)
    )
    retrieved_deck = result.scalars().first()

    assert retrieved_deck is not None
    # Note: May need to explicitly load relationships
    assert retrieved_deck.accession_id == deck_id

    # Query the resource to verify deck relationship
    resource_result = await db_session.execute(
        select(ResourceOrm).where(ResourceOrm.accession_id == resource_id)
    )
    retrieved_resource = resource_result.scalars().first()

    assert retrieved_resource is not None
    assert retrieved_resource.deck_accession_id == deck_id
    assert retrieved_resource.current_deck_position_name == "A1"


@pytest.mark.asyncio
async def test_deck_orm_is_resource_and_asset(
    db_session: AsyncSession, deck: DeckOrm
) -> None:
    """Verify that a DeckOrm is also a ResourceOrm and AssetOrm."""
    # Query as Asset
    asset_result = await db_session.execute(
        select(AssetOrm).where(AssetOrm.accession_id == deck.accession_id)
    )
    asset = asset_result.scalars().first()
    assert asset is not None
    assert asset.accession_id == deck.accession_id
    assert asset.name == "test_deck_fixture"
    assert asset.asset_type == AssetType.DECK

    # Query as Resource
    resource_result = await db_session.execute(
        select(ResourceOrm).where(ResourceOrm.accession_id == deck.accession_id)
    )
    resource = resource_result.scalars().first()
    assert resource is not None
    assert resource.accession_id == deck.accession_id
    assert resource.name == "test_deck_fixture"
    assert resource.status == ResourceStatusEnum.UNKNOWN


@pytest.mark.asyncio
async def test_deck_orm_relationships(
    db_session: AsyncSession,
    deck: DeckOrm,
    deck_definition: DeckDefinitionOrm,
    resource_definition: ResourceDefinitionOrm,
) -> None:
    """Test the relationships of the DeckOrm model."""
    result = await db_session.execute(
        select(DeckOrm)
        .where(DeckOrm.accession_id == deck.accession_id)
        .options(
            selectinload(DeckOrm.deck_type),
            selectinload(DeckOrm.resource_definition),
            selectinload(DeckOrm.resources),
        )
    )
    retrieved_deck = result.scalars().first()

    assert retrieved_deck is not None
    assert retrieved_deck.deck_type is not None
    assert retrieved_deck.deck_type.accession_id == deck_definition.accession_id
    assert retrieved_deck.resource_definition is not None
    assert (
        retrieved_deck.resource_definition.accession_id
        == resource_definition.accession_id
    )
    assert retrieved_deck.resources == []

    # Test bidirectional relationship from DeckDefinition
    result_def = await db_session.execute(
        select(DeckDefinitionOrm)
        .where(DeckDefinitionOrm.accession_id == deck_definition.accession_id)
        .options(selectinload(DeckDefinitionOrm.deck))
    )
    retrieved_def = result_def.scalars().first()
    assert retrieved_def is not None
    assert len(retrieved_def.deck) == 1
    assert retrieved_def.deck[0].accession_id == deck.accession_id
