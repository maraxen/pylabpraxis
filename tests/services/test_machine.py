import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import all required models from the central package
from praxis.backend.models import (
  DeckOrm,
  MachineOrm,
  MachineStatusEnum,
  ResourceDefinitionCatalogOrm,
  ResourceOrm,
)

# Import the service functions to be tested
from praxis.backend.services.machine import (
  create_machine,
  delete_machine,
  list_machines,
  read_machine,
  read_machine_by_name,
  update_machine,
  update_machine_status,
)
from praxis.backend.utils.db import Base

# --- Placeholder ORMs for dependency satisfaction ---


class WorkcellOrm(Base):
  __tablename__ = "workcells"
  accession_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  machines = relationship("MachineOrm", back_populates="workcell")


class ProtocolRunOrm(Base):
  __tablename__ = "protocol_runs"
  # The machine ORM references 'run_accession_id', so we name it that way.
  run_accession_id: Mapped[uuid.UUID] = mapped_column(
    primary_key=True,
    default=uuid.uuid4,
  )


# --- Pytest Fixtures ---


@pytest.fixture
async def resource_def(db: AsyncSession) -> ResourceDefinitionCatalogOrm:
  """Fixture for a ResourceDefinitionCatalogOrm."""
  definition = ResourceDefinitionCatalogOrm(
    name=f"test_machine_resource_def_{uuid.uuid4()}",
    python_fqn="pylabrobot.liquid_handling.LiquidHandler",
    category="LIQUID_HANDLER",
  )
  db.add(definition)
  await db.commit()
  return definition


@pytest.fixture
async def existing_resource(
  db: AsyncSession,
  resource_def: ResourceDefinitionCatalogOrm,
) -> ResourceOrm:
  """Fixture for a pre-existing ResourceOrm to test linking."""
  resource = ResourceOrm(
    user_assigned_name="ExistingResourceForLinking",
    name=resource_def.name,
  )
  db.add(resource)
  await db.commit()
  return resource


@pytest.fixture
async def existing_machine(db: AsyncSession) -> MachineOrm:
  """Fixture that creates a standard machine for update/read/delete tests."""
  machine = await create_machine(
    db,
    user_friendly_name=f"TestMachine_{uuid.uuid4()}",
    python_fqn="pylabrobot.liquid_handling.hamilton.STAR",
  )
  return machine


pytestmark = pytest.mark.asyncio


