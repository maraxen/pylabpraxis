# pylint: disable=redefined-outer-name, protected-access, unused-argument, invalid-name, too-many-locals, too-many-statements
"""Unit tests for the protocol decorator.

This test suite is structured to ensure isolation. Decorated functions are defined
within test functions or fixtures, not at the module level. This prevents the
global PROTOCOL_REGISTRY from becoming shared state across tests and ensures
each test case is self-contained and deterministic.
"""

import uuid
from collections.abc import Callable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pylabrobot.resources import Plate, Resource, TipRack

from praxis.backend.core.decorators import (
  DEFAULT_DECK_PARAM_NAME,
  DEFAULT_STATE_PARAM_NAME,
  praxis_run_context_cv,
  protocol_function,
)
from praxis.backend.core.orchestrator import ProtocolCancelledError
from praxis.backend.core.run_context import PROTOCOL_REGISTRY, PraxisRunContext
from praxis.backend.models import (
  FunctionCallStatusEnum,
  ProtocolRunStatusEnum,
)

# --- Test Constants (Static UUIDv7) ---
TEST_RUN_ID = uuid.UUID("018f5a6b-822e-7264-8c88-6625b8b2e16b")
TEST_DEF_ID = uuid.UUID("018f5b4f-40e9-74e9-8692-23c2a4f4c978")
TEST_CALL_LOG_ID = uuid.UUID("018f5a6c-940e-7973-874d-e9c8a2b55f19")


# --- Fixtures ---


@pytest.fixture(autouse=True)
def manage_registry_and_contextvar():
  """Fixture to ensure a clean slate for each test."""
  original_registry = PROTOCOL_REGISTRY.copy()
  PROTOCOL_REGISTRY.clear()
  # Set a valid, but empty, context to satisfy type hints.
  # Tests that require a real context will overwrite this.
  token = praxis_run_context_cv.set(MagicMock(spec=PraxisRunContext))
  yield
  praxis_run_context_cv.reset(token)
  PROTOCOL_REGISTRY.clear()
  PROTOCOL_REGISTRY.update(original_registry)


@pytest.fixture
def mock_run_context() -> MagicMock:
  """Provides a mock PraxisRunContext for runtime tests."""
  context = MagicMock(spec=PraxisRunContext)
  context.run_accession_id = TEST_RUN_ID
  context.current_db_session = AsyncMock()
  context.canonical_state = MagicMock()
  context.get_and_increment_sequence_val.return_value = 1
  context.create_context_for_nested_call.return_value = context
  context.current_call_log_db_accession_id = None
  return context


# --- Test Classes ---


@pytest.mark.asyncio
class TestProtocolDecoratorSetup:
  """Tests the decorator's setup-time behavior (static analysis, registry population).
  Functions are decorated inside each test to ensure isolation.
  """

  async def test_registry_population_and_full_parsing(self) -> None:
    """Test that a decorated function is correctly parsed and added to the registry."""

    # Arrange
    async def my_protocol(
      state: dict,
      source: Plate,
      tips: TipRack | None,
      volume: float = 100.0,
      enabled: bool = True,
      target: Plate | None = None,
    ) -> None:
      """A sample protocol."""

    # Act
    decorator = await protocol_function(
      name="test_protocol",
      version="1.0",
      is_top_level=True,
      description="Custom Description",
      param_metadata={
        "volume": {"description": "The volume in uL"},
        "enabled": {"ui_hints": {"label": "Enable Feature"}},
      },
    )
    decorator(my_protocol)

    # Assert
    assert "test_protocol_v1.0" in PROTOCOL_REGISTRY
    runtime_info = PROTOCOL_REGISTRY["test_protocol_v1.0"]
    definition = runtime_info.pydantic_definition

    assert definition.name == "test_protocol"
    assert definition.version == "1.0"
    assert definition.is_top_level is True
    assert definition.description == "Custom Description"
    assert definition.function_name == "my_protocol"

    params = {p.name: p for p in definition.parameters}
    assets = {a.name: a for a in definition.assets}

    assert "state" in params
    assert "volume" in params
    assert "enabled" in params
    assert "source" in assets
    assert "tips" in assets
    assert "target" in assets

    # Check parameter details
    assert params["volume"].optional is True
    assert params["volume"].default_value_repr == "100.0"
    assert params["volume"].description == "The volume in uL"
    assert params["enabled"].ui_hints.label == "Enable Feature"
    assert (
      params["enabled"].actual_type_str == "bool"
    )  # Ensure it resolves to the simple type

    # Check asset details
    assert assets["source"].optional is False
    assert assets["source"].actual_type_str == "Plate"
    assert assets["tips"].optional is True
    assert (
      "Optional[pylabrobot.resources.tip_rack.TipRack]" in assets["tips"].type_hint_str
    )
    assert (
      "Union[pylabrobot.resources.plate.Plate, NoneType]"
      in assets["target"].type_hint_str
    )

  async def test_raises_error_for_missing_state_param_for_top_level(self) -> None:
    """Test a TypeError is raised for a top-level protocol without a state parameter."""

    async def invalid_top_level(plate: Plate) -> None:
      pass

    decorator = await protocol_function(is_top_level=True)
    with pytest.raises(
      TypeError, match=f"must define a '{DEFAULT_STATE_PARAM_NAME}' parameter",
    ):
      decorator(invalid_top_level)

  async def test_raises_error_for_missing_deck_param_with_preconfigure(self) -> None:
    """Test a TypeError is raised if preconfigure_deck is True but the deck is missing."""

    async def invalid_deck_protocol(state: dict) -> None:
      pass

    decorator = await protocol_function(preconfigure_deck=True)
    with pytest.raises(TypeError, match=f"missing '{DEFAULT_DECK_PARAM_NAME}' param"):
      decorator(invalid_deck_protocol)

  async def test_raises_error_for_invalid_top_level_name(self) -> None:
    """Test a ValueError is raised for an invalid top-level protocol name."""

    async def protocol_with_bad_name(state: dict) -> None:
      pass

    decorator = await protocol_function(name="invalid-name!", is_top_level=True)
    with pytest.raises(ValueError, match="does not match format"):
      decorator(protocol_with_bad_name)


