import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import all required models from the central package
from praxis.backend.models import (
  MachineOrm,
  ProtocolRunOrm,
  ResourceDefinitionOrm,
  ResourceOrm,
  ResourceStatusEnum,
)

# Import the service functions to be tested
from praxis.backend.services import (
  create_resource,
  delete_resource,
  read_resource,
  read_resource_by_name,
  read_resources,
  update_resource,
  update_resource_location_and_status,
)

# --- Pytest Fixtures ---


@pytest.fixture
async def resource_def(db: AsyncSession) -> ResourceDefinitionOrm:
  """Fixture for a ResourceDefinitionOrm (e.g., a plate definition)."""
  definition = ResourceDefinitionOrm(
    name=f"corning_96_wellplate_360ul_flat_{uuid.uuid4()}",
    fqn="pylabrobot.resources.corning_96_wellplate_360ul_flat",
    category="plate",
  )
  db.add(definition)
  await db.commit()
  return definition


@pytest.fixture
async def machine(db: AsyncSession) -> MachineOrm:
  """Fixture for a MachineOrm to use for location and counterpart tests."""
  m = MachineOrm(
    name=f"TestMachine_{uuid.uuid4()}",
    fqn="machine.fqn",
  )
  db.add(m)
  await db.commit()
  return m


@pytest.fixture
async def protocol_run(db: AsyncSession) -> ProtocolRunOrm:
  """Fixture for a ProtocolRunOrm to use for status update tests."""
  p_run = ProtocolRunOrm(name="Test Run")
  db.add(p_run)
  await db.commit()
  return p_run


@pytest.fixture
async def existing_resource(
  db: AsyncSession,
  resource_def: ResourceDefinitionOrm,
) -> ResourceOrm:
  """Fixture that creates a standard resource instance for testing."""
  return await create_resource(
    db,
    name=f"TestPlate_{uuid.uuid4()}",
    fqn=resource_def.fqn,
    resource_definition_accession_id=resource_def.accession_id,
  )


pytestmark = pytest.mark.asyncio