class TestMachineService:
  """Test suite for the machine data service layer."""

  async def test_create_machine_simple(self, db: AsyncSession):
    """Test creating a machine with only required fields."""
    name = f"SimpleMachine_{uuid.uuid4()}"
    fqn = "pylabrobot.pumps.Pump"
    machine = await create_machine(db, user_friendly_name=name, python_fqn=fqn)
    assert machine is not None
    assert machine.user_friendly_name == name
    assert machine.python_fqn == fqn
    assert machine.is_resource is False
    assert machine.resource_counterpart is None

  async def test_create_machine_as_new_resource(
    self,
    db: AsyncSession,
    resource_def: ResourceDefinitionCatalogOrm,
  ):
    """Test creating a machine that is also a new resource counterpart."""
    name = f"MachineAsResource_{uuid.uuid4()}"
    machine = await create_machine(
      db,
      user_friendly_name=name,
      python_fqn=resource_def.python_fqn,
      is_resource=True,
      resource_def_name=resource_def.name,
    )
    assert machine.is_resource is True
    assert machine.resource_counterpart is not None
    assert machine.resource_counterpart.user_assigned_name == name
    assert machine.resource_counterpart.is_machine is True

  async def test_create_machine_fails_on_duplicate_name(
    self,
    db: AsyncSession,
    existing_machine: MachineOrm,
  ):
    """Test that creating a machine with a duplicate name raises ValueError."""
    with pytest.raises(ValueError, match="already exists"):
      await create_machine(
        db,
        user_friendly_name=existing_machine.user_friendly_name,
        python_fqn="some.other.fqn",
      )

  async def test_read_machine_and_read_by_name(
    self,
    db: AsyncSession,
    existing_machine: MachineOrm,
  ):
    """Test reading a machine by its ID and by its name."""
    from_id = await read_machine(db, existing_machine.accession_id)
    assert from_id is not None
    assert from_id.user_friendly_name == existing_machine.user_friendly_name

    from_name = await read_machine_by_name(db, existing_machine.user_friendly_name)
    assert from_name is not None
    assert from_name.accession_id == existing_machine.accession_id

  async def test_update_machine_simple_fields(
    self,
    db: AsyncSession,
    existing_machine: MachineOrm,
  ):
    """Test updating simple properties of a machine."""
    updated_machine = await update_machine(
      db,
      machine_accession_id=existing_machine.accession_id,
      status_details="Now with more details",
      properties_json={"calibration_factor": 1.05},
    )
    assert updated_machine.status_details == "Now with more details"
    assert updated_machine.properties_json is not None
    assert updated_machine.properties_json["calibration_factor"] == 1.05

  async def test_update_machine_name_and_resource_sync(
    self,
    db: AsyncSession,
    resource_def: ResourceDefinitionCatalogOrm,
  ):
    """Test that updating a machine's name also syncs to its resource counterpart."""
    name = f"SyncMachine_{uuid.uuid4()}"
    machine = await create_machine(
      db,
      user_friendly_name=name,
      python_fqn=resource_def.python_fqn,
      is_resource=True,
      resource_def_name=resource_def.name,
    )

    new_name = f"SyncedName_{uuid.uuid4()}"
    await update_machine(
      db,
      machine_accession_id=machine.accession_id,
      user_friendly_name=new_name,
    )

    await db.refresh(machine, ["resource_counterpart"])
    assert machine.user_friendly_name == new_name
    assert machine.resource_counterpart is not None
    assert machine.resource_counterpart.user_assigned_name == new_name

  async def test_update_machine_to_link_resource(
    self,
    db: AsyncSession,
    existing_machine: MachineOrm,
    existing_resource: ResourceOrm,
  ):
    """Test updating a machine to link it to an existing resource."""
    assert existing_machine.is_resource is False
    updated_machine = await update_machine(
      db,
      machine_accession_id=existing_machine.accession_id,
      is_resource=True,
      resource_counterpart_accession_id=existing_resource.accession_id,
    )
    assert updated_machine.is_resource is True
    assert (
      updated_machine.resource_counterpart_accession_id
      == existing_resource.accession_id
    )

  async def test_list_machines_with_filters(self, db: AsyncSession):
    """Test the filtering capabilities of the list_machines function."""
    name1 = f"FilterMachineA_{uuid.uuid4()}"
    name2 = f"FilterMachineB_{uuid.uuid4()}"
    await create_machine(
      db,
      name1,
      "pylabrobot.liquid_handling.hamilton.STAR",
      current_status=MachineStatusEnum.AVAILABLE,
    )
    await create_machine(
      db,
      name2,
      "pylabrobot.plate_readers.BioTek",
      current_status=MachineStatusEnum.OFFLINE,
    )

    # Filter by status
    results = await list_machines(db, status=MachineStatusEnum.OFFLINE)
    assert len(results) == 1
    assert results[0].user_friendly_name == name2

    # Filter by name (case-insensitive partial)
    results = await list_machines(db, user_friendly_name_filter="machinea")
    assert len(results) == 1
    assert results[0].user_friendly_name == name1

    # Filter by class
    results = await list_machines(db, pylabrobot_class_filter="BioTek")
    assert len(results) == 1
    assert results[0].user_friendly_name == name2

  async def test_update_machine_status(
    self,
    db: AsyncSession,
    existing_machine: MachineOrm,
  ):
    """Test the dedicated function for updating machine status."""
    protocol_run = ProtocolRunOrm()
    db.add(protocol_run)
    await db.commit()

    assert existing_machine.current_status == MachineStatusEnum.OFFLINE

    # Update to IN_USE
    updated_machine = await update_machine_status(
      db,
      machine_accession_id=existing_machine.accession_id,
      new_status=MachineStatusEnum.IN_USE,
      status_details="Running protocol",
      current_protocol_run_accession_id=protocol_run.run_accession_id,
    )
    assert updated_machine is not None
    assert updated_machine.current_status == MachineStatusEnum.IN_USE
    assert (
      updated_machine.current_protocol_run_accession_id == protocol_run.run_accession_id
    )
    assert updated_machine.last_seen_online is not None

  async def test_delete_machine(self, db: AsyncSession, existing_machine: MachineOrm):
    """Test deleting a machine."""
    machine_id = existing_machine.accession_id
    result = await delete_machine(db, machine_id)
    assert result is True

    # Verify it's gone
    assert await read_machine(db, machine_id) is None

  async def test_delete_machine_with_dependency_fails(
    self,
    db: AsyncSession,
    existing_machine: MachineOrm,
  ):
    """Test that deleting a machine with a foreign key dependency fails gracefully."""
    # Create a deck instance that depends on the machine
    deck = DeckOrm(
      name="DeckOnMachine",
      deck_accession_id=uuid.uuid4(),
      python_fqn="deck.fqn",
      parent_machine=existing_machine,  # This creates the FK constraint
    )
    db.add(deck)
    await db.commit()

    with pytest.raises(ValueError, match="due to existing references"):
      await delete_machine(db, existing_machine.accession_id)
