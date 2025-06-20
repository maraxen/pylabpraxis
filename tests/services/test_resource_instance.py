import datetime
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import all required models from the central package
from praxis.backend.models import (
  MachineOrm,
  MachineStatusEnum,
  ProtocolRunOrm,
  ResourceDefinitionCatalogOrm,
  ResourceInstanceOrm,
  ResourceInstanceStatusEnum,
)

# Import the service functions to be tested
from praxis.backend.services import (
  create_resource_instance,
  delete_resource_instance,
  list_resource_instances,
  read_resource_instance,
  read_resource_instance_by_name,
  update_resource_instance,
  update_resource_instance_location_and_status,
)

# --- Pytest Fixtures ---


@pytest.fixture
async def resource_def(db: AsyncSession) -> ResourceDefinitionCatalogOrm:
  """Fixture for a ResourceDefinitionCatalogOrm (e.g., a plate definition)."""
  definition = ResourceDefinitionCatalogOrm(
    name=f"corning_96_wellplate_360ul_flat_{uuid.uuid4()}",
    python_fqn="pylabrobot.resources.corning_96_wellplate_360ul_flat",
    category="plate",
  )
  db.add(definition)
  await db.commit()
  return definition


@pytest.fixture
async def machine(db: AsyncSession) -> MachineOrm:
  """Fixture for a MachineOrm to use for location and counterpart tests."""
  m = MachineOrm(
    user_friendly_name=f"TestMachine_{uuid.uuid4()}", python_fqn="machine.fqn"
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
  db: AsyncSession, resource_def: ResourceDefinitionCatalogOrm
) -> ResourceInstanceOrm:
  """Fixture that creates a standard resource instance for testing."""
  return await create_resource_instance(
    db,
    user_assigned_name=f"TestPlate_{uuid.uuid4()}",
    python_fqn=resource_def.python_fqn,
    resource_definition_accession_id=resource_def.accession_id,
  )


pytestmark = pytest.mark.asyncio