@pytest.mark.asyncio
class TestProtocolDecoratorRuntime:
  """Tests the decorator's runtime wrapper logic.
  Uses a fixture to provide a pre-decorated function for testing.
  """

  @pytest.fixture
  async def decorated_protocol(self) -> Callable:
    """Provides a fully decorated and registered async function for runtime tests."""

    async def my_runtime_protocol(state: dict, volume: float, resource: Resource):
      if volume < 0:
        msg = "Volume cannot be negative"
        raise ValueError(msg)
      return {"status": "ok", "volume_processed": volume}

    decorator = await protocol_function(
      name="runtime_protocol", version="1.0", is_top_level=True,
    )
    decorated_func = decorator(my_runtime_protocol)
    PROTOCOL_REGISTRY["runtime_protocol_v1.0"].db_accession_id = TEST_DEF_ID
    return decorated_func

  @pytest.fixture
  async def decorated_sync_protocol(self) -> Callable:
    """Provides a decorated and registered synchronous function."""

    def my_sync_protocol(state: dict) -> str:
      return "sync complete"

    decorator = await protocol_function(
      name="sync_protocol", version="1.0", is_top_level=True,
    )
    decorated_func = decorator(my_sync_protocol)
    PROTOCOL_REGISTRY["sync_protocol_v1.0"].db_accession_id = TEST_DEF_ID
    return decorated_func

  @patch(
    "praxis.backend.core.decorators.get_control_command",
    new_callable=AsyncMock,
    return_value=None,
  )
  @patch("praxis.backend.core.decorators.log_function_call_end", new_callable=AsyncMock)
  @patch(
    "praxis.backend.core.decorators.log_function_call_start", new_callable=AsyncMock,
  )
  async def test_wrapper_successful_execution(
    self,
    mock_start,
    mock_end,
    mock_get_control,
    decorated_protocol,
    mock_run_context,
  ) -> None:
    """Test a successful run of a decorated async function."""
    praxis_run_context_cv.set(mock_run_context)
    mock_call_log_orm = MagicMock(accession_id=TEST_CALL_LOG_ID)
    mock_start.return_value = mock_call_log_orm
    mock_resource = MagicMock(spec=Resource)

    result = await decorated_protocol(state={}, volume=150.0, resource=mock_resource)

    assert result == {"status": "ok", "volume_processed": 150.0}
    mock_start.assert_awaited_once()
    mock_end.assert_awaited_once()
    end_kwargs = mock_end.await_args.kwargs
    assert end_kwargs["status"] == FunctionCallStatusEnum.SUCCESS
    assert '"volume_processed": 150.0' in end_kwargs["return_value_json"]
    assert end_kwargs["error_message"] is None

  @patch(
    "praxis.backend.core.decorators.get_control_command",
    new_callable=AsyncMock,
    return_value=None,
  )
  @patch("praxis.backend.core.decorators.log_function_call_end", new_callable=AsyncMock)
  @patch(
    "praxis.backend.core.decorators.log_function_call_start", new_callable=AsyncMock,
  )
  async def test_wrapper_handles_sync_function(
    self,
    mock_start,
    mock_end,
    mock_get_control,
    decorated_sync_protocol,
    mock_run_context,
  ) -> None:
    """Test that a synchronous decorated function is run in an executor."""
    praxis_run_context_cv.set(mock_run_context)
    mock_call_log_orm = MagicMock(accession_id=TEST_CALL_LOG_ID)
    mock_start.return_value = mock_call_log_orm

    result = await decorated_sync_protocol(state={})

    assert result == "sync complete"
    mock_end.assert_awaited_once()
    end_kwargs = mock_end.await_args.kwargs
    assert end_kwargs["status"] == FunctionCallStatusEnum.SUCCESS
    assert end_kwargs["return_value_json"] == '"sync complete"'

  @patch(
    "praxis.backend.core.decorators.get_control_command",
    new_callable=AsyncMock,
    return_value=None,
  )
  @patch("praxis.backend.core.decorators.log_function_call_end", new_callable=AsyncMock)
  @patch(
    "praxis.backend.core.decorators.log_function_call_start", new_callable=AsyncMock,
  )
  async def test_wrapper_handles_exception(
    self,
    mock_start,
    mock_end,
    mock_get_control,
    decorated_protocol,
    mock_run_context,
  ) -> None:
    """Test that exceptions are caught, logged with ERROR status, and re-raised."""
    praxis_run_context_cv.set(mock_run_context)
    mock_call_log_orm = MagicMock(accession_id=TEST_CALL_LOG_ID)
    mock_start.return_value = mock_call_log_orm

    with pytest.raises(ValueError, match="Volume cannot be negative"):
      await decorated_protocol(state={}, volume=-10, resource=MagicMock())

    mock_end.assert_awaited_once()
    end_kwargs = mock_end.await_args.kwargs
    assert end_kwargs["status"] == FunctionCallStatusEnum.ERROR
    assert "Volume cannot be negative" in end_kwargs["error_message"]
    assert "ValueError" in end_kwargs["error_traceback"]

  async def test_wrapper_fails_without_valid_context(
    self, decorated_protocol, monkeypatch,
  ) -> None:
    """Test that calling a decorated function without a proper context raises a RuntimeError."""
    monkeypatch.setattr(praxis_run_context_cv, "get", lambda: None)
    with pytest.raises(RuntimeError, match="No PraxisRunContext found"):
      await decorated_protocol(state={}, volume=50, resource=MagicMock())

  @patch("praxis.backend.core.decorators.clear_control_command", new_callable=AsyncMock)
  @patch("praxis.backend.core.decorators.get_control_command", new_callable=AsyncMock)
  @patch(
    "praxis.backend.core.decorators.update_protocol_run_status",
    new_callable=AsyncMock,
  )
  @patch(
    "praxis.backend.core.decorators.log_function_call_start", new_callable=AsyncMock,
  )
  async def test_run_control_cancel(
    self,
    mock_start,
    mock_update_status,
    mock_get_control,
    mock_clear_control,
    decorated_protocol,
    mock_run_context,
  ) -> None:
    """Test the CANCEL control flow, ensuring it raises ProtocolCancelledError."""
    praxis_run_context_cv.set(mock_run_context)
    mock_start.return_value = MagicMock(accession_id=TEST_CALL_LOG_ID)
    mock_get_control.return_value = "CANCEL"

    with pytest.raises(ProtocolCancelledError):
      await decorated_protocol(state={}, volume=50, resource=MagicMock())

    status_updates = [call.args[1] for call in mock_update_status.call_args_list]
    assert ProtocolRunStatusEnum.CANCELING in status_updates
    assert ProtocolRunStatusEnum.CANCELLED in status_updates

  @patch("asyncio.sleep", new_callable=AsyncMock)
  @patch("praxis.backend.core.decorators.clear_control_command", new_callable=AsyncMock)
  @patch("praxis.backend.core.decorators.get_control_command", new_callable=AsyncMock)
  @patch(
    "praxis.backend.core.decorators.update_protocol_run_status",
    new_callable=AsyncMock,
  )
  @patch("praxis.backend.core.decorators.log_function_call_end", new_callable=AsyncMock)
  @patch(
    "praxis.backend.core.decorators.log_function_call_start", new_callable=AsyncMock,
  )
  async def test_run_control_pause_resume(
    self,
    mock_start,
    mock_end,
    mock_update_status,
    mock_get_control,
    mock_clear_control,
    mock_sleep,
    decorated_protocol,
    mock_run_context,
  ) -> None:
    """Test the PAUSE/RESUME control flow."""
    praxis_run_context_cv.set(mock_run_context)
    mock_start.return_value = MagicMock(accession_id=TEST_CALL_LOG_ID)
    # Simulate: PAUSE, then RESUME, then finish the run
    mock_get_control.side_effect = ["PAUSE", "RESUME", None]
    mock_resource = MagicMock(spec=Resource)

    result = await decorated_protocol(state={}, volume=50, resource=mock_resource)

    assert result is not None  # Should complete successfully
    mock_sleep.assert_awaited_once_with(1)

    status_updates = [call.args[1] for call in mock_update_status.call_args_list]
    assert ProtocolRunStatusEnum.PAUSING in status_updates
    assert ProtocolRunStatusEnum.PAUSED in status_updates
    assert ProtocolRunStatusEnum.RESUMING in status_updates
    assert ProtocolRunStatusEnum.RUNNING in status_updates

    # Check clear was called for PAUSE, RESUME
    assert mock_clear_control.call_count == 2
    # Check final log has SUCCESS status
    mock_end.assert_awaited_once()
    assert mock_end.await_args.kwargs["status"] == FunctionCallStatusEnum.SUCCESS
