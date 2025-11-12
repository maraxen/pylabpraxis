"""Unit tests for Resource Pydantic models."""
import json
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.pydantic_internals.resource import (
    ResourceBase,
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
)
from praxis.backend.models.enums import (
    AssetType,
    ResourceStatusEnum,
)
from praxis.backend.models.orm.resource import ResourceOrm, ResourceDefinitionOrm


def test_resource_base_minimal() -> None:
    """Test creating a ResourceBase with minimal required fields."""
    resource = ResourceBase(
        name="test_resource",
        asset_type=AssetType.RESOURCE,
    )

    assert resource.name == "test_resource"
    assert resource.asset_type == "RESOURCE"  # Enum stored as string
    assert resource.status == ResourceStatusEnum.UNKNOWN
    assert resource.fqn is None
    assert resource.resource_definition_accession_id is None
    assert resource.parent_accession_id is None


def test_resource_base_with_all_fields() -> None:
    """Test creating a ResourceBase with all fields populated."""
    plr_state = {"location": {"x": 100, "y": 200}, "rotation": {"z_deg": 90}}

    resource = ResourceBase(
        name="full_resource",
        fqn="test.full.Resource",
        asset_type=AssetType.RESOURCE,
        status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
        status_details="Ready to use",
        resource_definition_accession_id="019a6f00-0000-7000-8000-000000000001",
        parent_accession_id="019a6f00-0000-7000-8000-000000000002",
        workcell_accession_id="019a6f00-0000-7000-8000-000000000003",
        plr_state=plr_state,
    )

    assert resource.name == "full_resource"
    assert resource.fqn == "test.full.Resource"
    assert resource.asset_type == "RESOURCE"
    assert resource.status == "available_in_storage"  # use_enum_values=True
    assert resource.status_details == "Ready to use"
    assert resource.resource_definition_accession_id is not None
    assert resource.parent_accession_id is not None
    assert resource.workcell_accession_id is not None
    assert resource.plr_state == plr_state


def test_resource_create_inherits_from_base() -> None:
    """Test that ResourceCreate inherits all properties from ResourceBase."""
    resource = ResourceCreate(
        name="create_test",
        fqn="test.create.Resource",
        asset_type=AssetType.RESOURCE,
        status=ResourceStatusEnum.EMPTY,
    )

    assert resource.name == "create_test"
    assert resource.fqn == "test.create.Resource"
    assert resource.asset_type == "RESOURCE"
    assert resource.status == "empty"


def test_resource_update_all_fields_optional() -> None:
    """Test that ResourceUpdate allows all fields to be optional.

    Note: ResourceUpdate inherits from ResourceBase and AssetUpdate.
    For updates, fields should typically be optional or have defaults.
    """
    # Create with minimal fields
    update = ResourceUpdate(asset_type=AssetType.RESOURCE)
    assert update.asset_type == "RESOURCE"
    assert update.name is not None  # Auto-generated from UUID

    # Should be able to create with partial fields
    update_partial = ResourceUpdate(
        asset_type=AssetType.RESOURCE,
        name="new_name",
        status=ResourceStatusEnum.IN_USE,
    )
    assert update_partial.asset_type == "RESOURCE"
    assert update_partial.name == "new_name"
    assert update_partial.status == "in_use"


def test_resource_response_serialization_to_dict() -> None:
    """Test that ResourceResponse can be serialized to a dictionary."""
    resource = ResourceResponse(
        name="serialize_test",
        fqn="test.serialize.Resource",
        asset_type=AssetType.RESOURCE,
        status=ResourceStatusEnum.AVAILABLE_ON_DECK,
    )

    data = resource.model_dump()

    assert isinstance(data, dict)
    assert data["name"] == "serialize_test"
    assert data["fqn"] == "test.serialize.Resource"
    assert data["asset_type"] == "RESOURCE"  # Enum to string
    assert data["status"] == "available_on_deck"  # Enum to string


def test_resource_response_serialization_to_json() -> None:
    """Test that ResourceResponse can be serialized to JSON."""
    resource = ResourceResponse(
        name="json_test",
        fqn="test.json.Resource",
        asset_type=AssetType.RESOURCE,
        status=ResourceStatusEnum.IN_USE,
    )

    json_str = resource.model_dump_json()

    assert isinstance(json_str, str)
    data = json.loads(json_str)
    assert data["name"] == "json_test"
    assert data["fqn"] == "test.json.Resource"
    assert data["asset_type"] == "RESOURCE"
    assert data["status"] == "in_use"