class TestResourceService:
  """Test suite for the Resource  service layer."""

  async def test_create_and_read_resource(
    self,
    db: AsyncSession,
    resource_def: ResourceDefinitionOrm,
  ):
    """Test creating a simple resource and reading it back by ID and name."""
    name = f"MyPlate_{uuid.uuid4()}"
    resource = await create_resource(
      db,
      name=name,
      fqn=resource_def.fqn,
      resource_definition_accession_id=resource_def.accession_id,
      lot_number="L123",
      properties_json={"color": "blue"},
    )
    assert resource is not None
    assert resource.name == name
    assert resource.lot_number == "L123"
    assert resource.properties_json is not None
    assert resource.properties_json.get("color") == "blue"

    # Read back by ID
    read_by_id = await read_resource(db, resource.accession_id)
    assert read_by_id is not None
    assert read_by_id.name == name

    # Read back by name
    read_by_name = await read_resource_by_name(db, name)
    assert read_by_name is not None
    assert read_by_name.accession_id == resource.accession_id

  async def test_create_resource_as_new_machine(
    self,
    db: AsyncSession,
    resource_def: ResourceDefinitionOrm,
  ):
    """Test creating a resource that is also a new machine counterpart."""
    name = f"MachineResource_{uuid.uuid4()}"
    resource = await create_resource(
      db,
      name=name,
      fqn="pylabrobot.liquid_handling.LiquidHandler",
      resource_definition_accession_id=resource_def.accession_id,  # Simplified for test
      is_machine=True,
      machine_fqn="pylabrobot.liquid_handling.LiquidHandler",
      machine_name=name,
    )
    assert resource.is_machine is True
    assert resource.machine_counterpart is not None
    assert resource.machine_counterpart.name == name

  async def test_create_resource_fails_with_bad_definition(self, db: AsyncSession):
    """Test that creating a resource fails if the definition FQN does not exist."""
    with pytest.raises(ValueError, match="not found in catalog"):
      await create_resource(
        db,
        name="BadDefResource",
        fqn="non.existent.definition",
        resource_definition_accession_id=uuid.uuid4(),
      )

  async def test_update_resource(
    self,
    db: AsyncSession,
    existing_resource: ResourceOrm,
  ):
    """Test updating various fields of a resource instance."""
    updated_resource = await update_resource(
      db,
      instance_accession_id=existing_resource.accession_id,
      lot_number="L456",
      physical_location_description="Shelf A",
    )
    assert updated_resource is not None
    assert updated_resource.lot_number == "L456"
    assert updated_resource.physical_location_description == "Shelf A"

  async def test_read_resources_with_filters(
    self,
    db: AsyncSession,
    resource_def: ResourceDefinitionOrm,
    machine: MachineOrm,
  ):
    """Test filtering capabilities of the read_resources function."""
    # Create a diverse set of resources
    await create_resource(
      db,
      f"PlateA_{uuid.uuid4()}",
      resource_def.fqn,
      resource_def.accession_id,
      initial_status=ResourceStatusEnum.IN_USE,
      properties_json={"type": "assay"},
    )
    await create_resource(
      db,
      f"PlateB_{uuid.uuid4()}",
      resource_def.fqn,
      resource_def.accession_id,
      initial_status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
      properties_json={"type": "reagent"},
    )

    # Filter by status
    in_use_resources = await read_resources(
      db,
      status=ResourceStatusEnum.IN_USE,
    )
    assert len(in_use_resources) == 1
    assert in_use_resources[0].current_status == ResourceStatusEnum.IN_USE

    # Filter by FQN
    by_fqn = await read_resources(db, fqn=resource_def.fqn)
    assert len(by_fqn) >= 2

    # Filter by properties
    assay_plates = await read_resources(db, property_filters={"type": "assay"})
    assert len(assay_plates) == 1
    assert assay_plates[0].properties_json is not None
    assert assay_plates[0].properties_json.get("type") == "assay"

  async def test_update_resource_location_and_status(
    self,
    db: AsyncSession,
    existing_resource: ResourceOrm,
    machine: MachineOrm,
    protocol_run: ProtocolRunOrm,
  ):
    """Test the dedicated function for updating location, status, and properties."""
    assert existing_resource.current_status == ResourceStatusEnum.AVAILABLE_IN_STORAGE
    assert existing_resource.properties_json is None

    # Move to machine, set to IN_USE, and update properties
    updated_resource = await update_resource_location_and_status(
      db,
      resource_accession_id=existing_resource.accession_id,
      new_status=ResourceStatusEnum.IN_USE,
      location_machine_accession_id=machine.accession_id,
      current_deck_position_name="A1",
      properties_json_update={"content": "reagent_X"},
      current_protocol_run_accession_id=protocol_run.run_accession_id,
    )

    assert updated_resource is not None
    assert updated_resource.current_status == ResourceStatusEnum.IN_USE
    assert updated_resource.location_machine_accession_id == machine.accession_id
    assert updated_resource.current_deck_position_name == "A1"
    assert updated_resource.properties_json is not None
    assert updated_resource.properties_json["content"] == "reagent_X"
    assert updated_resource.current_protocol_run_accession_id == protocol_run.run_accession_id

    # Now, move it back to storage and merge properties
    back_to_storage = await update_resource_location_and_status(
      db,
      resource_accession_id=existing_resource.accession_id,
      new_status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
      location_machine_accession_id=None,
      current_deck_position_name=None,
      physical_location_description="Fridge 1, Shelf 2",
      properties_json_update={"concentration": "10mM"},
    )

    assert back_to_storage is not None
    assert back_to_storage.current_status == ResourceStatusEnum.AVAILABLE_IN_STORAGE
    assert back_to_storage.location_machine_accession_id is None
    assert back_to_storage.current_protocol_run_accession_id is None
    assert back_to_storage.properties_json is not None
    assert back_to_storage.properties_json["content"] == "reagent_X"
    assert back_to_storage.properties_json["concentration"] == "10mM"

  async def test_delete_resource(
    self,
    db: AsyncSession,
    existing_resource: ResourceOrm,
  ):
    """Test deleting a resource instance by ID and by name."""
    # Delete by ID
    resource_id = existing_resource.accession_id
    result = await delete_resource(db, resource_id)
    assert result is True
    assert await read_resource(db, resource_id) is None
