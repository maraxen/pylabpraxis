"""Unit tests for Machine Pydantic models."""
import json

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import (
    AssetType,
    MachineStatusEnum,
)
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.pydantic_internals.machine import (
    MachineBase,
    MachineCreate,
    MachineResponse,
    MachineUpdate,
)


def test_machine_base_minimal() -> None:
    """Test creating a MachineBase with minimal required fields."""
    machine = MachineBase(
        name="test_machine",
        asset_type=AssetType.MACHINE,
    )

    assert machine.name == "test_machine"
    assert machine.asset_type == "MACHINE"  # Enum stored as string
    # Note: MachineStatusEnum NOT converted to string (different from WorkcellStatusEnum)
    assert machine.status == MachineStatusEnum.OFFLINE
    assert machine.description is None
    assert machine.manufacturer is None
    assert machine.model is None


def test_machine_base_with_all_fields() -> None:
    """Test creating a MachineBase with all fields populated."""
    connection_info = {"backend": "hamilton", "address": "192.168.1.100"}

    machine = MachineBase(
        name="full_machine",
        fqn="test.full.Machine",
        asset_type=AssetType.MACHINE,
        status=MachineStatusEnum.AVAILABLE,
        description="A fully configured machine",
        manufacturer="Test Corp",
        model="Model X",
        serial_number="SN12345",
        connection_info=connection_info,
        is_simulation_override=False,
    )

    assert machine.name == "full_machine"
    assert machine.fqn == "test.full.Machine"
    assert machine.asset_type == "MACHINE"
    # use_enum_values=True means enum is stored as string value
    assert machine.status == MachineStatusEnum.AVAILABLE.value
    assert machine.description == "A fully configured machine"
    assert machine.manufacturer == "Test Corp"
    assert machine.model == "Model X"
    assert machine.serial_number == "SN12345"
    assert machine.connection_info == connection_info
    assert machine.is_simulation_override is False


def test_machine_create_inherits_from_base() -> None:
    """Test that MachineCreate inherits all properties from MachineBase."""
    machine = MachineCreate(
        name="create_test",
        fqn="test.create.Machine",
        asset_type=AssetType.MACHINE,
        description="Testing create model",
    )

    assert machine.name == "create_test"
    assert machine.fqn == "test.create.Machine"
    assert machine.asset_type == "MACHINE"
    assert machine.description == "Testing create model"
    # MachineStatusEnum stored as enum object, not string
    assert machine.status == MachineStatusEnum.OFFLINE


def test_machine_update_all_fields_optional() -> None:
    """Test that MachineUpdate allows all fields to be optional.

    Note: MachineUpdate inherits from AssetBase which requires asset_type.
    For updates, asset_type should typically not change, but must be provided.
    """
    # Create with minimal required field (asset_type)
    # Note: name has default_factory in PraxisBaseModel, so it's auto-generated
    update = MachineUpdate(asset_type=AssetType.MACHINE)
    # assert update.asset_type == "MACHINE"  # MachineUpdate does not strictly define asset_type field
    assert update.name is None  # Default is None
    assert update.description is None
    assert update.status is None

    # Should be able to create with partial fields
    update_partial = MachineUpdate(
        asset_type=AssetType.MACHINE,
        name="new_name",
        status=MachineStatusEnum.MAINTENANCE,
    )
    # assert update_partial.asset_type == "MACHINE"
    assert update_partial.name == "new_name"
    assert update_partial.status == "MAINTENANCE"
    assert update_partial.description is None


def test_machine_response_serialization_to_dict() -> None:
    """Test that MachineResponse can be serialized to a dictionary."""
    machine = MachineResponse(
        name="serialize_test",
        fqn="test.serialize.Machine",
        asset_type=AssetType.MACHINE,
        description="Testing serialization",
        status=MachineStatusEnum.MAINTENANCE,
    )

    data = machine.model_dump()

    assert isinstance(data, dict)
    assert data["name"] == "serialize_test"
    assert data["fqn"] == "test.serialize.Machine"
    assert data["asset_type"] == "MACHINE"  # Enum to string
    assert data["description"] == "Testing serialization"
    assert data["status"] == "MAINTENANCE"  # Enum to string


def test_machine_response_serialization_to_json() -> None:
    """Test that MachineResponse can be serialized to JSON."""
    machine = MachineResponse(
        name="json_test",
        fqn="test.json.Machine",
        asset_type=AssetType.MACHINE,
        status=MachineStatusEnum.ERROR,
    )

    json_str = machine.model_dump_json()

    assert isinstance(json_str, str)
    data = json.loads(json_str)
    assert data["name"] == "json_test"
    assert data["fqn"] == "test.json.Machine"
    assert data["asset_type"] == "MACHINE"
    assert data["status"] == "ERROR"