def test_resource_response_deserialization_from_dict() -> None:
    """Test that ResourceResponse can be deserialized from a dictionary."""
    data = {
        "name": "deserialize_test",
        "fqn": "test.deserialize.Resource",
        "asset_type": "RESOURCE",
        "status": "available_in_storage",
        "status_details": "From dict",
        "resource_definition_accession_id": "019a6f00-1234-7000-8000-111111111111",
        "parent_accession_id": "019a6f00-1234-7000-8000-222222222222",
        "accession_id": "019a6f00-1234-7000-8000-333333333333",
        "created_at": "2025-11-10T12:00:00Z",
        "properties_json": {},
    }

    resource = ResourceResponse.model_validate(data)

    assert resource.name == "deserialize_test"
    assert resource.fqn == "test.deserialize.Resource"
    assert resource.asset_type == "RESOURCE"
    assert resource.status == "available_in_storage"
    assert resource.status_details == "From dict"
    assert resource.resource_definition_accession_id is not None
    assert resource.parent_accession_id is not None


def test_resource_response_status_enum_validation() -> None:
    """Test that ResourceResponse properly validates status enum values."""
    # Valid enum value as string
    resource1 = ResourceResponse(
        name="enum_test_1",
        fqn="test.enum.1",
        asset_type=AssetType.RESOURCE,
        status="available_in_storage",
    )
    assert resource1.status == "available_in_storage"

    # Valid enum value as enum
    resource2 = ResourceResponse(
        name="enum_test_2",
        fqn="test.enum.2",
        asset_type=AssetType.RESOURCE,
        status=ResourceStatusEnum.IN_USE,
    )
    assert resource2.status == "in_use"

    # Invalid enum value should raise error
    with pytest.raises(ValueError):
        ResourceResponse(
            name="enum_test_3",
            fqn="test.enum.3",
            asset_type=AssetType.RESOURCE,
            status="invalid_status",
        )


def test_resource_response_roundtrip_serialization() -> None:
    """Test that ResourceResponse can be serialized and deserialized without data loss."""
    original = ResourceResponse(
        name="roundtrip_test",
        fqn="test.roundtrip.Resource",
        asset_type=AssetType.RESOURCE,
        status=ResourceStatusEnum.EMPTY,
        status_details="Testing roundtrip",
        resource_definition_accession_id="019a6f00-1234-7000-8000-444444444444",
        plr_state={"test": "data", "nested": {"value": 123}},
    )

    # Serialize to dict
    data = original.model_dump()

    # Deserialize back
    restored = ResourceResponse.model_validate(data)

    # Should be equal
    assert restored.name == original.name
    assert restored.fqn == original.fqn
    assert restored.asset_type == original.asset_type
    assert restored.status == original.status
    assert restored.status_details == original.status_details
    assert restored.resource_definition_accession_id == original.resource_definition_accession_id
    assert restored.plr_state == original.plr_state


@pytest.mark.asyncio
async def test_resource_response_from_orm(db_session: AsyncSession) -> None:
    """Test converting a ResourceOrm instance to ResourceResponse (critical for API layer).

    This validates that models inheriting from AssetOrm (with fqn field)
    can be successfully converted to their Pydantic response models.
    """
    from praxis.backend.utils.uuid import uuid7

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="orm_test_def",
        fqn="test.orm.Definition",
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Create an ORM instance
    resource_id = uuid7()
    orm_resource = ResourceOrm(
        accession_id=resource_id,
        name="orm_test_resource",
        fqn="test.orm.Resource",
        asset_type=AssetType.RESOURCE,
        status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
    )
    orm_resource.resource_definition = resource_def

    db_session.add(orm_resource)
    await db_session.flush()

    # Convert ORM to Pydantic using model_validate with from_attributes=True
    response = ResourceResponse.model_validate(orm_resource)

    # Verify all fields are correctly converted
    assert response.accession_id == resource_id
    assert response.name == "orm_test_resource"
    assert response.fqn == "test.orm.Resource"  # fqn IS present for Assets
    assert response.asset_type == "RESOURCE"  # Enum converted to string
    assert response.status == "available_in_storage"  # Enum converted to string value
    assert response.resource_definition_accession_id == resource_def.accession_id


@pytest.mark.asyncio
async def test_resource_response_from_orm_minimal(db_session: AsyncSession) -> None:
    """Test ORM-to-Pydantic conversion with minimal fields."""
    from praxis.backend.utils.uuid import uuid7

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="minimal_def",
        fqn="test.minimal.Definition",
    )
    db_session.add(resource_def)
    await db_session.flush()

    # Create minimal ORM instance
    resource_id = uuid7()
    orm_resource = ResourceOrm(
        accession_id=resource_id,
        name="minimal_resource",
        fqn="test.minimal.Resource",
        asset_type=AssetType.RESOURCE,
    )
    orm_resource.resource_definition = resource_def

    db_session.add(orm_resource)
    await db_session.flush()

    # Convert to Pydantic
    response = ResourceResponse.model_validate(orm_resource)

    # Verify required fields
    assert response.accession_id == resource_id
    assert response.name == "minimal_resource"
    assert response.fqn == "test.minimal.Resource"
    assert response.asset_type == "RESOURCE"
    assert response.status == "unknown"  # Default status

    # Verify optional fields are None or default
    assert response.status_details is None
    assert response.parent_accession_id is None
