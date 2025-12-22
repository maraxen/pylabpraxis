"""Tests for logging utilities in utils/logging.py."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from praxis.backend.utils.logging import (
    get_logger,
    log_async_runtime_errors,
    log_runtime_errors,
)


class TestGetLogger:

    """Tests for get_logger function."""

    def test_returns_logger_instance(self) -> None:
        """Test that get_logger returns a logging.Logger instance."""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)

    def test_logger_has_correct_name(self) -> None:
        """Test that logger has the correct name."""
        logger = get_logger("my_test_logger")
        assert logger.name == "my_test_logger"

    def test_logger_level_is_debug(self) -> None:
        """Test that logger level is set to DEBUG."""
        logger = get_logger("test_logger")
        assert logger.level == logging.DEBUG

    def test_logger_has_stream_handler(self) -> None:
        """Test that logger has a StreamHandler attached."""
        logger = get_logger("test_logger")
        # Check if any handler is a StreamHandler
        has_stream_handler = any(
            isinstance(handler, logging.StreamHandler) for handler in logger.handlers
        )
        assert has_stream_handler

    def test_creates_different_loggers_for_different_names(self) -> None:
        """Test that different names create different logger instances."""
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")
        assert logger1.name != logger2.name


class TestLogRuntimeErrors:

    """Tests for log_runtime_errors decorator."""

    def test_decorator_allows_normal_execution(self) -> None:
        """Test that decorator doesn't interfere with normal execution."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(logger_instance=mock_logger, raises=False)
        def test_func(x: int, y: int) -> int:
            return x + y

        result = test_func(2, 3)
        assert result == 5

    def test_decorator_catches_and_logs_exception(self) -> None:
        """Test that decorator catches exceptions and logs them."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(logger_instance=mock_logger, raises=False)
        def test_func() -> None:
            raise ValueError("Test error")

        result = test_func()
        assert result is None
        mock_logger.error.assert_called()

    def test_decorator_re_raises_exception_when_raises_true(self) -> None:
        """Test that decorator re-raises exception when raises=True."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(
            logger_instance=mock_logger, raises=True, raises_exception=RuntimeError,
        )
        def test_func() -> None:
            raise ValueError("Test error")

        with pytest.raises(RuntimeError):
            test_func()

    def test_decorator_adds_prefix_to_log_message(self) -> None:
        """Test that prefix is added to log messages."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(
            logger_instance=mock_logger, raises=False, prefix="PREFIX: ",
        )
        def test_func() -> None:
            raise ValueError("Test error")

        test_func()
        # Check that error was called with message containing prefix
        call_args = mock_logger.error.call_args
        assert "PREFIX:" in str(call_args)

    def test_decorator_adds_suffix_to_log_message(self) -> None:
        """Test that suffix is added to log messages."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(
            logger_instance=mock_logger, raises=False, suffix=" :SUFFIX",
        )
        def test_func() -> None:
            raise ValueError("Test error")

        test_func()
        call_args = mock_logger.error.call_args
        assert ":SUFFIX" in str(call_args)

    def test_decorator_returns_custom_value_on_exception(self) -> None:
        """Test that decorator returns custom value when exception occurs."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(
            logger_instance=mock_logger, raises=False, return_="default_value",
        )
        def test_func() -> str:
            raise ValueError("Test error")

        result = test_func()
        # When exception occurs and raises=False, returns None (not return_ value)
        assert result is None

    def test_decorator_preserves_function_name(self) -> None:
        """Test that decorator preserves function name via @wraps."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(logger_instance=mock_logger)
        def my_function() -> int:
            return 42

        assert my_function.__name__ == "my_function"

    def test_decorator_preserves_function_docstring(self) -> None:
        """Test that decorator preserves function docstring via @wraps."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(logger_instance=mock_logger)
        def documented_function() -> int:
            """This is a docstring."""
            return 42

        assert documented_function.__doc__ == "This is a docstring."

    def test_decorator_with_specific_exception_type(self) -> None:
        """Test that decorator only catches specified exception type."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(
            logger_instance=mock_logger,
            exception_type=ValueError,
            raises=False,
        )
        def test_func() -> None:
            raise ValueError("Test error")

        result = test_func()
        assert result is None
        mock_logger.error.assert_called()

    @patch("praxis.backend.utils.logging.traceback.print_exc")
    def test_decorator_prints_traceback(self, mock_print_exc: MagicMock) -> None:
        """Test that decorator prints exception traceback."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(logger_instance=mock_logger, raises=False)
        def test_func() -> None:
            raise ValueError("Test error")

        test_func()
        mock_print_exc.assert_called_once()


class TestLogAsyncRuntimeErrors:

    """Tests for log_async_runtime_errors decorator."""

    @pytest.mark.asyncio
    async def test_decorator_allows_normal_execution(self) -> None:
        """Test that decorator doesn't interfere with normal async execution."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_async_runtime_errors(logger_instance=mock_logger, raises=False)
        async def test_func(x: int, y: int) -> int:
            return x + y

        result = await test_func(2, 3)
        assert result == 5

    @pytest.mark.asyncio
    async def test_decorator_catches_and_logs_exception(self) -> None:
        """Test that decorator catches async exceptions and logs them."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_async_runtime_errors(logger_instance=mock_logger, raises=False)
        async def test_func() -> None:
            raise ValueError("Async test error")

        result = await test_func()
        assert result is None
        mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_decorator_re_raises_exception_when_raises_true(self) -> None:
        """Test that decorator re-raises exception when raises=True."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_async_runtime_errors(
            logger_instance=mock_logger, raises=True, raises_exception=RuntimeError,
        )
        async def test_func() -> None:
            raise ValueError("Async test error")

        with pytest.raises(RuntimeError):
            await test_func()

    @pytest.mark.asyncio
    async def test_decorator_adds_prefix_to_log_message(self) -> None:
        """Test that prefix is added to async log messages."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_async_runtime_errors(
            logger_instance=mock_logger, raises=False, prefix="ASYNC PREFIX: ",
        )
        async def test_func() -> None:
            raise ValueError("Test error")

        await test_func()
        call_args = mock_logger.error.call_args
        assert "ASYNC PREFIX:" in str(call_args)

    @pytest.mark.asyncio
    async def test_decorator_preserves_function_name(self) -> None:
        """Test that decorator preserves async function name via @wraps."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_async_runtime_errors(logger_instance=mock_logger)
        async def my_async_function() -> int:
            return 42

        assert my_async_function.__name__ == "my_async_function"

    @pytest.mark.asyncio
    async def test_decorator_preserves_function_docstring(self) -> None:
        """Test that decorator preserves async function docstring."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_async_runtime_errors(logger_instance=mock_logger)
        async def documented_async_function() -> int:
            """This is an async docstring."""
            return 42

        assert documented_async_function.__doc__ == "This is an async docstring."

    @pytest.mark.asyncio
    async def test_decorator_with_specific_exception_type(self) -> None:
        """Test that decorator only catches specified exception type."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_async_runtime_errors(
            logger_instance=mock_logger,
            exception_type=ValueError,
            raises=False,
        )
        async def test_func() -> None:
            raise ValueError("Test error")

        result = await test_func()
        assert result is None
        mock_logger.error.assert_called()

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.logging.traceback.print_exc")
    async def test_decorator_prints_traceback(self, mock_print_exc: MagicMock) -> None:
        """Test that decorator prints exception traceback."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_async_runtime_errors(logger_instance=mock_logger, raises=False)
        async def test_func() -> None:
            raise ValueError("Async test error")

        await test_func()
        mock_print_exc.assert_called_once()


class TestLogRuntimeErrorsIntegration:

    """Integration tests for logging decorators."""

    def test_sync_and_async_decorators_work_consistently(self) -> None:
        """Test that sync and async decorators behave consistently."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(logger_instance=mock_logger, raises=False)
        def sync_func() -> int:
            return 42

        @log_async_runtime_errors(logger_instance=mock_logger, raises=False)
        async def async_func() -> int:
            return 42

        # Both should execute normally
        sync_result = sync_func()
        assert sync_result == 42

    def test_nested_exception_handling(self) -> None:
        """Test that exceptions are properly chained when re-raised."""
        mock_logger = MagicMock(spec=logging.Logger)

        @log_runtime_errors(
            logger_instance=mock_logger, raises=True, raises_exception=RuntimeError,
        )
        def test_func() -> None:
            raise ValueError("Original error")

        with pytest.raises(RuntimeError) as exc_info:
            test_func()

        # Check that original exception is in the chain
        assert exc_info.value.__cause__.__class__.__name__ == "ValueError"