def test_machine_response_deserialization_from_dict() -> None:
    """Test that MachineResponse can be deserialized from a dictionary."""
    data = {
        "name": "deserialize_test",
        "fqn": "test.deserialize.Machine",
        "asset_type": "MACHINE",
        "description": "From dict",
        "status": "AVAILABLE",
        "manufacturer": "Test Manufacturer",
        "model": "Model Y",
        "connection_info": {"backend": "tecan"},
        "accession_id": "019a6ee5-1234-7890-abcd-ef1234567890",
        "created_at": "2025-11-10T12:00:00Z",
        "properties_json": {},
    }

    machine = MachineResponse.model_validate(data)

    assert machine.name == "deserialize_test"
    assert machine.fqn == "test.deserialize.Machine"
    assert machine.asset_type == "MACHINE"
    assert machine.description == "From dict"
    assert machine.status == "AVAILABLE"
    assert machine.manufacturer == "Test Manufacturer"
    assert machine.model == "Model Y"
    assert machine.connection_info == {"backend": "tecan"}


def test_machine_response_status_enum_validation() -> None:
    """Test that MachineResponse properly validates status enum values."""
    # Valid enum value as string
    machine1 = MachineResponse(
        name="enum_test_1",
        fqn="test.enum.1",
        asset_type=AssetType.MACHINE,
        status="AVAILABLE",
    )
    assert machine1.status == "AVAILABLE"

    # Valid enum value as enum
    machine2 = MachineResponse(
        name="enum_test_2",
        fqn="test.enum.2",
        asset_type=AssetType.MACHINE,
        status=MachineStatusEnum.IN_USE,
    )
    assert machine2.status == "IN_USE"

    # Invalid enum value should raise error
    with pytest.raises(ValueError):
        MachineResponse(
            name="enum_test_3",
            fqn="test.enum.3",
            asset_type=AssetType.MACHINE,
            status="invalid_status",
        )


def test_machine_response_roundtrip_serialization() -> None:
    """Test that MachineResponse can be serialized and deserialized without data loss."""
    original = MachineResponse(
        name="roundtrip_test",
        fqn="test.roundtrip.Machine",
        asset_type=AssetType.MACHINE,
        description="Testing roundtrip",
        status=MachineStatusEnum.MAINTENANCE,
        manufacturer="Roundtrip Corp",
        connection_info={"test": "data", "nested": {"value": 123}},
    )

    # Serialize to dict
    data = original.model_dump()

    # Deserialize back
    restored = MachineResponse.model_validate(data)

    # Should be equal
    assert restored.name == original.name
    assert restored.fqn == original.fqn
    assert restored.asset_type == original.asset_type
    assert restored.description == original.description
    assert restored.status == original.status
    assert restored.manufacturer == original.manufacturer
    assert restored.connection_info == original.connection_info


@pytest.mark.asyncio
async def test_machine_response_from_orm(db_session: AsyncSession) -> None:
    """Test converting a MachineOrm instance to MachineResponse (critical for API layer).

    This validates that models inheriting from AssetOrm (with fqn field)
    can be successfully converted to their Pydantic response models.
    """
    from praxis.backend.utils.uuid import uuid7

    # Create an ORM instance
    machine_id = uuid7()
    orm_machine = MachineOrm(
        # accession_id=machine_id,  # init=False in ORM
        name="orm_test_machine",
        fqn="test.orm.Machine",
        asset_type=AssetType.MACHINE,
        description="Testing ORM to Pydantic conversion",
        manufacturer="Test Manufacturer",
        model="Model Z",
        status=MachineStatusEnum.AVAILABLE,
        connection_info={"backend": "hamilton", "port": 8080},
    )
    orm_machine.accession_id = machine_id

    db_session.add(orm_machine)
    await db_session.flush()

    # Convert ORM to Pydantic using model_validate with from_attributes=True
    response = MachineResponse.model_validate(orm_machine)

    # Verify all fields are correctly converted
    assert response.accession_id == machine_id
    assert response.name == "orm_test_machine"
    assert response.fqn == "test.orm.Machine"  # fqn IS present for Assets
    assert response.asset_type == "MACHINE"  # Enum converted to string
    assert response.description == "Testing ORM to Pydantic conversion"
    assert response.manufacturer == "Test Manufacturer"
    assert response.model == "Model Z"
    assert response.status == "AVAILABLE"  # Enum converted to string value
    assert response.connection_info == {"backend": "hamilton", "port": 8080}


@pytest.mark.asyncio
async def test_machine_response_from_orm_minimal(db_session: AsyncSession) -> None:
    """Test ORM-to-Pydantic conversion with minimal fields."""
    from praxis.backend.utils.uuid import uuid7

    # Create minimal ORM instance
    machine_id = uuid7()
    orm_machine = MachineOrm(
        # accession_id=machine_id,
        name="minimal_machine",
        fqn="test.minimal.Machine",
        asset_type=AssetType.MACHINE,
    )
    orm_machine.accession_id = machine_id

    db_session.add(orm_machine)
    await db_session.flush()

    # Convert to Pydantic
    response = MachineResponse.model_validate(orm_machine)

    # Verify required fields
    assert response.accession_id == machine_id
    assert response.name == "minimal_machine"
    assert response.fqn == "test.minimal.Machine"
    assert response.asset_type == "MACHINE"
    assert response.status == "OFFLINE"  # Default status

    # Verify optional fields are None or default
    assert response.description is None
    assert response.manufacturer is None
    assert response.model is None
    assert response.serial_number is None
    assert response.connection_info is None