class TestResourceInstanceService:
  """Test suite for the Resource Instance service layer."""

  async def test_create_and_read_resource_instance(
    self, db: AsyncSession, resource_def: ResourceDefinitionCatalogOrm
  ):
    """Test creating a simple resource and reading it back by ID and name."""
    name = f"MyPlate_{uuid.uuid4()}"
    resource = await create_resource_instance(
      db,
      user_assigned_name=name,
      python_fqn=resource_def.python_fqn,
      resource_definition_accession_id=resource_def.accession_id,
      lot_number="L123",
      properties_json={"color": "blue"},
    )
    assert resource is not None
    assert resource.user_assigned_name == name
    assert resource.lot_number == "L123"
    assert resource.properties_json is not None
    assert resource.properties_json.get("color") == "blue"

    # Read back by ID
    read_by_id = await read_resource_instance(db, resource.accession_id)
    assert read_by_id is not None
    assert read_by_id.user_assigned_name == name

    # Read back by name
    read_by_name = await read_resource_instance_by_name(db, name)
    assert read_by_name is not None
    assert read_by_name.accession_id == resource.accession_id

  async def test_create_resource_as_new_machine(
    self, db: AsyncSession, resource_def: ResourceDefinitionCatalogOrm
  ):
    """Test creating a resource that is also a new machine counterpart."""
    name = f"MachineResource_{uuid.uuid4()}"
    resource = await create_resource_instance(
      db,
      user_assigned_name=name,
      python_fqn="pylabrobot.liquid_handling.LiquidHandler",
      resource_definition_accession_id=resource_def.accession_id,  # Simplified for test
      is_machine=True,
      machine_python_fqn="pylabrobot.liquid_handling.LiquidHandler",
      machine_user_friendly_name=name,
    )
    assert resource.is_machine is True
    assert resource.machine_counterpart is not None
    assert resource.machine_counterpart.user_friendly_name == name

  async def test_create_resource_fails_with_bad_definition(self, db: AsyncSession):
    """Test that creating a resource fails if the definition FQN does not exist."""
    with pytest.raises(ValueError, match="not found in catalog"):
      await create_resource_instance(
        db,
        user_assigned_name="BadDefResource",
        python_fqn="non.existent.definition",
        resource_definition_accession_id=uuid.uuid4(),
      )

  async def test_update_resource_instance(
    self, db: AsyncSession, existing_resource: ResourceInstanceOrm
  ):
    """Test updating various fields of a resource instance."""
    updated_resource = await update_resource_instance(
      db,
      instance_accession_id=existing_resource.accession_id,
      lot_number="L456",
      physical_location_description="Shelf A",
    )
    assert updated_resource is not None
    assert updated_resource.lot_number == "L456"
    assert updated_resource.physical_location_description == "Shelf A"

  async def test_list_resource_instances_with_filters(
    self,
    db: AsyncSession,
    resource_def: ResourceDefinitionCatalogOrm,
    machine: MachineOrm,
  ):
    """Test filtering capabilities of the list_resource_instances function."""
    # Create a diverse set of resources
    await create_resource_instance(
      db,
      f"PlateA_{uuid.uuid4()}",
      resource_def.python_fqn,
      resource_def.accession_id,
      initial_status=ResourceInstanceStatusEnum.IN_USE,
      properties_json={"type": "assay"},
    )
    await create_resource_instance(
      db,
      f"PlateB_{uuid.uuid4()}",
      resource_def.python_fqn,
      resource_def.accession_id,
      initial_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
      properties_json={"type": "reagent"},
    )

    # Filter by status
    in_use_resources = await list_resource_instances(
      db, status=ResourceInstanceStatusEnum.IN_USE
    )
    assert len(in_use_resources) == 1
    assert in_use_resources[0].current_status == ResourceInstanceStatusEnum.IN_USE

    # Filter by FQN
    by_fqn = await list_resource_instances(db, python_fqn=resource_def.python_fqn)
    assert len(by_fqn) >= 2

    # Filter by properties
    assay_plates = await list_resource_instances(db, property_filters={"type": "assay"})
    assert len(assay_plates) == 1
    assert assay_plates[0].properties_json is not None
    assert assay_plates[0].properties_json.get("type") == "assay"

  async def test_update_resource_location_and_status(
    self,
    db: AsyncSession,
    existing_resource: ResourceInstanceOrm,
    machine: MachineOrm,
    protocol_run: ProtocolRunOrm,
  ):
    """Test the dedicated function for updating location, status, and properties."""
    assert (
      existing_resource.current_status
      == ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE
    )
    assert existing_resource.properties_json is None

    # Move to machine, set to IN_USE, and update properties
    updated_resource = await update_resource_instance_location_and_status(
      db,
      resource_instance_accession_id=existing_resource.accession_id,
      new_status=ResourceInstanceStatusEnum.IN_USE,
      location_machine_accession_id=machine.accession_id,
      current_deck_position_name="A1",
      properties_json_update={"content": "reagent_X"},
      current_protocol_run_accession_id=protocol_run.run_accession_id,
    )

    assert updated_resource is not None
    assert updated_resource.current_status == ResourceInstanceStatusEnum.IN_USE
    assert updated_resource.location_machine_accession_id == machine.accession_id
    assert updated_resource.current_deck_position_name == "A1"
    assert updated_resource.properties_json is not None
    assert updated_resource.properties_json["content"] == "reagent_X"
    assert (
      updated_resource.current_protocol_run_accession_id
      == protocol_run.run_accession_id
    )

    # Now, move it back to storage and merge properties
    back_to_storage = await update_resource_instance_location_and_status(
      db,
      resource_instance_accession_id=existing_resource.accession_id,
      new_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
      location_machine_accession_id=None,
      current_deck_position_name=None,
      physical_location_description="Fridge 1, Shelf 2",
      properties_json_update={"concentration": "10mM"},
    )

    assert back_to_storage is not None
    assert (
      back_to_storage.current_status == ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE
    )
    assert back_to_storage.location_machine_accession_id is None
    assert back_to_storage.current_protocol_run_accession_id is None
    assert back_to_storage.properties_json is not None
    assert back_to_storage.properties_json["content"] == "reagent_X"
    assert back_to_storage.properties_json["concentration"] == "10mM"

  async def test_delete_resource_instance(
    self, db: AsyncSession, existing_resource: ResourceInstanceOrm
  ):
    """Test deleting a resource instance by ID and by name."""
    # Delete by ID
    resource_id = existing_resource.accession_id
    result = await delete_resource_instance(db, resource_id)
    assert result is True
    assert await read_resource_instance(db, resource_id) is None
