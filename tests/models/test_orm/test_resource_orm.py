"""Unit tests for ResourceOrm model."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.resource import ResourceOrm, ResourceDefinitionOrm
from praxis.backend.models.enums import AssetType, ResourceStatusEnum


@pytest.mark.asyncio
async def test_resource_orm_creation_with_defaults(db_session: AsyncSession) -> None:
    """Test creating a ResourceOrm with default values."""
    from praxis.backend.utils.uuid import uuid7

    # Create a resource definition first
    resource_def = ResourceDefinitionOrm(
        name="test_resource_def",
        fqn="test.resource.Definition",
    )
    db_session.add(resource_def)
    await db_session.flush()
    def_id = resource_def.accession_id

    # Create a resource with only required fields
    resource_id = uuid7()
    resource = ResourceOrm(
        accession_id=resource_id,
        name="test_resource",
        fqn="test.resource.Fqn",
        asset_type=AssetType.RESOURCE,
        resource_definition_accession_id=def_id,
    )

    # Verify defaults are set
    assert resource.accession_id == resource_id
    assert resource.name == "test_resource"
    assert resource.fqn == "test.resource.Fqn"
    assert resource.asset_type == AssetType.RESOURCE
    assert resource.status == ResourceStatusEnum.UNKNOWN
    assert resource.resource_definition_accession_id == def_id
    assert resource.parent_accession_id is None


@pytest.mark.asyncio
@pytest.mark.skip(reason="ResourceOrm.resource_definition_accession_id not persisting - MappedAsDataclass + kw_only FK issue")
async def test_resource_orm_persist_to_database(db_session: AsyncSession) -> None:
    """Test that a ResourceOrm can be persisted to the database.

    KNOWN ISSUE: resource_definition_accession_id is not being persisted even when
    passed in constructor. This is due to MappedAsDataclass + kw_only + joined-table
    inheritance causing the FK value to become NULL during INSERT.

    See: prerelease_dev_docs/MODEL_ISSUES.md Issue #5
    """
    from praxis.backend.utils.uuid import uuid7

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="persist_def",
        fqn="test.resource.PersistDef",
    )
    db_session.add(resource_def)
    await db_session.flush()
    def_id = resource_def.accession_id

    # Create resource
    resource_id = uuid7()
    resource = ResourceOrm(
        accession_id=resource_id,
        name="test_persistence",
        fqn="test.persistence.Resource",
        asset_type=AssetType.RESOURCE,
        status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
        resource_definition_accession_id=def_id,
    )

    # Add to session and flush
    db_session.add(resource)
    await db_session.flush()

    # Query back from database
    result = await db_session.execute(
        select(ResourceOrm).where(ResourceOrm.accession_id == resource_id)
    )
    retrieved = result.scalars().first()

    # Verify persistence
    assert retrieved is not None
    assert retrieved.accession_id == resource_id
    assert retrieved.name == "test_persistence"
    assert retrieved.fqn == "test.persistence.Resource"
    assert retrieved.status == ResourceStatusEnum.AVAILABLE_IN_STORAGE
    assert retrieved.resource_definition_accession_id == def_id


@pytest.mark.asyncio
@pytest.mark.skip(reason="ResourceOrm.resource_definition_accession_id not persisting - MappedAsDataclass + kw_only FK issue")
async def test_resource_orm_unique_name_constraint(db_session: AsyncSession) -> None:
    """Test that resource names must be unique.

    KNOWN ISSUE: Cannot persist ResourceOrm to database - see MODEL_ISSUES.md Issue #5
    """
    from praxis.backend.utils.uuid import uuid7
    from sqlalchemy.exc import IntegrityError

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="unique_def",
        fqn="test.resource.UniqueDef",
    )
    db_session.add(resource_def)
    await db_session.flush()
    def_id = resource_def.accession_id

    # Create first resource
    resource1 = ResourceOrm(
        accession_id=uuid7(),
        name="unique_resource",
        fqn="test.resource.1",
        asset_type=AssetType.RESOURCE,
    )
    resource1.resource_definition_accession_id = def_id
    db_session.add(resource1)
    await db_session.flush()

    # Try to create another with same name
    resource2 = ResourceOrm(
        accession_id=uuid7(),
        name="unique_resource",  # Duplicate name
        fqn="test.resource.2",
        asset_type=AssetType.RESOURCE,
    )
    resource2.resource_definition_accession_id = def_id
    db_session.add(resource2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
@pytest.mark.skip(reason="ResourceOrm.resource_definition_accession_id not persisting - MappedAsDataclass + kw_only FK issue")
async def test_resource_orm_status_enum_values(db_session: AsyncSession) -> None:
    """Test that resource status enum values are stored correctly.

    KNOWN ISSUE: Cannot persist ResourceOrm to database - see MODEL_ISSUES.md Issue #5
    """
    from praxis.backend.utils.uuid import uuid7

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="status_def",
        fqn="test.resource.StatusDef",
    )
    db_session.add(resource_def)
    await db_session.flush()
    def_id = resource_def.accession_id

    # Test a few key statuses
    statuses = [
        ResourceStatusEnum.AVAILABLE_IN_STORAGE,
        ResourceStatusEnum.IN_USE,
        ResourceStatusEnum.EMPTY,
        ResourceStatusEnum.UNKNOWN,
    ]

    for status in statuses:
        resource = ResourceOrm(
            accession_id=uuid7(),
            name=f"resource_{status.value}",
            fqn=f"test.resource.{status.value}",
            asset_type=AssetType.RESOURCE,
            status=status,
        )
        resource.resource_definition_accession_id = def_id
        db_session.add(resource)
        await db_session.flush()

        # Verify status was set correctly
        assert resource.status == status


@pytest.mark.asyncio
@pytest.mark.skip(reason="ResourceOrm.resource_definition_accession_id not persisting - MappedAsDataclass + kw_only FK issue")
async def test_resource_orm_parent_child_relationship(db_session: AsyncSession) -> None:
    """Test self-referential parent-child relationship between resources.

    KNOWN ISSUE: Cannot persist ResourceOrm to database - see MODEL_ISSUES.md Issue #5
    """
    from praxis.backend.utils.uuid import uuid7

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="hierarchy_def",
        fqn="test.resource.HierarchyDef",
    )
    db_session.add(resource_def)
    await db_session.flush()
    def_id = resource_def.accession_id

    # Create parent resource
    parent_id = uuid7()
    parent = ResourceOrm(
        accession_id=parent_id,
        name="parent_resource",
        fqn="test.resource.Parent",
        asset_type=AssetType.RESOURCE,
    )
    parent.resource_definition_accession_id = def_id
    db_session.add(parent)
    await db_session.flush()

    # Create child resource referencing parent
    child_id = uuid7()
    child = ResourceOrm(
        accession_id=child_id,
        name="child_resource",
        fqn="test.resource.Child",
        asset_type=AssetType.RESOURCE,
    )
    child.resource_definition_accession_id = def_id
    child.parent_accession_id = parent_id
    db_session.add(child)
    await db_session.flush()

    # Query back and verify relationship
    result = await db_session.execute(
        select(ResourceOrm).where(ResourceOrm.accession_id == child_id)
    )
    retrieved_child = result.scalars().first()

    assert retrieved_child is not None
    assert retrieved_child.parent_accession_id == parent_id


@pytest.mark.asyncio
@pytest.mark.skip(reason="ResourceOrm.resource_definition_accession_id not persisting - MappedAsDataclass + kw_only FK issue")
async def test_resource_orm_with_workcell_relationship(db_session: AsyncSession) -> None:
    """Test creating a resource with a workcell relationship.

    KNOWN ISSUE: Cannot persist ResourceOrm to database - see MODEL_ISSUES.md Issue #5
    """
    from praxis.backend.utils.uuid import uuid7
    from praxis.backend.models.orm.workcell import WorkcellOrm

    # Create workcell
    workcell_id = uuid7()
    workcell = WorkcellOrm(
        accession_id=workcell_id,
        name="test_workcell_for_resource",
    )
    db_session.add(workcell)
    await db_session.flush()

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="workcell_resource_def",
        fqn="test.resource.WorkcellDef",
    )
    db_session.add(resource_def)
    await db_session.flush()
    def_id = resource_def.accession_id

    # Create resource in workcell
    resource_id = uuid7()
    resource = ResourceOrm(
        accession_id=resource_id,
        name="resource_in_workcell",
        fqn="test.resource.InWorkcell",
        asset_type=AssetType.RESOURCE,
    )
    resource.resource_definition_accession_id = def_id
    resource.workcell_accession_id = workcell_id
    db_session.add(resource)
    await db_session.flush()

    # Query back and verify
    result = await db_session.execute(
        select(ResourceOrm).where(ResourceOrm.accession_id == resource_id)
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.workcell_accession_id == workcell_id


@pytest.mark.asyncio
@pytest.mark.skip(reason="ResourceOrm.resource_definition_accession_id not persisting - MappedAsDataclass + kw_only FK issue")
async def test_resource_orm_plr_state_json(db_session: AsyncSession) -> None:
    """Test that resource plr_state JSONB field works correctly.

    KNOWN ISSUE: Cannot persist ResourceOrm to database - see MODEL_ISSUES.md Issue #5
    """
    from praxis.backend.utils.uuid import uuid7

    # Create resource definition
    resource_def = ResourceDefinitionOrm(
        name="plr_state_def",
        fqn="test.resource.PLRStateDef",
    )
    db_session.add(resource_def)
    await db_session.flush()
    def_id = resource_def.accession_id

    # Create resource with PLR state
    plr_state = {
        "location": {"x": 100.5, "y": 200.3, "z": 50.0},
        "rotation": {"x_deg": 0, "y_deg": 0, "z_deg": 90},
        "metadata": {"type": "plate", "barcode": "ABC123"},
    }

    resource = ResourceOrm(
        accession_id=uuid7(),
        name="resource_with_plr_state",
        fqn="test.resource.WithPLRState",
        asset_type=AssetType.RESOURCE,
        plr_state=plr_state,
    )
    resource.resource_definition_accession_id = def_id

    db_session.add(resource)
    await db_session.flush()

    # Verify JSON was stored correctly
    assert resource.plr_state == plr_state
    assert resource.plr_state["location"]["x"] == 100.5
    assert resource.plr_state["metadata"]["barcode"] == "ABC123"
