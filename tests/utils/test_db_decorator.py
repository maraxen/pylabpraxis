"""Tests for database transaction decorator in utils/db_decorator.py."""

from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.utils.db_decorator import handle_db_transaction


class TestHandleDbTransaction:

    """Tests for handle_db_transaction decorator."""

    @pytest.mark.asyncio
    async def test_commits_on_success(self) -> None:
        """Test that decorator commits transaction on successful execution."""
        mock_session = Mock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        @handle_db_transaction
        async def test_func(db: AsyncSession) -> str:
            return "success"

        result = await test_func(mock_session)

        assert result == "success"
        mock_session.commit.assert_awaited_once()
        mock_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self) -> None:
        """Test that decorator rolls back transaction on exception."""
        mock_session = Mock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        @handle_db_transaction
        async def test_func(db: AsyncSession) -> None:
            msg = "Test error"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="Test error"):
            await test_func(mock_session)

        mock_session.rollback.assert_awaited_once()
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_original_exception(self) -> None:
        """Test that decorator re-raises the original exception."""
        mock_session = Mock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        @handle_db_transaction
        async def test_func(db: AsyncSession) -> None:
            msg = "Original error"
            raise RuntimeError(msg)

        with pytest.raises(ValueError, match="An unexpected error occurred: Original error"):
            await test_func(mock_session)

    @pytest.mark.asyncio
    async def test_works_with_positional_db_arg(self) -> None:
        """Test that decorator works when db is passed as positional argument."""
        mock_session = Mock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        @handle_db_transaction
        async def test_func(db: AsyncSession, value: int) -> int:
            return value * 2

        result = await test_func(mock_session, 5)

        assert result == 10
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_works_with_keyword_db_arg(self) -> None:
        """Test that decorator works when db is passed as keyword argument."""
        mock_session = Mock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        @handle_db_transaction
        async def test_func(value: int, db: AsyncSession) -> int:
            return value * 3

        result = await test_func(5, db=mock_session)

        assert result == 15
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_raises_type_error_without_db_session(self) -> None:
        """Test that decorator raises TypeError if no db session provided."""

        @handle_db_transaction
        async def test_func(value: int) -> int:
            return value

        with pytest.raises(
            TypeError,
            match="Function decorated with @handle_db_transaction must have a 'db' argument",
        ):
            await test_func(5)

    @pytest.mark.asyncio
    async def test_preserves_function_name(self) -> None:
        """Test that decorator preserves function name (via @wraps)."""

        @handle_db_transaction
        async def my_test_function(db: AsyncSession) -> str:
            return "test"

        assert my_test_function.__name__ == "my_test_function"

    @pytest.mark.asyncio
    async def test_preserves_function_docstring(self) -> None:
        """Test that decorator preserves function docstring (via @wraps)."""

        @handle_db_transaction
        async def documented_function(db: AsyncSession) -> str:
            """This is a test docstring."""
            return "test"

        assert documented_function.__doc__ == "This is a test docstring."

    @pytest.mark.asyncio
    async def test_works_with_multiple_arguments(self) -> None:
        """Test that decorator works with functions that have multiple arguments."""
        mock_session = Mock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        @handle_db_transaction
        async def test_func(
            db: AsyncSession, name: str, age: int, active: bool = True,
        ) -> dict:
            return {"name": name, "age": age, "active": active}

        result = await test_func(mock_session, "Alice", 30, active=False)

        assert result == {"name": "Alice", "age": 30, "active": False}
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_works_when_db_is_second_positional_arg(self) -> None:
        """Test that decorator finds db session when it's not the first argument."""
        mock_session = Mock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        @handle_db_transaction
        async def test_func(self: object, db: AsyncSession, value: int) -> int:
            return value * 2

        # Simulate instance method call with self
        fake_self = object()
        result = await test_func(fake_self, mock_session, 7)

        assert result == 14
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_commit_called_before_returning_result(self) -> None:
        """Test that commit is called before returning the result."""
        mock_session = Mock(spec=AsyncSession)
        commit_called = False

        async def track_commit() -> None:
            nonlocal commit_called
            commit_called = True

        mock_session.commit = track_commit
        mock_session.rollback = AsyncMock()

        @handle_db_transaction
        async def test_func(db: AsyncSession) -> str:
            # At this point, commit should not have been called yet
            assert not commit_called
            return "done"

        result = await test_func(mock_session)

        # After function returns, commit should have been called
        assert commit_called
        assert result == "done"

    @pytest.mark.asyncio
    async def test_rollback_called_before_raising_exception(self) -> None:
        """Test that rollback is called before re-raising exception."""
        mock_session = Mock(spec=AsyncSession)
        rollback_called = False

        async def track_rollback() -> None:
            nonlocal rollback_called
            rollback_called = True

        mock_session.commit = AsyncMock()
        mock_session.rollback = track_rollback

        @handle_db_transaction
        async def test_func(db: AsyncSession) -> None:
            msg = "Error"
            raise ValueError(msg)

        try:
            await test_func(mock_session)
        except ValueError:
            # After exception, rollback should have been called
            assert rollback_called

    @pytest.mark.asyncio
    async def test_works_with_none_return_value(self) -> None:
        """Test that decorator works with functions that return None."""
        mock_session = Mock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        @handle_db_transaction
        async def test_func(db: AsyncSession) -> None:
            # Function that returns None
            pass

        result = await test_func(mock_session)

        assert result is None
        mock_session.commit.assert_awaited_once()
