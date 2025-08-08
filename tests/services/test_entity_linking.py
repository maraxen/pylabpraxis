# tests/db_services/test_entity_linking.py

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models import (
  DeckOrm,
  MachineOrm,
  ResourceDefinitionOrm,
  ResourceOrm,
)
from praxis.backend.services.entity_linking import (
  _create_or_link_machine_counterpart_for_resource,
  _create_or_link_resource_counterpart_for_machine,
  _read_resource_definition_for_linking,
  synchronize_deck_resource_names,
  synchronize_machine_resource_names,
  synchronize_resource_deck_names,
  synchronize_resource_machine_names,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def resource_def(db: AsyncSession) -> ResourceDefinitionOrm:
  """Fixture to create a ResourceDefinitionOrm instance."""
  definition = ResourceDefinitionOrm(
    name=f"test_definition_{uuid.uuid4()}",
    fqn="pylabrobot.resources.Plate",
    category="plate",
  )
  db.add(definition)
  await db.commit()
  await db.refresh(definition)
  return definition


@pytest.fixture
async def machine1(db: AsyncSession) -> MachineOrm:
  """Fixture to create a basic MachineOrm instance."""
  machine = MachineOrm(
    name="TestMachine1",
    fqn="pylabrobot.liquid_handling.LiquidHandler",
  )
  db.add(machine)
  await db.commit()
  await db.refresh(machine)
  return machine


@pytest.fixture
async def resource1(
  db: AsyncSession,
  resource_def: ResourceDefinitionOrm,
) -> ResourceOrm:
  """Fixture to create a basic ResourceOrm instance."""
  resource = ResourceOrm(
    name="TestResource1",
    resource_definition_name=resource_def.name,
  )
  db.add(resource)
  await db.commit()
  await db.refresh(resource)
  return resource


@pytest.fixture
async def deck1(db: AsyncSession, resource1: ResourceOrm) -> DeckOrm:
  """Fixture to create a basic DeckOrm."""
  deck = DeckOrm(
    name="TestDeck1",
    deck_accession_id=resource1.accession_id,  # Just needs a valid UUID
    fqn="pylabrobot.resources.Deck",
  )
  db.add(deck)
  await db.commit()
  await db.refresh(deck)
  return deck


class TestEntityLinking:

  """Test suite for entity linking and synchronization functions."""

  async def test_read_resource_definition_for_linking(
    self,
    db: AsyncSession,
    resource_def: ResourceDefinitionOrm,
  ) -> None:
    """Test successfully reading an existing resource definition."""
    result = await _read_resource_definition_for_linking(db, resource_def.name)
    assert result is not None
    assert result.name == resource_def.name

  async def test_read_resource_definition_not_found(self, db: AsyncSession) -> None:
    """Test that reading a non-existent resource definition raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
      await _read_resource_definition_for_linking(db, "non_existent_def")

  # --- Machine <-> Resource Linking ---

  async def test_create_resource_counterpart_for_machine(
    self,
    db: AsyncSession,
    machine1: MachineOrm,
    resource_def: ResourceDefinitionOrm,
  ) -> None:
    """Test creating a new resource counterpart for a machine."""
    resource = await _create_or_link_resource_counterpart_for_machine(
      db=db,
      machine_orm=machine1,
      is_resource=True,
      resource_counterpart_accession_id=None,
      resource_def_name=resource_def.name,
    )
    await db.commit()

    assert resource is not None
    await db.refresh(machine1, ["resource_counterpart"])
    await db.refresh(resource, ["machine_counterpart"])

    assert machine1.resource_counterpart_accession_id == resource.accession_id
    assert resource.machine_counterpart_accession_id == machine1.accession_id
    assert resource.is_machine is True
    assert resource.name == machine1.name

  async def test_link_existing_resource_to_machine(
    self,
    db: AsyncSession,
    machine1: MachineOrm,
    resource1: ResourceOrm,
  ) -> None:
    """Test linking an existing resource to a machine."""
    linked_resource = await _create_or_link_resource_counterpart_for_machine(
      db=db,
      machine_orm=machine1,
      is_resource=True,
      resource_counterpart_accession_id=resource1.accession_id,
    )
    await db.commit()

    assert linked_resource is not None
    assert linked_resource.accession_id == resource1.accession_id
    await db.refresh(machine1, ["resource_counterpart"])
    await db.refresh(resource1, ["machine_counterpart"])

    assert machine1.resource_counterpart_accession_id == resource1.accession_id
    assert resource1.machine_counterpart_accession_id == machine1.accession_id
    assert resource1.is_machine is True
    assert resource1.name == machine1.name

  async def test_unlink_resource_from_machine(
    self,
    db: AsyncSession,
    machine1: MachineOrm,
    resource1: ResourceOrm,
  ) -> None:
    """Test unlinking a resource from a machine by setting is_resource=False."""
    # First, link them
    machine1.resource_counterpart = resource1
    resource1.machine_counterpart = machine1
    resource1.is_machine = True
    db.add_all([machine1, resource1])
    await db.commit()

    # Now, unlink
    await _create_or_link_resource_counterpart_for_machine(
      db=db,
      machine_orm=machine1,
      is_resource=False,
      resource_counterpart_accession_id=None,
    )
    await db.commit()

    await db.refresh(machine1)
    await db.refresh(resource1)

    assert machine1.resource_counterpart is None
    assert resource1.machine_counterpart is None
    assert resource1.is_machine is False

  # --- Resource <-> Machine Linking (Inverse) ---

  async def test_create_machine_counterpart_for_resource(
    self,
    db: AsyncSession,
    resource1: ResourceOrm,
  ) -> None:
    """Test creating a new machine counterpart for a resource."""
    machine = await _create_or_link_machine_counterpart_for_resource(
      db=db,
      resource_orm=resource1,
      is_machine=True,
      machine_counterpart_accession_id=None,
      machine_name=resource1.name,
      machine_fqn="pylabrobot.new.Machine",
    )
    await db.commit()

    assert machine is not None
    await db.refresh(resource1, ["machine_counterpart"])
    await db.refresh(machine, ["resource_counterpart"])

    assert resource1.machine_counterpart_accession_id == machine.accession_id
    assert machine.resource_counterpart_accession_id == resource1.accession_id
    assert machine.is_resource is True
    assert machine.name == resource1.name

  async def test_link_existing_machine_to_resource(
    self,
    db: AsyncSession,
    machine1: MachineOrm,
    resource1: ResourceOrm,
  ) -> None:
    """Test linking an existing machine to a resource."""
    linked_machine = await _create_or_link_machine_counterpart_for_resource(
      db=db,
      resource_orm=resource1,
      is_machine=True,
      machine_counterpart_accession_id=machine1.accession_id,
    )
    await db.commit()

    assert linked_machine is not None
    assert linked_machine.accession_id == machine1.accession_id
    await db.refresh(resource1, ["machine_counterpart"])
    await db.refresh(machine1, ["resource_counterpart"])

    assert resource1.machine_counterpart_accession_id == machine1.accession_id
    assert machine1.resource_counterpart_accession_id == resource1.accession_id
    assert machine1.is_resource is True
    assert machine1.name == resource1.name

  # --- Name Synchronization ---

  async def test_synchronize_machine_to_resource_name(
    self,
    db: AsyncSession,
    machine1: MachineOrm,
    resource1: ResourceOrm,
  ) -> None:
    """Test that updating a machine's name synchronizes to its resource counterpart."""
    # Link them
    machine1.resource_counterpart = resource1
    db.add(machine1)
    await db.commit()

    new_name = "UpdatedMachineName"
    machine1.name = new_name
    await synchronize_machine_resource_names(db, machine1)
    await db.commit()

    await db.refresh(resource1)
    assert resource1.name == new_name

  async def test_synchronize_resource_to_machine_name(
    self,
    db: AsyncSession,
    machine1: MachineOrm,
    resource1: ResourceOrm,
  ) -> None:
    """Test that updating a resource's name synchronizes to its machine counterpart."""
    # Link them
    resource1.machine_counterpart = machine1
    resource1.is_machine = True
    db.add(resource1)
    await db.commit()

    new_name = "UpdatedResourceName"
    resource1.name = new_name
    await synchronize_resource_machine_names(db, resource1)
    await db.commit()

    await db.refresh(machine1)
    assert machine1.name == new_name

  async def test_synchronize_deck_to_resource_name(
    self,
    db: AsyncSession,
    deck1: DeckOrm,
    resource1: ResourceOrm,
  ) -> None:
    """Test that updating a deck's name synchronizes to its resource counterpart."""
    # Link them
    deck1.resource_counterpart = resource1
    db.add(deck1)
    await db.commit()

    new_name = "UpdatedDeckName"
    deck1.name = new_name
    await synchronize_deck_resource_names(db, deck1)
    await db.commit()

    await db.refresh(resource1)
    assert resource1.name == new_name

  async def test_synchronize_resource_to_deck_name(
    self,
    db: AsyncSession,
    deck1: DeckOrm,
    resource1: ResourceOrm,
  ) -> None:
    """Test that updating a resource's name synchronizes to its deck counterpart."""
    # Link them
    resource1.deck_counterpart = deck1
    db.add(resource1)
    await db.commit()

    new_name = "UpdatedResourceNameForDeck"
    resource1.name = new_name
    await synchronize_resource_deck_names(db, resource1)
    await db.commit()

    await db.refresh(deck1)
    assert deck1.name == new_name
