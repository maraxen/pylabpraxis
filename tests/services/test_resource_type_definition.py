import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import all required models from the central package
from praxis.backend.models import (
  ResourceDefinitionCatalogOrm,
)

# Import the service functions to be tested
from praxis.backend.services import (
  create_resource_definition,
  create_resource_instance,  # Also needed for a deletion test
  delete_resource_definition,
  list_resource_definitions,
  read_resource_definition,
  read_resource_definition_by_fqn,
  update_resource_definition,
)

# --- Pytest Fixtures ---


@pytest.fixture
async def existing_def(db: AsyncSession) -> ResourceDefinitionCatalogOrm:
  """Fixture that creates a standard resource definition for testing."""
  name = f"tip_rack_1000ul_{uuid.uuid4()}"
  return await create_resource_definition(
    db,
    name=name,
    python_fqn=f"pylabrobot.resources.{name}",
    manufacturer="PraxisTestCo",
    is_consumable=True,
  )


pytestmark = pytest.mark.asyncio


class TestResourceDefinitionService:
  """Test suite for the Resource Definition service layer."""

  async def test_create_and_read_resource_definition(self, db: AsyncSession):
    """Test creating a resource definition and reading it back by name and FQN."""
    name = f"plate_96_deep_well_{uuid.uuid4()}"
    fqn = f"pylabrobot.resources.Plate.{name}"

    created_def = await create_resource_definition(
      db,
      name=name,
      python_fqn=fqn,
      resource_type="96-Well Deep Well Plate",
      description="A standard 96-well deep well plate.",
      manufacturer="Corning",
      is_consumable=True,
      nominal_volume_ul=2000.0,
    )
    assert created_def is not None
    assert created_def.name == name
    assert created_def.manufacturer == "Corning"

    # Test reading by name
    read_by_name = await read_resource_definition(db, name)
    assert read_by_name is not None
    assert read_by_name.accession_id == created_def.accession_id

    # Test reading by FQN
    read_by_fqn = await read_resource_definition_by_fqn(db, fqn)
    assert read_by_fqn is not None
    assert read_by_fqn.accession_id == created_def.accession_id

  async def test_create_definition_fails_on_duplicate_name(
    self, db: AsyncSession, existing_def: ResourceDefinitionCatalogOrm,
  ):
    """Test that creating a definition with a duplicate name raises ValueError."""
    with pytest.raises(ValueError, match="already exists"):
      await create_resource_definition(
        db, name=existing_def.name, python_fqn="some.other.fqn",
      )

  async def test_update_resource_definition(
    self, db: AsyncSession, existing_def: ResourceDefinitionCatalogOrm,
  ):
    """Test updating various fields of a resource definition."""
    new_description = "An updated description for this tip rack."
    new_details = {"tip_length": 95.5}

    updated_def = await update_resource_definition(
      db,
      name=existing_def.name,
      description=new_description,
      is_consumable=False,  # Change a boolean field
      plr_definition_details_json=new_details,
    )

    assert updated_def is not None
    assert updated_def.accession_id == existing_def.accession_id
    assert updated_def.description == new_description
    assert updated_def.is_consumable is False
    assert updated_def.plr_definition_details_json is not None
    assert updated_def.plr_definition_details_json.get("tip_length") == 95.5

  async def test_update_non_existent_definition_fails(self, db: AsyncSession):
    """Test that updating a non-existent definition raises ValueError."""
    with pytest.raises(ValueError, match="not found for update"):
      await update_resource_definition(
        db, name="non-existent-def-name", description="new desc",
      )

  async def test_list_resource_definitions_with_filters(
    self, db: AsyncSession, existing_def: ResourceDefinitionCatalogOrm,
  ):
    """Test the filtering capabilities of the list_resource_definitions function."""
    # Create another definition for robust filtering
    await create_resource_definition(
      db,
      name=f"trough_{uuid.uuid4()}",
      python_fqn="pylabrobot.resources.Trough",
      manufacturer="Axygen",
      is_consumable=False,
    )

    # Filter by manufacturer (case-insensitive partial)
    praxis_defs = await list_resource_definitions(db, manufacturer="praxistest")
    assert len(praxis_defs) == 1
    assert praxis_defs[0].name == existing_def.name

    # Filter by is_consumable=True
    consumables = await list_resource_definitions(db, is_consumable=True)
    assert len(consumables) == 1
    assert consumables[0].is_consumable is True

    # Filter by is_consumable=False
    non_consumables = await list_resource_definitions(db, is_consumable=False)
    assert len(non_consumables) == 1
    assert non_consumables[0].manufacturer == "Axygen"

    # Test pagination
    all_defs = await list_resource_definitions(db, limit=1)
    assert len(all_defs) == 1

  async def test_delete_resource_definition_success(self, db: AsyncSession):
    """Test successfully deleting an unused resource definition."""
    def_to_delete = await create_resource_definition(
      db, name=f"def_to_delete_{uuid.uuid4()}", python_fqn="to.delete.fqn",
    )

    result = await delete_resource_definition(db, def_to_delete.name)
    assert result is True

    # Verify it's gone
    assert await read_resource_definition(db, def_to_delete.name) is None

  async def test_delete_resource_definition_fails_if_in_use(
    self, db: AsyncSession, existing_def: ResourceDefinitionCatalogOrm,
  ):
    """Test that deleting a definition fails if it's used by a resource instance."""
    # Create a resource instance that uses the definition
    await create_resource_instance(
      db,
      user_assigned_name=f"instance_using_{existing_def.name}",
      python_fqn=existing_def.python_fqn,
      resource_definition_accession_id=existing_def.accession_id,
    )

    # Attempting to delete the definition should now fail
    with pytest.raises(ValueError, match="due to existing references"):
      await delete_resource_definition(db, existing_def.name)
