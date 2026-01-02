"""Additional runtime tests for protocol_decorator.py to achieve 80% coverage."""
from unittest.mock import AsyncMock, Mock, patch

import pytest

from praxis.backend.core.decorators import praxis_run_context_cv, protocol_function
from praxis.backend.core.decorators.protocol_decorator import (
    _handle_control_commands,
    _handle_pause_state,
    _log_call_start,
    _process_wrapper_arguments,
)
from praxis.backend.core.orchestrator import ProtocolCancelledError
from praxis.backend.core.run_context import PraxisRunContext
from praxis.backend.models.pydantic_internals.protocol import (
    FunctionCallStatusEnum,
    ProtocolRunStatusEnum,
)
from praxis.backend.utils.uuid import uuid7


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_run_context(mock_db_session):
    """Create a mock PraxisRunContext."""
    context = Mock(spec=PraxisRunContext)
    context.run_accession_id = uuid7()
    context.current_db_session = mock_db_session
    context.current_call_log_db_accession_id = uuid7()
    context.canonical_state = None
    context.get_and_increment_sequence_val = Mock(return_value=1)
    context.create_context_for_nested_call = Mock()

    # Create nested context
    nested_context = Mock(spec=PraxisRunContext)
    nested_context.run_accession_id = context.run_accession_id
    nested_context.current_db_session = mock_db_session
    nested_context.current_call_log_db_accession_id = uuid7()
    context.create_context_for_nested_call.return_value = nested_context

    return context


class TestLogCallStart:
    """Tests for _log_call_start function."""

    @pytest.mark.asyncio
    async def test_log_call_start_success(self, mock_run_context):
        """Test successful function call logging."""
        function_def_id = uuid7()
        parent_log_id = uuid7()

        # Mock the log_function_call_start service call
        with patch("praxis.backend.core.decorators.protocol_decorator.log_function_call_start") as mock_log:
            mock_log_entry = Mock()
            mock_log_entry.accession_id = uuid7()
            mock_log.return_value = mock_log_entry

            result = await _log_call_start(
                context=mock_run_context,
                function_def_db_id=function_def_id,
                parent_log_id=parent_log_id,
                args=(1, 2),
                kwargs={"volume": 100},
            )

            assert result == mock_log_entry.accession_id
            mock_log.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_call_start_exception_handling(self, mock_run_context):
        """Test that logging exceptions are caught and handled gracefully."""
        function_def_id = uuid7()

        with patch("praxis.backend.core.decorators.protocol_decorator.log_function_call_start") as mock_log:
            mock_log.side_effect = Exception("Database error")

            result = await _log_call_start(
                context=mock_run_context,
                function_def_db_id=function_def_id,
                parent_log_id=None,
                args=(),
                kwargs={},
            )

            assert result is None  # Should return None on error


