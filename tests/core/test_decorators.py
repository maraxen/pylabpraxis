# pylint: disable=redefined-outer-name, protected-access, unused-argument, invalid-name, too-many-locals
"""Unit tests for the protocol decorator.

This test suite is structured to ensure isolation. Decorated functions are defined
within test functions or fixtures, not at the module level. This prevents the
global PROTOCOL_REGISTRY from becoming shared state across tests and ensures
each test case is self-contained and deterministic.
"""

import inspect
import uuid
from typing import Callable, Dict, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pylabrobot.resources import Plate, TipRack

# FIX: Import the decorator correctly. It's an async function returning a decorator.
from praxis.backend.core.decorators import protocol_function
from praxis.backend.core.orchestrator import ProtocolCancelledError
from praxis.backend.core.run_context import PROTOCOL_REGISTRY, PraxisRunContext
from praxis.backend.models import (
  AssetRequirementModel,
  FunctionCallStatusEnum,
  FunctionProtocolDefinitionModel,
  ParameterMetadataModel,
  ProtocolRunStatusEnum,
)
from praxis.backend.core.decorators import praxis_run_context_cv

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
  # FIX: Set a valid, but empty, context to satisfy type hints.
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
  context.get_and_increment_sequence_val.return_value = 1
  context.create_context_for_nested_call.return_value = context
  context.current_call_log_db_accession_id = None
  return context


# --- Test Classes ---


class TestProtocolDecoratorSetup:
  """
  Tests the decorator's setup-time behavior (static analysis, registry population).
  Functions are decorated inside each test to ensure isolation.
  """

  @pytest.mark.asyncio
  async def test_registry_population_and_parsing(self):
    """Test that a decorated function is correctly parsed and added to the registry."""

    # Arrange: Define the function to be decorated *inside* the test.
    async def my_protocol(state: dict, source: Plate, volume: float = 100.0):
      """A sample protocol."""

    # Act: Apply the decorator. The decorator itself is an async function.
    decorator = await protocol_function(
      name="test_protocol",
      version="1.0",
      is_top_level=True,
      assets=[
        AssetRequirementModel(
          accession_id=uuid.uuidv7(),
          name="tips",
          fqn="pylabrobot.resources.TipRack",
          optional=True,
        )
      ],
    )
    decorated_func = decorator(my_protocol)

    # Assert: Check the global registry
    assert "test_protocol_v1.0" in PROTOCOL_REGISTRY
    runtime_info = PROTOCOL_REGISTRY["test_protocol_v1.0"]
    definition = runtime_info.pydantic_definition

    assert definition.name == "test_protocol"
    assert definition.version == "1.0"
    assert definition.is_top_level is True
    assert definition.description == "A sample protocol."
    assert definition.function_name == "my_protocol"

    param_names = {p.name for p in definition.parameters}
    asset_names = {a.name for a in definition.assets}

    assert "state" in param_names
    assert "volume" in param_names
    assert "source" in asset_names
    assert "tips" in asset_names

  @pytest.mark.asyncio
  async def test_raises_error_for_missing_state_param_for_top_level(self):
    """Test a TypeError is raised for a top-level protocol without a state parameter."""

    async def invalid_top_level(plate: Plate):
      pass

    decorator = await protocol_function(is_top_level=True)
    with pytest.raises(TypeError, match="must define a 'state' parameter"):
      decorator(invalid_top_level)

  @pytest.mark.asyncio
  async def test_raises_error_for_invalid_top_level_name(self):
    """Test a ValueError is raised for an invalid top-level protocol name."""

    async def protocol_with_bad_name(state: dict):
      pass

    decorator = await protocol_function(name="invalid-name!", is_top_level=True)
    with pytest.raises(ValueError, match="does not match format"):
      decorator(protocol_with_bad_name)


