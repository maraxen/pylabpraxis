"""Unit tests for Workcell Pydantic models."""
import json
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums.workcell import WorkcellStatusEnum
from praxis.backend.models.orm.workcell import WorkcellOrm
from praxis.backend.models.pydantic_internals.workcell import (
    WorkcellBase,
    WorkcellCreate,
    WorkcellResponse,
    WorkcellUpdate,
)
from praxis.backend.utils.uuid import uuid7


def test_workcell_base_minimal() -> None:
    """Test creating a WorkcellBase with minimal required fields."""
    workcell = WorkcellBase(name="test_workcell")

    assert workcell.name == "test_workcell"
    assert workcell.fqn is None  # fqn is now optional
    assert workcell.status == WorkcellStatusEnum.AVAILABLE
    assert workcell.description is None
    assert workcell.physical_location is None
    assert workcell.latest_state_json is None
    assert workcell.last_state_update_time is None


def test_workcell_base_with_all_fields() -> None:
    """Test creating a WorkcellBase with all fields populated."""
    now = datetime.now(timezone.utc)
    state = {"foo": "bar", "count": 42}

    workcell = WorkcellBase(
        name="full_workcell",
        fqn="test.full.workcell",
        description="A fully populated workcell",
        physical_location="Lab 1, Room 101",
        status=WorkcellStatusEnum.IN_USE,
        latest_state_json=state,
        last_state_update_time=now,
    )

    assert workcell.name == "full_workcell"
    assert workcell.fqn == "test.full.workcell"
    assert workcell.description == "A fully populated workcell"
    assert workcell.physical_location == "Lab 1, Room 101"
    # use_enum_values=True means enum is stored as string value
    assert workcell.status == WorkcellStatusEnum.IN_USE.value
    assert workcell.latest_state_json == state
    assert workcell.last_state_update_time == now


def test_workcell_create_inherits_from_base() -> None:
    """Test that WorkcellCreate inherits all properties from WorkcellBase."""
    workcell = WorkcellCreate(
        name="create_test",
        description="Testing create model",
    )

    assert workcell.name == "create_test"
    assert workcell.fqn is None  # fqn is optional
    assert workcell.description == "Testing create model"
    assert workcell.status == WorkcellStatusEnum.AVAILABLE


def test_workcell_update_all_fields_optional() -> None:
    """Test that WorkcellUpdate allows all fields to be optional."""
    # Should be able to create with no fields
    update = WorkcellUpdate()
    assert update.name is None
    assert update.description is None
    assert update.physical_location is None
    assert update.status is None
    assert update.latest_state_json is None

    # Should be able to create with partial fields
    update_partial = WorkcellUpdate(name="new_name")
    assert update_partial.name == "new_name"
    assert update_partial.description is None


def test_workcell_response_with_empty_relationships() -> None:
    """Test WorkcellResponse with empty relationship lists."""
    workcell = WorkcellResponse(name="response_test")

    assert workcell.fqn is None
    assert workcell.machines == []
    assert workcell.resources == []
    assert workcell.decks == []


def test_workcell_response_serialization_to_dict() -> None:
    """Test that WorkcellResponse can be serialized to a dictionary."""
    workcell = WorkcellResponse(
        name="serialize_test",
        fqn="test.serialize",  # Providing fqn explicitly
        description="Testing serialization",
        status=WorkcellStatusEnum.MAINTENANCE,
    )

    data = workcell.model_dump()

    assert isinstance(data, dict)
    assert data["name"] == "serialize_test"
    assert data["fqn"] == "test.serialize"
    assert data["description"] == "Testing serialization"
    # Enum is serialized to its string value (use_enum_values=True)
    assert data["status"] == "maintenance"
    assert data["machines"] == []
    assert data["resources"] == []
    assert data["decks"] == []


def test_workcell_response_serialization_to_json() -> None:
    """Test that WorkcellResponse can be serialized to JSON."""
    now = datetime.now(timezone.utc)
    workcell = WorkcellResponse(
        name="json_test",
        status=WorkcellStatusEnum.ERROR,
        last_state_update_time=now,
    )

    json_str = workcell.model_dump_json()

    assert isinstance(json_str, str)
    data = json.loads(json_str)
    assert data["name"] == "json_test"
    assert data["fqn"] is None  # fqn is optional
    assert data["status"] == "error"  # Enum value