class TestProcessWrapperArguments:
    """Tests for _process_wrapper_arguments function."""

    @pytest.mark.asyncio
    async def test_process_wrapper_arguments_basic(self, mock_run_context):
        """Test processing wrapper arguments."""
        from praxis.backend.core.decorators.models import ProtocolRuntimeInfo
        from praxis.backend.models.pydantic_internals.protocol import (
            FunctionProtocolDefinitionCreate,
        )

        # Create mock runtime info
        protocol_def = FunctionProtocolDefinitionCreate(
            name="test_protocol",
            version="1.0.0",
            description="Test",
            fqn="test.protocol",
            source_file_path="test_file.py",
            module_name="test_module",
            function_name="test_function",
            parameters=[],
            assets=[],
        )

        runtime_info = ProtocolRuntimeInfo(
            pydantic_definition=protocol_def,
            function_ref=lambda: None,
            found_state_param_details=None,
        )
        runtime_info.db_accession_id = uuid7()

        def test_func():
            pass

        with patch("praxis.backend.core.decorators.protocol_decorator._log_call_start") as mock_log:
            mock_log.return_value = uuid7()

            call_id, context, token = await _process_wrapper_arguments(
                parent_context=mock_run_context,
                current_meta=runtime_info,
                processed_args=[],
                processed_kwargs={},
                _state_param_name="state",
                _protocol_unique_key="test_protocol_v1.0.0",
                _func=test_func,
            )

            assert call_id is not None
            assert context is not None
            assert token is not None

    @pytest.mark.asyncio
    async def test_process_wrapper_arguments_missing_db_id(self, mock_run_context):
        """Test error when DB accession ID is missing."""
        from praxis.backend.core.decorators.models import ProtocolRuntimeInfo
        from praxis.backend.models.pydantic_internals.protocol import (
            FunctionProtocolDefinitionCreate,
        )

        protocol_def = FunctionProtocolDefinitionCreate(
            name="test_protocol",
            version="1.0.0",
            description="Test",
            fqn="test.protocol",
            source_file_path="test_file.py",
            module_name="test_module",
            function_name="test_function",
            parameters=[],
            assets=[],
        )

        runtime_info = ProtocolRuntimeInfo(
            pydantic_definition=protocol_def,
            function_ref=lambda: None,
            found_state_param_details=None,
        )
        # db_accession_id is already None by default - Missing!

        with pytest.raises(ValueError, match="Function definition DB accession ID is missing"):
            await _process_wrapper_arguments(
                parent_context=mock_run_context,
                current_meta=runtime_info,
                processed_args=[],
                processed_kwargs={},
                _state_param_name="state",
                _protocol_unique_key="test_protocol_v1.0.0",
                _func=lambda: None,
            )

    @pytest.mark.asyncio
    async def test_process_wrapper_arguments_with_state_param(self, mock_run_context):
        """Test processing with state parameter details."""
        from praxis.backend.core.decorators.models import ProtocolRuntimeInfo
        from praxis.backend.models.pydantic_internals.protocol import (
            FunctionProtocolDefinitionCreate,
        )

        protocol_def = FunctionProtocolDefinitionCreate(
            name="test_protocol",
            version="1.0.0",
            description="Test",
            fqn="test.protocol",
            source_file_path="test_file.py",
            module_name="test_module",
            function_name="test_function",
            parameters=[],
            assets=[],
        )

        state_param_details = {
            "name": "state",
            "expects_praxis_state": True,
            "expects_dict": False,
        }

        runtime_info = ProtocolRuntimeInfo(
            pydantic_definition=protocol_def,
            function_ref=lambda: None,
            found_state_param_details=state_param_details,
        )
        runtime_info.db_accession_id = uuid7()

        # Set up canonical state
        mock_state = Mock()
        mock_state.data = {"key": "value"}
        mock_run_context.canonical_state = mock_state

        kwargs = {"state": {}, "volume": 100}

        with patch("praxis.backend.core.decorators.protocol_decorator._log_call_start") as mock_log:
            mock_log.return_value = uuid7()

            _call_id, _context, _token = await _process_wrapper_arguments(
                parent_context=mock_run_context,
                current_meta=runtime_info,
                processed_args=[],
                processed_kwargs=kwargs,
                _state_param_name="state",
                _protocol_unique_key="test_protocol_v1.0.0",
                _func=lambda: None,
            )

            # State should be replaced with canonical state
            assert kwargs["state"] == mock_state


