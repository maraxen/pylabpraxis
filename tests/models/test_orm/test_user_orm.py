"""Unit tests for UserOrm model."""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.user import UserOrm


@pytest.mark.asyncio
async def test_user_orm_creation_minimal(db_session: AsyncSession) -> None:
    """Test creating UserOrm with minimal required fields."""
    from praxis.backend.utils.uuid import uuid7

    user_id = uuid7()
    user = UserOrm(
        accession_id=user_id,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password_123",
    )
    db_session.add(user)
    await db_session.flush()

    # Verify creation
    assert user.accession_id == user_id
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password_123"
    assert user.is_active is True  # Default
    assert user.full_name is None
    assert user.phone_number is None
    assert user.phone_carrier is None


@pytest.mark.asyncio
async def test_user_orm_creation_with_all_fields(db_session: AsyncSession) -> None:
    """Test creating UserOrm with all fields populated."""
    from praxis.backend.utils.uuid import uuid7

    user_id = uuid7()
    user = UserOrm(
        accession_id=user_id,
        username="fulluser",
        email="full@example.com",
        hashed_password="hashed_password_456",
        full_name="John Doe",
        is_active=True,
        phone_number="555-1234",
        phone_carrier="verizon",
    )
    db_session.add(user)
    await db_session.flush()

    # Verify all fields
    assert user.accession_id == user_id
    assert user.username == "fulluser"
    assert user.email == "full@example.com"
    assert user.hashed_password == "hashed_password_456"
    assert user.full_name == "John Doe"
    assert user.is_active is True
    assert user.phone_number == "555-1234"
    assert user.phone_carrier == "verizon"


@pytest.mark.asyncio
async def test_user_orm_persist_to_database(db_session: AsyncSession) -> None:
    """Test full persistence cycle for UserOrm."""
    from praxis.backend.utils.uuid import uuid7

    user_id = uuid7()
    user = UserOrm(
        accession_id=user_id,
        username="persistuser",
        email="persist@example.com",
        hashed_password="hashed_password_789",
        full_name="Jane Smith",
    )
    db_session.add(user)
    await db_session.flush()

    # Query back
    result = await db_session.execute(
        select(UserOrm).where(UserOrm.accession_id == user_id),
    )
    retrieved = result.scalars().first()

    # Verify persistence
    assert retrieved is not None
    assert retrieved.accession_id == user_id
    assert retrieved.username == "persistuser"
    assert retrieved.email == "persist@example.com"
    assert retrieved.hashed_password == "hashed_password_789"
    assert retrieved.full_name == "Jane Smith"
    assert retrieved.is_active is True


@pytest.mark.asyncio
async def test_user_orm_unique_username_constraint(db_session: AsyncSession) -> None:
    """Test that username must be unique."""
    from praxis.backend.utils.uuid import uuid7

    # Create first user
    user1 = UserOrm(
        accession_id=uuid7(),
        username="uniqueuser",
        email="user1@example.com",
        hashed_password="hash1",
    )
    db_session.add(user1)
    await db_session.flush()

    # Try to create another with same username
    user2 = UserOrm(
        accession_id=uuid7(),
        username="uniqueuser",  # Duplicate username
        email="user2@example.com",
        hashed_password="hash2",
    )
    db_session.add(user2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_user_orm_unique_email_constraint(db_session: AsyncSession) -> None:
    """Test that email must be unique."""
    from praxis.backend.utils.uuid import uuid7

    # Create first user
    user1 = UserOrm(
        accession_id=uuid7(),
        username="user1",
        email="unique@example.com",
        hashed_password="hash1",
    )
    db_session.add(user1)
    await db_session.flush()

    # Try to create another with same email
    user2 = UserOrm(
        accession_id=uuid7(),
        username="user2",
        email="unique@example.com",  # Duplicate email
        hashed_password="hash2",
    )
    db_session.add(user2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_user_orm_is_active_flag(db_session: AsyncSession) -> None:
    """Test is_active flag for user accounts."""
    from praxis.backend.utils.uuid import uuid7

    # Active user (default)
    active_user = UserOrm(
        accession_id=uuid7(),
        username="activeuser",
        email="active@example.com",
        hashed_password="hash_active",
    )
    db_session.add(active_user)
    await db_session.flush()
    assert active_user.is_active is True

    # Inactive user
    inactive_user = UserOrm(
        accession_id=uuid7(),
        username="inactiveuser",
        email="inactive@example.com",
        hashed_password="hash_inactive",
        is_active=False,
    )
    db_session.add(inactive_user)
    await db_session.flush()
    assert inactive_user.is_active is False


@pytest.mark.asyncio
async def test_user_orm_phone_fields(db_session: AsyncSession) -> None:
    """Test phone number and carrier fields."""
    from praxis.backend.utils.uuid import uuid7

    user = UserOrm(
        accession_id=uuid7(),
        username="phoneuser",
        email="phone@example.com",
        hashed_password="hash_phone",
        phone_number="555-0100",
        phone_carrier="att",
    )
    db_session.add(user)
    await db_session.flush()

    # Query back
    result = await db_session.execute(
        select(UserOrm).where(UserOrm.username == "phoneuser"),
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.phone_number == "555-0100"
    assert retrieved.phone_carrier == "att"


@pytest.mark.asyncio
async def test_user_orm_repr(db_session: AsyncSession) -> None:
    """Test string representation of UserOrm."""
    from praxis.backend.utils.uuid import uuid7

    user_id = uuid7()
    user = UserOrm(
        accession_id=user_id,
        username="repruser",
        email="repr@example.com",
        hashed_password="hash_repr",
    )

    repr_str = repr(user)
    assert "UserOrm" in repr_str
    assert str(user_id) in repr_str
    assert "repruser" in repr_str
    assert "repr@example.com" in repr_str
    assert "is_active=True" in repr_str


@pytest.mark.asyncio
async def test_user_orm_query_by_username(db_session: AsyncSession) -> None:
    """Test querying users by username."""
    from praxis.backend.utils.uuid import uuid7

    user = UserOrm(
        accession_id=uuid7(),
        username="queryuser",
        email="query@example.com",
        hashed_password="hash_query",
    )
    db_session.add(user)
    await db_session.flush()

    # Query by username
    result = await db_session.execute(
        select(UserOrm).where(UserOrm.username == "queryuser"),
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.username == "queryuser"
    assert retrieved.email == "query@example.com"


@pytest.mark.asyncio
async def test_user_orm_query_by_email(db_session: AsyncSession) -> None:
    """Test querying users by email."""
    from praxis.backend.utils.uuid import uuid7

    user = UserOrm(
        accession_id=uuid7(),
        username="emailquery",
        email="emailquery@example.com",
        hashed_password="hash_email",
    )
    db_session.add(user)
    await db_session.flush()

    # Query by email
    result = await db_session.execute(
        select(UserOrm).where(UserOrm.email == "emailquery@example.com"),
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.username == "emailquery"
    assert retrieved.email == "emailquery@example.com"