@pytest.mark.asyncio
class TestProtocolDecoratorRuntime:
  """
  Tests the decorator's runtime wrapper logic.
  Uses a fixture to provide a pre-decorated function for testing.
  """

  @pytest.fixture
  async def decorated_protocol_in_registry(self) -> Callable:
    """Provides a fully decorated and registered async function for runtime tests."""

    async def my_runtime_protocol(state: dict, volume: float):
      if volume < 0:
        raise ValueError("Volume cannot be negative")
      return {"status": "ok", "volume_processed": volume}

    decorator = await protocol_function(
      name="runtime_protocol", version="1.0", is_top_level=True
    )
    decorated_func = decorator(my_runtime_protocol)
    PROTOCOL_REGISTRY["runtime_protocol_v1.0"].db_accession_id = TEST_DEF_ID
    return decorated_func

  async def test_wrapper_successful_execution(
    self, decorated_protocol_in_registry, mock_run_context
  ):
    """Test a successful run of a decorated function, checking logs and return value."""
    praxis_run_context_cv.set(mock_run_context)
    mock_call_log_orm = MagicMock(accession_id=TEST_CALL_LOG_ID)

    with patch(
      "praxis.backend.core.decorators.log_function_call_start",
      new_callable=AsyncMock,
      return_value=mock_call_log_orm,
    ) as mock_start, patch(
      "praxis.backend.core.decorators.log_function_call_end", new_callable=AsyncMock
    ) as mock_end, patch(
      "praxis.backend.core.decorators.get_control_command",
      new_callable=AsyncMock,
      return_value=None,
    ):
      result = await decorated_protocol_in_registry(state={}, volume=150.0)

      assert result == {"status": "ok", "volume_processed": 150.0}
      mock_start.assert_awaited_once()
      # FIX: Ensure mocked call_args have the kwargs attribute to avoid NoneType error
      mock_end.assert_awaited_once()
      assert mock_end.await_args.kwargs["status"] == FunctionCallStatusEnum.SUCCESS
      assert (
        '"volume_processed": 150.0' in mock_end.await_args.kwargs["return_value_json"]
      )

  async def test_wrapper_handles_exception(
    self, decorated_protocol_in_registry, mock_run_context
  ):
    """Test that exceptions are caught, logged with ERROR status, and re-raised."""
    praxis_run_context_cv.set(mock_run_context)
    mock_call_log_orm = MagicMock(accession_id=uuid.uuidv7())

    with patch(
      "praxis.backend.core.decorators.log_function_call_start",
      new_callable=AsyncMock,
      return_value=mock_call_log_orm,
    ), patch(
      "praxis.backend.core.decorators.log_function_call_end", new_callable=AsyncMock
    ) as mock_end:
      with pytest.raises(ValueError, match="Volume cannot be negative"):
        await decorated_protocol_in_registry(state={}, volume=-10)

      mock_end.assert_awaited_once()
      assert mock_end.await_args.kwargs["status"] == FunctionCallStatusEnum.ERROR
      assert "Volume cannot be negative" in mock_end.await_args.kwargs["error_message"]

  async def test_wrapper_fails_without_valid_context(
    self, decorated_protocol_in_registry
  ):
    """Test that calling a decorated function without a proper context raises a RuntimeError."""
    # The autouse fixture sets a mock, but let's test the None case explicitly
    praxis_run_context_cv.set(None)
    with pytest.raises(RuntimeError, match="No PraxisRunContext found"):
      await decorated_protocol_in_registry(state={}, volume=50)

  async def test_run_control_cancel(
    self, decorated_protocol_in_registry, mock_run_context
  ):
    """Test the CANCEL control flow, ensuring it raises ProtocolCancelledError."""
    praxis_run_context_cv.set(mock_run_context)

    with patch(
      "praxis.backend.core.decorators.log_function_call_start",
      new_callable=AsyncMock,
      return_value=MagicMock(accession_id=uuid.uuidv7()),
    ), patch(
      "praxis.backend.core.decorators.update_protocol_run_status",
      new_callable=AsyncMock,
    ) as mock_update_status, patch(
      "praxis.backend.core.decorators.get_control_command",
      new_callable=AsyncMock,
      return_value="CANCEL",
    ), patch(
      "praxis.backend.core.decorators.clear_control_command", new_callable=AsyncMock
    ):
      with pytest.raises(ProtocolCancelledError):
        await decorated_protocol_in_registry(state={}, volume=50)

      status_updates = [call.args[1] for call in mock_update_status.call_args_list]
      assert ProtocolRunStatusEnum.CANCELING in status_updates
      assert ProtocolRunStatusEnum.CANCELLED in status_updates