def test_workcell_response_deserialization_from_dict() -> None:
    """Test that WorkcellResponse can be deserialized from a dictionary."""
    data = {
        "name": "deserialize_test",
        "fqn": "test.deserialize",
        "description": "From dict",
        "physical_location": "Lab 2",
        "status": "inactive",
        "latest_state_json": {"key": "value"},
        "last_state_update_time": None,
        "machines": [],
        "resources": [],
        "decks": [],
    }

    workcell = WorkcellResponse.model_validate(data)

    assert workcell.name == "deserialize_test"
    assert workcell.fqn == "test.deserialize"
    assert workcell.description == "From dict"
    assert workcell.physical_location == "Lab 2"
    # Enum is stored as string value (use_enum_values=True)
    assert workcell.status == "inactive"
    assert workcell.latest_state_json == {"key": "value"}


def test_workcell_response_enum_validation() -> None:
    """Test that WorkcellResponse properly validates enum values."""
    # Valid enum value as string
    workcell1 = WorkcellResponse(
        name="enum_test_1",
        status="active",
    )
    # With use_enum_values=True, status is stored as string
    assert workcell1.status == "active"

    # Valid enum value as enum
    workcell2 = WorkcellResponse(
        name="enum_test_2",
        status=WorkcellStatusEnum.RESERVED,
    )
    # With use_enum_values=True, enum is converted to string value
    assert workcell2.status == "reserved"

    # Invalid enum value should raise error
    with pytest.raises(ValueError):
        WorkcellResponse(
            name="enum_test_3",
            status="invalid_status",
        )


def test_workcell_response_roundtrip_serialization() -> None:
    """Test that WorkcellResponse can be serialized and deserialized without data loss."""
    original = WorkcellResponse(
        name="roundtrip_test",
        fqn="test.roundtrip",
        description="Testing roundtrip",
        physical_location="Lab 3",
        status=WorkcellStatusEnum.MAINTENANCE,
        latest_state_json={"test": "data", "nested": {"value": 123}},
    )

    # Serialize to dict
    data = original.model_dump()

    # Deserialize back
    restored = WorkcellResponse.model_validate(data)

    # Should be equal
    assert restored.name == original.name
    assert restored.fqn == original.fqn
    assert restored.description == original.description
    assert restored.physical_location == original.physical_location
    assert restored.status == original.status
    assert restored.latest_state_json == original.latest_state_json


@pytest.mark.asyncio
async def test_workcell_response_from_orm(db_session: AsyncSession) -> None:
    """Test converting a WorkcellOrm instance to WorkcellResponse (critical for API layer).

    Note: WorkcellOrm doesn't have an 'fqn' field (doesn't inherit from AssetOrm),
    but WorkcellResponse.fqn is now optional, so conversion works with fqn=None.
    """
    # Create an ORM instance
    workcell_id = uuid7()
    orm_workcell = WorkcellOrm(
        accession_id=workcell_id,
        name="orm_test_workcell",
        description="Testing ORM to Pydantic conversion",
        physical_location="Lab 4",
        status=WorkcellStatusEnum.ACTIVE.value,
        latest_state_json={"key": "value"},
    )

    db_session.add(orm_workcell)
    await db_session.flush()

    # Convert ORM to Pydantic using model_validate with from_attributes=True
    response = WorkcellResponse.model_validate(orm_workcell)

    # Verify all fields are correctly converted
    assert response.accession_id == workcell_id
    assert response.name == "orm_test_workcell"
    assert response.fqn is None  # fqn is optional and not present in ORM
    assert response.description == "Testing ORM to Pydantic conversion"
    assert response.physical_location == "Lab 4"
    assert response.status == "active"  # Enum converted to string value
    assert response.latest_state_json == {"key": "value"}
    assert response.machines == []
    assert response.resources == []
    assert response.decks == []