class TestHandlePauseState:
    """Tests for _handle_pause_state function."""

    @pytest.mark.asyncio
    async def test_handle_pause_resume(self, mock_db_session):
        """Test handling RESUME command while paused."""
        run_id = uuid7()

        # Mock get_control_command to return RESUME
        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            mock_get_cmd.return_value = "RESUME"

            # Mock asyncio.sleep to avoid delays
            with patch("praxis.backend.core.decorators.protocol_decorator.asyncio.sleep", new_callable=AsyncMock):
                result = await _handle_pause_state(run_id, mock_db_session)

                assert result == "RESUME"

    @pytest.mark.asyncio
    async def test_handle_pause_cancel(self, mock_db_session):
        """Test handling CANCEL command while paused."""
        run_id = uuid7()

        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            mock_get_cmd.return_value = "CANCEL"

            with patch("praxis.backend.core.decorators.protocol_decorator.asyncio.sleep", new_callable=AsyncMock):
                result = await _handle_pause_state(run_id, mock_db_session)

                assert result == "CANCEL"

    @pytest.mark.asyncio
    async def test_handle_pause_intervene(self, mock_db_session):
        """Test handling INTERVENE command while paused."""
        run_id = uuid7()

        # First INTERVENE, then RESUME
        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            mock_get_cmd.side_effect = ["INTERVENE", "RESUME"]

            with patch("praxis.backend.core.decorators.protocol_decorator.clear_control_command", new_callable=AsyncMock):
                with patch("praxis.backend.core.decorators.protocol_decorator.protocol_run_service") as mock_service:
                    mock_service.update_run_status = AsyncMock()

                    with patch("praxis.backend.core.decorators.protocol_decorator.asyncio.sleep", new_callable=AsyncMock):
                        result = await _handle_pause_state(run_id, mock_db_session)

                        assert result == "RESUME"
                        # Should have updated status to INTERVENING
                        assert mock_service.update_run_status.called

    @pytest.mark.asyncio
    async def test_handle_pause_duplicate_pause_ignored(self, mock_db_session):
        """Test that PAUSE command while already paused is ignored."""
        run_id = uuid7()

        # PAUSE then RESUME
        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            mock_get_cmd.side_effect = ["PAUSE", "RESUME"]

            with patch("praxis.backend.core.decorators.protocol_decorator.asyncio.sleep", new_callable=AsyncMock):
                result = await _handle_pause_state(run_id, mock_db_session)

                assert result == "RESUME"

    @pytest.mark.asyncio
    async def test_handle_pause_invalid_command_cleared(self, mock_db_session):
        """Test that invalid commands are cleared."""
        run_id = uuid7()

        # Invalid command, then RESUME
        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            mock_get_cmd.side_effect = ["INVALID", "RESUME"]

            with patch("praxis.backend.core.decorators.protocol_decorator.clear_control_command", new_callable=AsyncMock) as mock_clear:
                with patch("praxis.backend.core.decorators.protocol_decorator.asyncio.sleep", new_callable=AsyncMock):
                    result = await _handle_pause_state(run_id, mock_db_session)

                    assert result == "RESUME"
                    # Invalid command should be cleared
                    assert mock_clear.called


class TestHandleControlCommands:
    """Tests for _handle_control_commands function."""

    @pytest.mark.asyncio
    async def test_no_command(self, mock_db_session):
        """Test when there's no control command."""
        run_id = uuid7()

        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            mock_get_cmd.return_value = None

            # Should return immediately without error
            await _handle_control_commands(run_id, mock_db_session)

            mock_get_cmd.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_command_cleared(self, mock_db_session):
        """Test that invalid commands are cleared and loop continues."""
        run_id = uuid7()

        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            # Invalid command, then None
            mock_get_cmd.side_effect = ["INVALID_CMD", None]

            with patch("praxis.backend.core.decorators.protocol_decorator.clear_control_command", new_callable=AsyncMock) as mock_clear:
                await _handle_control_commands(run_id, mock_db_session)

                assert mock_clear.called

    @pytest.mark.asyncio
    async def test_pause_command(self, mock_db_session):
        """Test handling PAUSE command."""
        run_id = uuid7()

        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            # PAUSE, then None (after resume)
            mock_get_cmd.side_effect = ["PAUSE", None]

            with patch("praxis.backend.core.decorators.protocol_decorator.clear_control_command", new_callable=AsyncMock):
                with patch("praxis.backend.core.decorators.protocol_decorator.protocol_run_service") as mock_service:
                    mock_service.update_run_status = AsyncMock()

                    with patch("praxis.backend.core.decorators.protocol_decorator._handle_pause_state") as mock_pause:
                        mock_pause.return_value = "RESUME"

                        await _handle_control_commands(run_id, mock_db_session)

                        # Should update status to PAUSING, PAUSED, RESUMING, RUNNING
                        assert mock_service.update_run_status.call_count >= 4

    @pytest.mark.asyncio
    async def test_cancel_command(self, mock_db_session):
        """Test handling CANCEL command."""
        run_id = uuid7()

        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            mock_get_cmd.return_value = "CANCEL"

            with patch("praxis.backend.core.decorators.protocol_decorator.clear_control_command", new_callable=AsyncMock):
                with patch("praxis.backend.core.decorators.protocol_decorator.protocol_run_service") as mock_service:
                    mock_service.update_run_status = AsyncMock()

                    with pytest.raises(ProtocolCancelledError, match="cancelled by user"):
                        await _handle_control_commands(run_id, mock_db_session)

                    # Should update status to CANCELING and CANCELLED
                    assert mock_service.update_run_status.call_count == 2

    @pytest.mark.asyncio
    async def test_intervene_command(self, mock_db_session):
        """Test handling INTERVENE command."""
        run_id = uuid7()

        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            # INTERVENE, then None
            mock_get_cmd.side_effect = ["INTERVENE", None]

            with patch("praxis.backend.core.decorators.protocol_decorator.clear_control_command", new_callable=AsyncMock):
                with patch("praxis.backend.core.decorators.protocol_decorator.protocol_run_service") as mock_service:
                    mock_service.update_run_status = AsyncMock()

                    await _handle_control_commands(run_id, mock_db_session)

                    # Should update status to INTERVENING
                    mock_service.update_run_status.assert_called_with(
                        mock_db_session,
                        run_id,
                        ProtocolRunStatusEnum.INTERVENING,
                    )

    @pytest.mark.asyncio
    async def test_pause_then_cancel(self, mock_db_session):
        """Test PAUSE followed by CANCEL."""
        run_id = uuid7()

        with patch("praxis.backend.core.decorators.protocol_decorator.get_control_command") as mock_get_cmd:
            mock_get_cmd.return_value = "PAUSE"

            with patch("praxis.backend.core.decorators.protocol_decorator.clear_control_command", new_callable=AsyncMock):
                with patch("praxis.backend.core.decorators.protocol_decorator.protocol_run_service") as mock_service:
                    mock_service.update_run_status = AsyncMock()

                    with patch("praxis.backend.core.decorators.protocol_decorator._handle_pause_state") as mock_pause:
                        mock_pause.return_value = "CANCEL"

                        with pytest.raises(ProtocolCancelledError):
                            await _handle_control_commands(run_id, mock_db_session)


