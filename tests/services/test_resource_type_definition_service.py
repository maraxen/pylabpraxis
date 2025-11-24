import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from pylabrobot.resources import Resource

from praxis.backend.services.resource_type_definition import (
    ResourceTypeDefinitionCRUDService,
    ResourceTypeDefinitionService,
)
from praxis.backend.models.pydantic_internals.resource import (
    ResourceDefinitionCreate,
    ResourceDefinitionUpdate,
)
from praxis.backend.models.orm.resource import ResourceDefinitionOrm

@pytest.fixture
def resource_type_definition_crud_service() -> ResourceTypeDefinitionCRUDService:
    return ResourceTypeDefinitionCRUDService(ResourceDefinitionOrm)

@pytest.fixture
def resource_type_definition_service(db_session: AsyncSession) -> ResourceTypeDefinitionService:
    return ResourceTypeDefinitionService(db_session)

@pytest.mark.asyncio
async def test_crud_resource_type_definition(
    db_session: AsyncSession,
    resource_type_definition_crud_service: ResourceTypeDefinitionCRUDService
) -> None:
    """Test CRUD operations for resource type definition."""

    # Create
    create_data = ResourceDefinitionCreate(
        name="Test Resource",
        fqn="test.resource.Type",
        version="1.0.0",
        description="A test resource",
        size_x_mm=100.0,
        size_y_mm=80.0,
        size_z_mm=15.0
    )
    created_def = await resource_type_definition_crud_service.create(
        db_session, obj_in=create_data
    )

    assert created_def.accession_id is not None
    assert created_def.name == "Test Resource"
    assert created_def.size_x_mm == 100.0

    # Read
    fetched_def = await resource_type_definition_crud_service.get(
        db_session, created_def.accession_id
    )
    assert fetched_def is not None
    assert fetched_def.accession_id == created_def.accession_id

    # Update
    update_data = ResourceDefinitionUpdate(
        description="Updated description"
    )
    updated_def = await resource_type_definition_crud_service.update(
        db_session, db_obj=created_def, obj_in=update_data
    )
    assert updated_def.description == "Updated description"

    # Delete
    await resource_type_definition_crud_service.remove(
        db_session, accession_id=created_def.accession_id
    )
    fetched_def = await resource_type_definition_crud_service.get(
        db_session, created_def.accession_id
    )
    assert fetched_def is None

class MockResourceClass(Resource):
    """Mock PyLabRobot resource class."""
    __module__ = "pylabrobot.resources.plate"
    category = "plate"
    ordering = ["A1", "A2"]
    size_x = 127.0
    size_y = 86.0
    size_z = 14.0
    nominal_volume = 100.0

    def __init__(self, name="mock"):
        super().__init__(name=name, size_x=0, size_y=0, size_z=0, category="plate")

@pytest.mark.asyncio
async def test_discovery_service_helpers(
    resource_type_definition_service: ResourceTypeDefinitionService
) -> None:
    """Test helper methods of ResourceTypeDefinitionService."""

    # Mock inspect.isabstract to return False (MockResourceClass is concrete)
    # No need to patch isclass or issubclass as we inherit from Resource
    assert resource_type_definition_service._can_catalog_resource(MockResourceClass) is True

    assert resource_type_definition_service._get_category_from_plr_class(MockResourceClass) == "plate"
    assert resource_type_definition_service._extract_ordering_from_plr_class(MockResourceClass) == "A1,A2"
    assert resource_type_definition_service._get_short_name_from_plr_class(MockResourceClass) == "MockResourceClass"
    assert resource_type_definition_service._get_size_x_mm_from_plr_class(MockResourceClass) == 127.0
