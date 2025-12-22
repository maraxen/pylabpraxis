"""Tests for WebSocket endpoints."""
import asyncio
import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest

from praxis.backend.api.websockets import websocket_endpoint


class MockWebSocket:
    """Mock WebSocket for testing."""

    def __init__(self):
        self.accepted = False
        self.closed = False
        self.close_code = None
        self.messages = []
        self.app = Mock()
        self.app.state = Mock()

    async def accept(self):
        """Mock accept method."""
        self.accepted = True

    async def send_json(self, data):
        """Mock send_json method."""
        self.messages.append(data)

    async def close(self, code=1000):
        """Mock close method."""
        self.closed = True
        self.close_code = code


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator with protocol_run_service."""
    orchestrator = Mock()
    orchestrator.protocol_run_service = Mock()
    return orchestrator


class TestWebSocketEndpoint:
    """Test suite for WebSocket execution endpoint."""

    @pytest.mark.asyncio
    async def test_websocket_connection_and_completion(self, mock_orchestrator):
        """Test successful WebSocket connection and completion flow."""
        run_id = str(uuid.uuid4())
        websocket = MockWebSocket()
        websocket.app.state.orchestrator = mock_orchestrator

        # Mock the status to return completed immediately
        mock_orchestrator.protocol_run_service.get_protocol_run_status = AsyncMock(
            return_value={
                "status": "COMPLETED",
                "progress": 100,
                "logs": [],
                "current_step_name": "Done"
            }
        )

        # Patch asyncio.sleep to avoid delays
        with patch('praxis.backend.api.websockets.asyncio.sleep', new_callable=AsyncMock):
            await websocket_endpoint(websocket, run_id)

        # Verify websocket was accepted
        assert websocket.accepted

        # Verify messages were sent
        assert len(websocket.messages) > 0

        # Find status message
        status_messages = [m for m in websocket.messages if m["type"] == "status"]
        assert len(status_messages) >= 1
        assert status_messages[0]["payload"]["status"] == "COMPLETED"

        # Find progress message
        progress_messages = [m for m in websocket.messages if m["type"] == "progress"]
        assert len(progress_messages) >= 1

        # Find complete message
        complete_messages = [m for m in websocket.messages if m["type"] == "complete"]
        assert len(complete_messages) == 1

    @pytest.mark.asyncio
    async def test_websocket_status_progression(self, mock_orchestrator):
        """Test that status updates are sent when status changes."""
        run_id = str(uuid.uuid4())
        websocket = MockWebSocket()
        websocket.app.state.orchestrator = mock_orchestrator

        # Simulate status progression
        statuses = [
            {"status": "PREPARING", "progress": 0, "logs": [], "current_step_name": "Preparing"},
            {"status": "RUNNING", "progress": 50, "logs": [], "current_step_name": "Running"},
            {"status": "COMPLETED", "progress": 100, "logs": [], "current_step_name": "Done"},
        ]

        status_iter = iter(statuses)

        async def get_status_side_effect(run_uuid):
            try:
                return next(status_iter)
            except StopIteration:
                return statuses[-1]

        mock_orchestrator.protocol_run_service.get_protocol_run_status = AsyncMock(
            side_effect=get_status_side_effect
        )

        with patch('asyncio.sleep', new_callable=AsyncMock):
            await websocket_endpoint(websocket, run_id)

        # Verify status messages for each state
        status_messages = [m for m in websocket.messages if m["type"] == "status"]
        assert len(status_messages) == 3

        assert status_messages[0]["payload"]["status"] == "PREPARING"
        assert status_messages[0]["payload"]["step"] == "Preparing"

        assert status_messages[1]["payload"]["status"] == "RUNNING"
        assert status_messages[1]["payload"]["step"] == "Running"

        assert status_messages[2]["payload"]["status"] == "COMPLETED"

    @pytest.mark.asyncio
    async def test_websocket_log_streaming(self, mock_orchestrator):
        """Test that new logs are streamed to the client."""
        run_id = str(uuid.uuid4())
        websocket = MockWebSocket()
        websocket.app.state.orchestrator = mock_orchestrator

        # Simulate logs being added over time
        logs_progression = [
            {"status": "RUNNING", "progress": 10, "logs": ["Log 1"], "current_step_name": "Step 1"},
            {"status": "RUNNING", "progress": 20, "logs": ["Log 1", "Log 2"], "current_step_name": "Step 2"},
            {"status": "COMPLETED", "progress": 100, "logs": ["Log 1", "Log 2", "Log 3"], "current_step_name": "Done"},
        ]

        logs_iter = iter(logs_progression)

        async def get_status_side_effect(run_uuid):
            try:
                return next(logs_iter)
            except StopIteration:
                return logs_progression[-1]

        mock_orchestrator.protocol_run_service.get_protocol_run_status = AsyncMock(
            side_effect=get_status_side_effect
        )

        with patch('asyncio.sleep', new_callable=AsyncMock):
            await websocket_endpoint(websocket, run_id)

        # Verify log messages were sent
        log_messages = [m for m in websocket.messages if m["type"] == "log"]
        assert len(log_messages) == 3

        assert log_messages[0]["payload"]["message"] == "Log 1"
        assert log_messages[1]["payload"]["message"] == "Log 2"
        assert log_messages[2]["payload"]["message"] == "Log 3"

        # All logs should have level INFO
        for log_msg in log_messages:
            assert log_msg["payload"]["level"] == "INFO"

    @pytest.mark.asyncio
    async def test_websocket_failed_execution(self, mock_orchestrator):
        """Test WebSocket behavior when execution fails."""
        run_id = str(uuid.uuid4())
        websocket = MockWebSocket()
        websocket.app.state.orchestrator = mock_orchestrator

        # Mock a failed execution
        mock_orchestrator.protocol_run_service.get_protocol_run_status = AsyncMock(
            return_value={
                "status": "FAILED",
                "progress": 50,
                "logs": ["Error occurred"],
                "current_step_name": "Failed"
            }
        )

        with patch('asyncio.sleep', new_callable=AsyncMock):
            await websocket_endpoint(websocket, run_id)

        # Verify error message was sent
        error_messages = [m for m in websocket.messages if m["type"] == "error"]
        assert len(error_messages) == 1
        assert "failed" in error_messages[0]["payload"]["error"].lower()

        # Verify status message
        status_messages = [m for m in websocket.messages if m["type"] == "status"]
        assert status_messages[0]["payload"]["status"] == "FAILED"

    @pytest.mark.asyncio
    async def test_websocket_cancelled_execution(self, mock_orchestrator):
        """Test WebSocket behavior when execution is cancelled."""
        run_id = str(uuid.uuid4())
        websocket = MockWebSocket()
        websocket.app.state.orchestrator = mock_orchestrator

        # Mock a cancelled execution
        mock_orchestrator.protocol_run_service.get_protocol_run_status = AsyncMock(
            return_value={
                "status": "CANCELLED",
                "progress": 30,
                "logs": [],
                "current_step_name": "Cancelled"
            }
        )

        with patch('asyncio.sleep', new_callable=AsyncMock):
            await websocket_endpoint(websocket, run_id)

        # Verify status message
        status_messages = [m for m in websocket.messages if m["type"] == "status"]
        assert status_messages[0]["payload"]["status"] == "CANCELLED"

        # Should not have complete or error message for CANCELLED
        complete_messages = [m for m in websocket.messages if m["type"] == "complete"]
        error_messages = [m for m in websocket.messages if m["type"] == "error"]
        assert len(complete_messages) == 0
        assert len(error_messages) == 0

    @pytest.mark.asyncio
    async def test_websocket_invalid_uuid(self, mock_orchestrator):
        """Test WebSocket with invalid UUID format."""
        invalid_run_id = "not-a-valid-uuid"
        websocket = MockWebSocket()
        websocket.app.state.orchestrator = mock_orchestrator

        await websocket_endpoint(websocket, invalid_run_id)

        # Should close with code 1003 (invalid data)
        assert websocket.closed
        assert websocket.close_code == 1003

    @pytest.mark.asyncio
    async def test_websocket_progress_updates_every_poll(self, mock_orchestrator):
        """Test that progress updates are sent on every poll cycle."""
        run_id = str(uuid.uuid4())
        websocket = MockWebSocket()
        websocket.app.state.orchestrator = mock_orchestrator

        # Same status, changing progress
        statuses = [
            {"status": "RUNNING", "progress": 25, "logs": [], "current_step_name": "Processing"},
            {"status": "RUNNING", "progress": 50, "logs": [], "current_step_name": "Processing"},
            {"status": "COMPLETED", "progress": 100, "logs": [], "current_step_name": "Done"},
        ]

        status_iter = iter(statuses)

        async def get_status_side_effect(run_uuid):
            try:
                return next(status_iter)
            except StopIteration:
                return statuses[-1]

        mock_orchestrator.protocol_run_service.get_protocol_run_status = AsyncMock(
            side_effect=get_status_side_effect
        )

        with patch('asyncio.sleep', new_callable=AsyncMock):
            await websocket_endpoint(websocket, run_id)

        # Verify progress messages sent for each poll
        progress_messages = [m for m in websocket.messages if m["type"] == "progress"]
        assert len(progress_messages) == 3

        assert progress_messages[0]["payload"]["progress"] == 25
        assert progress_messages[1]["payload"]["progress"] == 50
        assert progress_messages[2]["payload"]["progress"] == 100

    @pytest.mark.asyncio
    async def test_websocket_handles_service_exception(self, mock_orchestrator):
        """Test that WebSocket handles exceptions from the service gracefully."""
        run_id = str(uuid.uuid4())
        websocket = MockWebSocket()
        websocket.app.state.orchestrator = mock_orchestrator

        # First call raises exception, second succeeds
        call_count = 0

        async def get_status_side_effect(run_uuid):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Database connection error")
            return {
                "status": "COMPLETED",
                "progress": 100,
                "logs": [],
                "current_step_name": "Done"
            }

        mock_orchestrator.protocol_run_service.get_protocol_run_status = AsyncMock(
            side_effect=get_status_side_effect
        )

        with patch('asyncio.sleep', new_callable=AsyncMock):
            await websocket_endpoint(websocket, run_id)

        # After the exception, it should retry and get the status
        status_messages = [m for m in websocket.messages if m["type"] == "status"]
        assert len(status_messages) == 1
        assert status_messages[0]["payload"]["status"] == "COMPLETED"

        # Verify we retried
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_websocket_log_dict_format(self, mock_orchestrator):
        """Test that log entries can be dictionaries and are converted to strings."""
        run_id = str(uuid.uuid4())
        websocket = MockWebSocket()
        websocket.app.state.orchestrator = mock_orchestrator

        # Logs as dictionaries
        mock_orchestrator.protocol_run_service.get_protocol_run_status = AsyncMock(
            return_value={
                "status": "COMPLETED",
                "progress": 100,
                "logs": [{"level": "INFO", "message": "Test log", "timestamp": "2025-01-01"}],
                "current_step_name": "Done"
            }
        )

        with patch('asyncio.sleep', new_callable=AsyncMock):
            await websocket_endpoint(websocket, run_id)

        # Verify log was converted to string
        log_messages = [m for m in websocket.messages if m["type"] == "log"]
        assert len(log_messages) == 1
        assert isinstance(log_messages[0]["payload"]["message"], str)

    @pytest.mark.asyncio
    async def test_websocket_no_duplicate_status_messages(self, mock_orchestrator):
        """Test that status messages are only sent when status actually changes."""
        run_id = str(uuid.uuid4())
        websocket = MockWebSocket()
        websocket.app.state.orchestrator = mock_orchestrator

        # Status stays the same across polls
        mock_orchestrator.protocol_run_service.get_protocol_run_status = AsyncMock(
            side_effect=[
                {"status": "RUNNING", "progress": 10, "logs": [], "current_step_name": "Step 1"},
                {"status": "RUNNING", "progress": 20, "logs": [], "current_step_name": "Step 1"},
                {"status": "COMPLETED", "progress": 100, "logs": [], "current_step_name": "Done"},
            ]
        )

        with patch('asyncio.sleep', new_callable=AsyncMock):
            await websocket_endpoint(websocket, run_id)

        # Should only have 2 status messages (RUNNING once, then COMPLETED)
        status_messages = [m for m in websocket.messages if m["type"] == "status"]
        assert len(status_messages) == 2
        assert status_messages[0]["payload"]["status"] == "RUNNING"
        assert status_messages[1]["payload"]["status"] == "COMPLETED"

        # But should have 3 progress messages (one per poll)
        progress_messages = [m for m in websocket.messages if m["type"] == "progress"]
        assert len(progress_messages) == 3
