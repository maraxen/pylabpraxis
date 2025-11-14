"""Unit tests for User Pydantic models."""
import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.pydantic_internals.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
)
from praxis.backend.models.orm.user import UserOrm


def test_user_base_minimal() -> None:
    """Test UserBase with minimal required fields."""
    user = UserBase(
        username="testuser",
        email="test@example.com",
    )

    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.full_name is None
    assert user.is_active is True  # Default


def test_user_base_with_all_fields() -> None:
    """Test UserBase with all fields populated."""
    user = UserBase(
        username="fulluser",
        email="full@example.com",
        full_name="John Doe",
        is_active=True,
    )

    assert user.username == "fulluser"
    assert user.email == "full@example.com"
    assert user.full_name == "John Doe"
    assert user.is_active is True


def test_user_create_with_password() -> None:
    """Test UserCreate includes password field."""
    user = UserCreate(
        username="newuser",
        email="new@example.com",
        password="secure_password_123",
        full_name="Jane Smith",
    )

    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert user.password == "secure_password_123"
    assert user.full_name == "Jane Smith"
    assert user.is_active is True


def test_user_create_password_required() -> None:
    """Test that UserCreate requires password field."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            username="testuser",
            email="test@example.com",
            # Missing password
        )

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("password",) for error in errors)


def test_user_update_all_fields_optional() -> None:
    """Test that UserUpdate allows all fields to be optional."""
    # Empty update is valid
    update = UserUpdate()

    assert update.username is None
    assert update.email is None
    assert update.full_name is None
    assert update.is_active is None
    assert update.password is None

    # Can update specific fields
    update_partial = UserUpdate(
        username="updated_user",
        is_active=False,
    )

    assert update_partial.username == "updated_user"
    assert update_partial.is_active is False
    assert update_partial.email is None


def test_user_update_with_password() -> None:
    """Test UserUpdate can include password change."""
    update = UserUpdate(
        password="new_password_456",
    )

    assert update.password == "new_password_456"
    assert update.username is None


def test_user_response_serialization_to_dict() -> None:
    """Test UserResponse serialization to dict."""
    response = UserResponse(
        username="response_user",
        email="response@example.com",
        full_name="Response User",
        is_active=True,
    )

    user_dict = response.model_dump()

    assert user_dict["username"] == "response_user"
    assert user_dict["email"] == "response@example.com"
    assert user_dict["full_name"] == "Response User"
    assert user_dict["is_active"] is True


def test_user_response_serialization_to_json() -> None:
    """Test UserResponse serialization to JSON."""
    response = UserResponse(
        username="json_user",
        email="json@example.com",
        full_name="JSON User",
    )

    json_str = response.model_dump_json()

    assert isinstance(json_str, str)
    assert "json_user" in json_str
    assert "json@example.com" in json_str


def test_user_response_deserialization_from_dict() -> None:
    """Test creating UserResponse from dict."""
    user_data = {
        "username": "deserialized_user",
        "email": "deserialized@example.com",
        "full_name": "Deserialized User",
        "is_active": True,
    }

    response = UserResponse(**user_data)

    assert response.username == "deserialized_user"
    assert response.email == "deserialized@example.com"
    assert response.full_name == "Deserialized User"
    assert response.is_active is True


def test_user_response_roundtrip_serialization() -> None:
    """Test UserResponse survives serialization round-trip."""
    original = UserResponse(
        username="roundtrip_user",
        email="roundtrip@example.com",
        full_name="Roundtrip Test",
        is_active=False,
    )

    # Serialize to dict and back
    user_dict = original.model_dump()
    restored = UserResponse(**user_dict)

    assert restored.username == original.username
    assert restored.email == original.email
    assert restored.full_name == original.full_name
    assert restored.is_active == original.is_active


@pytest.mark.asyncio
async def test_user_response_from_orm(db_session: AsyncSession) -> None:
    """Test converting UserOrm to UserResponse."""
    from praxis.backend.utils.uuid import uuid7

    # Create ORM instance
    user_id = uuid7()
    orm_user = UserOrm(
        accession_id=user_id,
        name="orm_test_user",
        username="orm_test_user",
        email="orm@example.com",
        hashed_password="hashed_password_123",
        full_name="ORM Test User",
        is_active=True,
        phone_number="555-1234",
        phone_carrier="verizon",
    )
    orm_user.accession_id = user_id
    db_session.add(orm_user)
    await db_session.flush()

    # Convert to Pydantic
    response = UserResponse.model_validate(orm_user)

    # Verify conversion (note: phone fields and hashed_password are not in Pydantic model)
    assert response.username == "orm_test_user"
    assert response.email == "orm@example.com"
    assert response.full_name == "ORM Test User"
    assert response.is_active is True


@pytest.mark.asyncio
async def test_user_response_from_orm_minimal(db_session: AsyncSession) -> None:
    """Test ORM-to-Pydantic conversion with minimal fields."""
    from praxis.backend.utils.uuid import uuid7

    user_id = uuid7()
    orm_user = UserOrm(
        accession_id=user_id,
        name="minimal_user",
        username="minimal_user",
        email="minimal@example.com",
        hashed_password="hashed_password_456",
    )

    db_session.add(orm_user)
    await db_session.flush()

    # Convert to Pydantic
    response = UserResponse.model_validate(orm_user)

    # Verify
    assert response.username == "minimal_user"
    assert response.email == "minimal@example.com"
    assert response.full_name is None
    assert response.is_active is True  # Default


def test_user_base_inactive_user() -> None:
    """Test UserBase with inactive user."""
    user = UserBase(
        username="inactiveuser",
        email="inactive@example.com",
        is_active=False,
    )

    assert user.username == "inactiveuser"
    assert user.is_active is False


def test_user_create_inactive_user() -> None:
    """Test creating an inactive user."""
    user = UserCreate(
        username="newinactive",
        email="newinactive@example.com",
        password="password123",
        is_active=False,
    )

    assert user.username == "newinactive"
    assert user.is_active is False


def test_user_response_does_not_expose_password() -> None:
    """Test that UserResponse does not contain password field."""
    response = UserResponse(
        username="secure_user",
        email="secure@example.com",
    )

    # Verify password is not in the model
    assert not hasattr(response, "password")
    assert not hasattr(response, "hashed_password")

    # Verify it's not in serialized output
    user_dict = response.model_dump()
    assert "password" not in user_dict
    assert "hashed_password" not in user_dict
