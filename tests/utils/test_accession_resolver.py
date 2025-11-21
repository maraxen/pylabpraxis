"""Tests for accession resolver utility in utils/accession_resolver.py."""

from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.utils.accession_resolver import get_accession_id_from_accession


class MockEntity:
    """Mock entity for testing."""

    def __init__(self, entity_id: UUID) -> None:
        self.id = entity_id


class MockEntityWithoutId:
    """Mock entity without id attribute for testing edge case."""

    def __init__(self) -> None:
        self.name = "test"


class TestGetAccessionIdFromAccession:
    """Tests for get_accession_id_from_accession function."""

    @pytest.mark.asyncio
    async def test_resolves_uuid_successfully(self) -> None:
        """Test that UUID accession is resolved when entity exists."""
        entity_id = uuid4()
        entity = MockEntity(entity_id)

        mock_db = Mock(spec=AsyncSession)
        mock_get_func = AsyncMock(return_value=entity)
        mock_get_by_name_func = AsyncMock()

        result = await get_accession_id_from_accession(
            accession=entity_id,
            db=mock_db,
            get_func=mock_get_func,
            get_by_name_func=mock_get_by_name_func,
            entity_type_name="Resource",
        )

        assert result == entity_id
        mock_get_func.assert_awaited_once_with(mock_db, entity_id)
        mock_get_by_name_func.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolves_name_string_successfully(self) -> None:
        """Test that name string accession is resolved to UUID."""
        entity_id = uuid4()
        entity = MockEntity(entity_id)

        mock_db = Mock(spec=AsyncSession)
        mock_get_func = AsyncMock()
        mock_get_by_name_func = AsyncMock(return_value=entity)

        result = await get_accession_id_from_accession(
            accession="test-resource",
            db=mock_db,
            get_func=mock_get_func,
            get_by_name_func=mock_get_by_name_func,
            entity_type_name="Resource",
        )

        assert result == entity_id
        mock_get_by_name_func.assert_awaited_once_with(mock_db, "test-resource")
        mock_get_func.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_value_error_when_uuid_not_found(self) -> None:
        """Test that ValueError is raised when UUID entity not found."""
        entity_id = uuid4()

        mock_db = Mock(spec=AsyncSession)
        mock_get_func = AsyncMock(return_value=None)
        mock_get_by_name_func = AsyncMock()

        with pytest.raises(
            ValueError, match=f"Resource with accession '{entity_id}' not found"
        ):
            await get_accession_id_from_accession(
                accession=entity_id,
                db=mock_db,
                get_func=mock_get_func,
                get_by_name_func=mock_get_by_name_func,
                entity_type_name="Resource",
            )

    @pytest.mark.asyncio
    async def test_raises_value_error_when_name_not_found(self) -> None:
        """Test that ValueError is raised when named entity not found."""
        mock_db = Mock(spec=AsyncSession)
        mock_get_func = AsyncMock()
        mock_get_by_name_func = AsyncMock(return_value=None)

        with pytest.raises(
            ValueError, match="Resource with accession 'nonexistent' not found"
        ):
            await get_accession_id_from_accession(
                accession="nonexistent",
                db=mock_db,
                get_func=mock_get_func,
                get_by_name_func=mock_get_by_name_func,
                entity_type_name="Resource",
            )

    @pytest.mark.asyncio
    async def test_raises_type_error_for_invalid_accession_type(self) -> None:
        """Test that TypeError is raised for invalid accession type."""
        mock_db = Mock(spec=AsyncSession)
        mock_get_func = AsyncMock()
        mock_get_by_name_func = AsyncMock()

        with pytest.raises(TypeError, match="Invalid accession type provided"):
            await get_accession_id_from_accession(
                accession=123,  # type: ignore  # Invalid type
                db=mock_db,
                get_func=mock_get_func,
                get_by_name_func=mock_get_by_name_func,
                entity_type_name="Resource",
            )

    @pytest.mark.asyncio
    async def test_uses_entity_type_name_in_error_messages(self) -> None:
        """Test that entity_type_name is used in error messages."""
        entity_id = uuid4()

        mock_db = Mock(spec=AsyncSession)
        mock_get_func = AsyncMock(return_value=None)
        mock_get_by_name_func = AsyncMock()

        with pytest.raises(ValueError, match="Deck"):
            await get_accession_id_from_accession(
                accession=entity_id,
                db=mock_db,
                get_func=mock_get_func,
                get_by_name_func=mock_get_by_name_func,
                entity_type_name="Deck",  # Different entity type
            )

    @pytest.mark.asyncio
    async def test_handles_entity_without_id_attribute(self) -> None:
        """Test graceful handling when entity doesn't have id attribute."""
        entity = MockEntityWithoutId()

        mock_db = Mock(spec=AsyncSession)
        mock_get_func = AsyncMock()
        mock_get_by_name_func = AsyncMock(return_value=entity)

        # Should raise ValueError since hasattr check for 'id' fails
        with pytest.raises(ValueError, match="not found"):
            await get_accession_id_from_accession(
                accession="test",
                db=mock_db,
                get_func=mock_get_func,
                get_by_name_func=mock_get_by_name_func,
                entity_type_name="Resource",
            )

    @pytest.mark.asyncio
    async def test_works_with_different_entity_types(self) -> None:
        """Test that function works with various entity type names."""
        entity_id = uuid4()
        entity = MockEntity(entity_id)

        mock_db = Mock(spec=AsyncSession)
        mock_get_func = AsyncMock(return_value=entity)
        mock_get_by_name_func = AsyncMock()

        entity_types = ["Resource", "Deck", "Machine", "Protocol", "Workcell"]

        for entity_type in entity_types:
            result = await get_accession_id_from_accession(
                accession=entity_id,
                db=mock_db,
                get_func=mock_get_func,
                get_by_name_func=mock_get_by_name_func,
                entity_type_name=entity_type,
            )
            assert result == entity_id

    @pytest.mark.asyncio
    async def test_string_uuid_format_is_treated_as_string(self) -> None:
        """Test that UUID-formatted strings are treated as name lookups."""
        entity_id = uuid4()
        entity = MockEntity(entity_id)
        uuid_string = str(uuid4())  # String representation of UUID

        mock_db = Mock(spec=AsyncSession)
        mock_get_func = AsyncMock()
        mock_get_by_name_func = AsyncMock(return_value=entity)

        result = await get_accession_id_from_accession(
            accession=uuid_string,
            db=mock_db,
            get_func=mock_get_func,
            get_by_name_func=mock_get_by_name_func,
            entity_type_name="Resource",
        )

        # Should use get_by_name_func, not get_func
        mock_get_by_name_func.assert_awaited_once_with(mock_db, uuid_string)
        mock_get_func.assert_not_called()
        assert result == entity_id

    @pytest.mark.asyncio
    async def test_returns_correct_id_from_found_entity(self) -> None:
        """Test that the returned ID matches the entity's ID attribute."""
        entity_id = uuid4()
        different_id = uuid4()
        entity = MockEntity(entity_id)

        mock_db = Mock(spec=AsyncSession)
        mock_get_func = AsyncMock()
        mock_get_by_name_func = AsyncMock(return_value=entity)

        result = await get_accession_id_from_accession(
            accession="test",
            db=mock_db,
            get_func=mock_get_func,
            get_by_name_func=mock_get_by_name_func,
            entity_type_name="Resource",
        )

        # Should return entity's ID, not a different one
        assert result == entity_id
        assert result != different_id
