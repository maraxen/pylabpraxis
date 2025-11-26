"""Tests for run control utilities in utils/run_control.py."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from redis.exceptions import RedisError

from praxis.backend.utils.run_control import (
    ALLOWED_COMMANDS,
    COMMAND_KEY_PREFIX,
    _get_command_key,
    clear_control_command,
    get_control_command,
    send_control_command,
)


class TestConstants:

    """Tests for module constants."""

    def test_allowed_commands_contains_standard_commands(self) -> None:
        """Test that ALLOWED_COMMANDS contains standard control commands."""
        assert "PAUSE" in ALLOWED_COMMANDS
        assert "RESUME" in ALLOWED_COMMANDS
        assert "CANCEL" in ALLOWED_COMMANDS

    def test_allowed_commands_is_list(self) -> None:
        """Test that ALLOWED_COMMANDS is a list."""
        assert isinstance(ALLOWED_COMMANDS, list)

    def test_command_key_prefix_is_correct(self) -> None:
        """Test that COMMAND_KEY_PREFIX has correct value."""
        assert COMMAND_KEY_PREFIX == "orchestrator:control"


class TestGetCommandKey:

    """Tests for _get_command_key helper function."""

    def test_get_command_key_formats_correctly(self) -> None:
        """Test that _get_command_key formats key correctly."""
        run_id = uuid4()
        key = _get_command_key(run_id)
        assert key == f"orchestrator:control:{run_id}"

    def test_get_command_key_with_different_uuids(self) -> None:
        """Test that different UUIDs produce different keys."""
        run_id1 = uuid4()
        run_id2 = uuid4()

        key1 = _get_command_key(run_id1)
        key2 = _get_command_key(run_id2)

        assert key1 != key2
        assert str(run_id1) in key1
        assert str(run_id2) in key2


class TestSendControlCommand:

    """Tests for send_control_command function."""

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_send_control_command_sets_redis_key(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that send_control_command sets value in Redis."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock()
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        result = await send_control_command(run_id, "PAUSE")

        assert result is True
        mock_redis.set.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_send_control_command_uses_correct_key(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that send_control_command uses correctly formatted key."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock()
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        await send_control_command(run_id, "PAUSE")

        call_args = mock_redis.set.call_args
        key = call_args[0][0]
        assert key == f"orchestrator:control:{run_id}"

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_send_control_command_sets_correct_value(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that send_control_command sets correct command value."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock()
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        await send_control_command(run_id, "CANCEL")

        call_args = mock_redis.set.call_args
        command = call_args[0][1]
        assert command == "CANCEL"

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_send_control_command_sets_ttl(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that send_control_command sets TTL expiration."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock()
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        await send_control_command(run_id, "PAUSE", ttl_seconds=7200)

        call_args = mock_redis.set.call_args
        ttl = call_args[1]["ex"]
        assert ttl == 7200

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_send_control_command_default_ttl(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that send_control_command uses default TTL of 3600 seconds."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock()
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        await send_control_command(run_id, "PAUSE")

        call_args = mock_redis.set.call_args
        ttl = call_args[1]["ex"]
        assert ttl == 3600

    @pytest.mark.asyncio
    async def test_send_control_command_rejects_invalid_command(self) -> None:
        """Test that send_control_command raises ValueError for invalid command."""
        run_id = uuid4()

        with pytest.raises(ValueError, match="Invalid command"):
            await send_control_command(run_id, "INVALID_COMMAND")

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_send_control_command_handles_redis_error(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that send_control_command returns False on Redis error."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock(side_effect=RedisError("Connection failed"))
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        result = await send_control_command(run_id, "PAUSE")

        assert result is False


class TestGetControlCommand:

    """Tests for get_control_command function."""

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_get_control_command_retrieves_from_redis(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that get_control_command retrieves value from Redis."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value="PAUSE")
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        result = await get_control_command(run_id)

        assert result == "PAUSE"
        mock_redis.get.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_get_control_command_uses_correct_key(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that get_control_command uses correctly formatted key."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value="RESUME")
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        await get_control_command(run_id)

        call_args = mock_redis.get.call_args
        key = call_args[0][0]
        assert key == f"orchestrator:control:{run_id}"

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_get_control_command_returns_none_when_not_found(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that get_control_command returns None when key doesn't exist."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        result = await get_control_command(run_id)

        assert result is None

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_get_control_command_handles_redis_error(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that get_control_command returns None on Redis error."""
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock(side_effect=RedisError("Connection failed"))
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        result = await get_control_command(run_id)

        assert result is None


class TestClearControlCommand:

    """Tests for clear_control_command function."""

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_clear_control_command_deletes_from_redis(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that clear_control_command deletes key from Redis."""
        mock_redis = MagicMock()
        mock_redis.delete = AsyncMock(return_value=1)
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        result = await clear_control_command(run_id)

        assert result is True
        mock_redis.delete.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_clear_control_command_uses_correct_key(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that clear_control_command uses correctly formatted key."""
        mock_redis = MagicMock()
        mock_redis.delete = AsyncMock(return_value=1)
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        await clear_control_command(run_id)

        call_args = mock_redis.delete.call_args
        key = call_args[0][0]
        assert key == f"orchestrator:control:{run_id}"

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_clear_control_command_returns_false_when_not_found(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that clear_control_command returns False when key doesn't exist."""
        mock_redis = MagicMock()
        mock_redis.delete = AsyncMock(return_value=0)
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        result = await clear_control_command(run_id)

        assert result is False

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_clear_control_command_handles_redis_error(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that clear_control_command returns False on Redis error."""
        mock_redis = MagicMock()
        mock_redis.delete = AsyncMock(side_effect=RedisError("Connection failed"))
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()
        result = await clear_control_command(run_id)

        assert result is False


class TestRunControlIntegration:

    """Integration tests for run control utilities."""

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_all_allowed_commands_work(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test that all allowed commands can be sent successfully."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock()
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()

        for command in ALLOWED_COMMANDS:
            result = await send_control_command(run_id, command)
            assert result is True

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.run_control._get_redis_client")
    async def test_send_and_retrieve_command_flow(
        self, mock_get_redis: MagicMock,
    ) -> None:
        """Test the flow of sending and retrieving a command."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock()
        mock_redis.get = AsyncMock(return_value="CANCEL")
        mock_get_redis.return_value = mock_redis

        run_id = uuid4()

        # Send command
        send_result = await send_control_command(run_id, "CANCEL")
        assert send_result is True

        # Retrieve command
        retrieved = await get_control_command(run_id)
        assert retrieved == "CANCEL"
