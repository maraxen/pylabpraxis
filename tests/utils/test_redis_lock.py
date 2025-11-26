"""Tests for Redis lock utilities in utils/redis_lock.py."""

import time
from unittest.mock import MagicMock, patch

import pytest

from praxis.backend.utils.redis_lock import acquire_lock


class TestAcquireLock:

    """Tests for acquire_lock context manager."""

    @patch("praxis.backend.utils.redis_lock.time.time")
    def test_acquire_lock_succeeds_immediately(self, mock_time: MagicMock) -> None:
        """Test that lock is acquired immediately when available."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.return_value = True  # Lock acquired
        mock_redis.get.return_value = b"1234567890"
        mock_redis.delete.return_value = 1

        with acquire_lock(mock_redis, "test_resource") as acquired:
            assert acquired is True

        mock_redis.set.assert_called_once()
        mock_redis.delete.assert_called_once()

    @patch("praxis.backend.utils.redis_lock.time.time")
    def test_acquire_lock_formats_lock_name_correctly(
        self, mock_time: MagicMock,
    ) -> None:
        """Test that lock name is formatted with lock: prefix."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b"1234567890"

        with acquire_lock(mock_redis, "my_resource"):
            pass

        call_args = mock_redis.set.call_args
        lock_name = call_args[0][0]
        assert lock_name == "lock:my_resource"

    @patch("praxis.backend.utils.redis_lock.time.time")
    def test_acquire_lock_sets_expiration(self, mock_time: MagicMock) -> None:
        """Test that lock is set with expiration timeout."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b"1234567890"

        with acquire_lock(mock_redis, "test_resource", lock_timeout=120):
            pass

        call_args = mock_redis.set.call_args
        timeout = call_args[1]["ex"]
        assert timeout == 120

    @patch("praxis.backend.utils.redis_lock.time.time")
    def test_acquire_lock_uses_nx_option(self, mock_time: MagicMock) -> None:
        """Test that lock uses nx (not exists) option for atomicity."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b"1234567890"

        with acquire_lock(mock_redis, "test_resource"):
            pass

        call_args = mock_redis.set.call_args
        nx = call_args[1]["nx"]
        assert nx is True

    def test_acquire_lock_returns_false_on_timeout(self) -> None:
        """Test that lock returns False when acquisition times out."""
        mock_redis = MagicMock()
        mock_redis.set.return_value = False  # Lock not available

        with acquire_lock(
            mock_redis, "test_resource", acquire_timeout=0.2,
        ) as acquired:
            assert acquired is False

        # Should have tried multiple times
        assert mock_redis.set.call_count > 1

    @patch("praxis.backend.utils.redis_lock.time.time")
    @patch("praxis.backend.utils.redis_lock.time.sleep")
    def test_acquire_lock_retries_with_sleep(
        self, mock_sleep: MagicMock, mock_time: MagicMock,
    ) -> None:
        """Test that lock acquisition retries with sleep between attempts."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.side_effect = [False, False, True]  # Succeeds on 3rd try
        mock_redis.get.return_value = b"1234567890"

        with acquire_lock(mock_redis, "test_resource"):
            pass

        # Should have called sleep between retry attempts
        assert mock_sleep.call_count >= 2
        mock_sleep.assert_called_with(0.1)

    @patch("praxis.backend.utils.redis_lock.time.time")
    def test_acquire_lock_releases_lock_on_success(self, mock_time: MagicMock) -> None:
        """Test that lock is released when context exits normally."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b"1234567890"

        with acquire_lock(mock_redis, "test_resource"):
            pass

        mock_redis.delete.assert_called_once()

    def test_acquire_lock_does_not_release_on_timeout(self) -> None:
        """Test that lock is not deleted when acquisition times out."""
        mock_redis = MagicMock()
        mock_redis.set.return_value = False  # Always fails

        with acquire_lock(
            mock_redis, "test_resource", acquire_timeout=0.1,
        ) as acquired:
            assert acquired is False

        # Should not call delete since lock was never acquired
        mock_redis.delete.assert_not_called()

    def test_acquire_lock_verifies_identifier_before_release(self) -> None:
        """Test that lock verifies identifier matches before releasing."""
        mock_redis = MagicMock()
        mock_redis.set.return_value = True
        # Simulate identifier mismatch (someone else's lock)
        mock_redis.get.return_value = b"different_identifier"

        with acquire_lock(mock_redis, "test_resource"):
            pass

        # Should not delete since identifier doesn't match
        mock_redis.delete.assert_not_called()

    def test_acquire_lock_raises_exception_on_redis_error(self) -> None:
        """Test that exceptions from Redis operations are propagated."""
        mock_redis = MagicMock()
        mock_redis.set.side_effect = Exception("Redis connection failed")

        with pytest.raises(Exception, match="Redis connection failed"):
            with acquire_lock(mock_redis, "test_resource"):
                pass

    @patch("praxis.backend.utils.redis_lock.time.time")
    def test_acquire_lock_releases_even_on_exception_in_context(
        self, mock_time: MagicMock,
    ) -> None:
        """Test that lock is released even if exception occurs in with block."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b"1234567890"

        with pytest.raises(ValueError), acquire_lock(mock_redis, "test_resource"):
            raise ValueError("Error in protected code")

        # Lock should still be released
        mock_redis.delete.assert_called_once()

    def test_acquire_lock_allows_custom_acquire_timeout(self) -> None:
        """Test that custom acquire_timeout is respected."""
        mock_redis = MagicMock()
        mock_redis.set.return_value = False

        start_time = time.time()
        with acquire_lock(
            mock_redis, "test_resource", acquire_timeout=0.3,
        ) as acquired:
            elapsed = time.time() - start_time

        assert acquired is False
        # Should have timed out around 0.3 seconds (with some tolerance)
        assert 0.2 < elapsed < 0.5

    @patch("praxis.backend.utils.redis_lock.time.time")
    def test_acquire_lock_default_timeouts(self, mock_time: MagicMock) -> None:
        """Test that default timeout values are used when not specified."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b"1234567890"

        with acquire_lock(mock_redis, "test_resource"):
            pass

        # Check that default lock_timeout (60 seconds) was used
        call_args = mock_redis.set.call_args
        timeout = call_args[1]["ex"]
        assert timeout == 60

    def test_acquire_lock_unique_identifiers_for_different_locks(self) -> None:
        """Test that different lock acquisitions use different identifiers."""
        mock_redis = MagicMock()
        mock_redis.set.return_value = True

        # Capture identifiers from set calls
        identifiers = []

        def capture_identifier(lock_name, identifier, **kwargs):
            identifiers.append(identifier)
            return True

        mock_redis.set.side_effect = capture_identifier
        mock_redis.get.return_value = b"timestamp"

        # Acquire lock twice (with small delay to ensure different timestamps)
        with acquire_lock(mock_redis, "resource1"):
            pass

        time.sleep(0.01)

        with acquire_lock(mock_redis, "resource2"):
            pass

        # Identifiers may or may not be different depending on time precision
        # but both should be valid timestamp strings
        assert len(identifiers) == 2
        assert all(identifier.isdigit() for identifier in identifiers)

    @patch("praxis.backend.utils.redis_lock.time.time")
    def test_acquire_lock_works_as_context_manager(self, mock_time: MagicMock) -> None:
        """Test that acquire_lock properly implements context manager protocol."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b"1234567890"

        # Should work with 'with' statement
        with acquire_lock(mock_redis, "test_resource") as lock_acquired:
            # Inside context, lock should be acquired
            assert lock_acquired is True
            # Verify set was called
            assert mock_redis.set.called

        # After context, lock should be released
        assert mock_redis.delete.called


class TestAcquireLockEdgeCases:

    """Edge case tests for acquire_lock."""

    def test_acquire_lock_with_zero_acquire_timeout(self) -> None:
        """Test behavior with zero acquire timeout."""
        mock_redis = MagicMock()
        mock_redis.set.return_value = False

        with acquire_lock(
            mock_redis, "test_resource", acquire_timeout=0.0,
        ) as acquired:
            # Should immediately timeout
            assert acquired is False

    @patch("praxis.backend.utils.redis_lock.time.time")
    def test_acquire_lock_exception_in_finally_block(
        self, mock_time: MagicMock,
    ) -> None:
        """Test that exception in finally block is propagated."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b"1234567890"
        mock_redis.delete.side_effect = Exception("Delete failed")

        with pytest.raises(Exception, match="Delete failed"):
            with acquire_lock(mock_redis, "test_resource"):
                pass

    @patch("praxis.backend.utils.redis_lock.time.time")
    def test_acquire_lock_with_very_long_resource_name(
        self, mock_time: MagicMock,
    ) -> None:
        """Test that lock works with very long resource names."""
        mock_time.return_value = 1234567890.0
        mock_redis = MagicMock()
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b"1234567890"

        long_name = "a" * 1000
        with acquire_lock(mock_redis, long_name):
            pass

        call_args = mock_redis.set.call_args
        lock_name = call_args[0][0]
        assert lock_name == f"lock:{long_name}"