class TestProtocolFunctionWrapperRuntime:
    """Tests for protocol_function wrapper execution."""

    @pytest.mark.asyncio
    async def test_wrapper_async_function_execution(self, mock_run_context):
        """Test executing an async function through the wrapper."""
        # Define a decorated protocol
        @protocol_function(name="test_async_protocol", is_top_level=False)  # Not top-level
        async def async_protocol(volume: int):
            return {"result": volume * 2}

        # Set DB accession ID
        async_protocol._protocol_runtime_info.db_accession_id = uuid7()

        # Set context
        token = praxis_run_context_cv.set(mock_run_context)

        try:
            with patch("praxis.backend.core.decorators.protocol_decorator._process_wrapper_arguments") as mock_process:
                call_id = uuid7()
                nested_context = mock_run_context.create_context_for_nested_call.return_value
                # Create a real token by setting a nested context
                nested_token = praxis_run_context_cv.set(nested_context)
                mock_process.return_value = (call_id, nested_context, nested_token)

                with patch("praxis.backend.core.decorators.protocol_decorator.log_function_call_end", new_callable=AsyncMock):
                    result = await async_protocol(volume=100)

                    assert result == {"result": 200}
        finally:
            praxis_run_context_cv.reset(token)

    @pytest.mark.asyncio
    async def test_wrapper_sync_function_execution(self, mock_run_context):
        """Test executing a sync function through the wrapper."""
        @protocol_function(name="test_sync_protocol", is_top_level=False)  # Not top-level
        def sync_protocol(volume: int):
            return {"result": volume * 3}

        sync_protocol._protocol_runtime_info.db_accession_id = uuid7()

        token = praxis_run_context_cv.set(mock_run_context)

        try:
            with patch("praxis.backend.core.decorators.protocol_decorator._process_wrapper_arguments") as mock_process:
                call_id = uuid7()
                nested_context = mock_run_context.create_context_for_nested_call.return_value
                # Create a real token by setting a nested context
                nested_token = praxis_run_context_cv.set(nested_context)
                mock_process.return_value = (call_id, nested_context, nested_token)

                with patch("praxis.backend.core.decorators.protocol_decorator.log_function_call_end", new_callable=AsyncMock):
                    result = await sync_protocol(volume=50)

                    assert result == {"result": 150}
        finally:
            praxis_run_context_cv.reset(token)

    @pytest.mark.asyncio
    async def test_wrapper_error_handling(self, mock_run_context):
        """Test that errors in protocol functions are properly logged."""
        @protocol_function(name="test_error_protocol", is_top_level=False)  # Not top-level
        async def error_protocol():
            msg = "Test error"
            raise ValueError(msg)

        error_protocol._protocol_runtime_info.db_accession_id = uuid7()

        token = praxis_run_context_cv.set(mock_run_context)

        try:
            with patch("praxis.backend.core.decorators.protocol_decorator._process_wrapper_arguments") as mock_process:
                call_id = uuid7()
                nested_context = mock_run_context.create_context_for_nested_call.return_value
                # Create a real token by setting a nested context
                nested_token = praxis_run_context_cv.set(nested_context)
                mock_process.return_value = (call_id, nested_context, nested_token)

                with patch("praxis.backend.core.decorators.protocol_decorator.log_function_call_end", new_callable=AsyncMock) as mock_log:
                    with pytest.raises(ValueError, match="Test error"):
                        await error_protocol()

                    # Should log the error
                    assert mock_log.called
                    call_args = mock_log.call_args[1]
                    assert call_args["status"] == FunctionCallStatusEnum.ERROR
                    assert "Test error" in call_args["error_message"]
        finally:
            praxis_run_context_cv.reset(token)

    @pytest.mark.asyncio
    async def test_wrapper_missing_context_error(self):
        """Test error when no context is set."""
        @protocol_function(name="test_no_context", is_top_level=False)  # Not top-level
        async def no_context_protocol():
            return "result"

        no_context_protocol._protocol_runtime_info.db_accession_id = uuid7()

        # Don't set context - should raise error
        with pytest.raises(RuntimeError, match="No PraxisRunContext found"):
            await no_context_protocol()

    @pytest.mark.asyncio
    async def test_wrapper_missing_db_id_error(self, mock_run_context):
        """Test error when protocol is not registered (missing DB ID)."""
        @protocol_function(name="test_no_db_id", is_top_level=False)  # Not top-level
        async def no_db_id_protocol():
            return "result"

        # Don't set DB ID
        no_db_id_protocol._protocol_runtime_info.db_accession_id = None

        token = praxis_run_context_cv.set(mock_run_context)

        try:
            with pytest.raises(RuntimeError, match="not registered or missing DB ID"):
                await no_db_id_protocol()
        finally:
            praxis_run_context_cv.reset(token)

    @pytest.mark.asyncio
    async def test_wrapper_protocol_cancelled_error_propagation(self, mock_run_context):
        """Test that ProtocolCancelledError is propagated correctly."""
        @protocol_function(name="test_cancelled", is_top_level=False)  # Not top-level
        async def cancelled_protocol():
            msg = "Cancelled"
            raise ProtocolCancelledError(msg)

        cancelled_protocol._protocol_runtime_info.db_accession_id = uuid7()

        token = praxis_run_context_cv.set(mock_run_context)

        try:
            with patch("praxis.backend.core.decorators.protocol_decorator._process_wrapper_arguments") as mock_process:
                call_id = uuid7()
                nested_context = mock_run_context.create_context_for_nested_call.return_value
                # Create a real token by setting a nested context
                nested_token = praxis_run_context_cv.set(nested_context)
                mock_process.return_value = (call_id, nested_context, nested_token)

                with patch("praxis.backend.core.decorators.protocol_decorator.log_function_call_end", new_callable=AsyncMock):
                    with pytest.raises(ProtocolCancelledError):
                        await cancelled_protocol()
        finally:
            praxis_run_context_cv.reset(token)

    @pytest.mark.asyncio
    async def test_wrapper_logging_failure_doesnt_break_execution(self, mock_run_context):
        """Test that logging failures don't break protocol execution."""
        @protocol_function(name="test_log_failure", is_top_level=False)  # Not top-level
        async def log_failure_protocol():
            return "success"

        log_failure_protocol._protocol_runtime_info.db_accession_id = uuid7()

        token = praxis_run_context_cv.set(mock_run_context)

        try:
            with patch("praxis.backend.core.decorators.protocol_decorator._process_wrapper_arguments") as mock_process:
                call_id = uuid7()
                nested_context = mock_run_context.create_context_for_nested_call.return_value
                # Create a real token by setting a nested context
                nested_token = praxis_run_context_cv.set(nested_context)
                mock_process.return_value = (call_id, nested_context, nested_token)

                # Make logging fail
                with patch("praxis.backend.core.decorators.protocol_decorator.log_function_call_end", new_callable=AsyncMock) as mock_log:
                    mock_log.side_effect = Exception("Logging failed")

                    # Should still return result despite logging failure
                    result = await log_failure_protocol()
                    assert result == "success"
        finally:
            praxis_run_context_cv.reset(token)
