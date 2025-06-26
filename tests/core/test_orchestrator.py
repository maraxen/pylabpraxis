# pylint: disable=redefined-outer-name, protected-access, unused-argument, invalid-name, too-many-locals
"""Unit tests for the Orchestrator.

These tests validate the logic of the Orchestrator class, ensuring it correctly
manages the lifecycle of a protocol run. Dependencies are mocked to test the
Orchestrator's logic in isolation, following the principles outlined in the
TESTING_STRATEGY.md.
"""

import uuid
from unittest.mock import ANY, AsyncMock, MagicMock, call, patch

import pytest

from praxis.backend.core.decorators import ProtocolRuntimeInfo
from praxis.backend.core.orchestrator import Orchestrator, ProtocolCancelledError
from praxis.backend.core.run_context import PROTOCOL_REGISTRY
from praxis.backend.models import (
  AssetRequirementModel,
  FunctionProtocolDefinitionModel,
  ProtocolRunStatusEnum,
)

# --- Test Constants ---
TEST_RUN_ID = uuid.uuid4()
TEST_PROTOCOL_DEF_ID = uuid.uuid4()
TEST_PROTOCOL_NAME = "test_protocol"
TEST_PROTOCOL_VERSION = "1.0.0"


# --- Fixtures ---


@pytest.fixture
def mock_db_session() -> AsyncMock:
  """Provide a mock SQLAlchemy async session."""
  return AsyncMock()


@pytest.fixture
def mock_workcell() -> MagicMock:
  """Provide a mock Workcell object."""
  return MagicMock()


@pytest.fixture
def mock_protocol_definition() -> FunctionProtocolDefinitionModel:
  """Provide a mock protocol definition model."""
  asset_req = AssetRequirementModel(
    accession_id=uuid.uuid4(),
    name="test_asset",
    fqn="pylabrobot.resources.resource.Resource",
  )
  return FunctionProtocolDefinitionModel(
    accession_id=TEST_PROTOCOL_DEF_ID,
    name=TEST_PROTOCOL_NAME,
    version=TEST_PROTOCOL_VERSION,
    assets=[asset_req],
    parameters=[],
    source_file_path="/fake/path.py",
    module_name="fake.path",
    function_name="my_protocol",
  )


@pytest.fixture
def orchestrator(mock_db_session: AsyncMock, mock_workcell: MagicMock) -> Orchestrator:
  """Provide an Orchestrator instance with mocked dependencies."""
  # Patch AssetManager and WorkcellRuntime for the orchestrator
  asset_manager = MagicMock()
  workcell_runtime = MagicMock()
  return Orchestrator(
    db_session_factory=mock_db_session,
    asset_manager=asset_manager,
    workcell_runtime=workcell_runtime,
  )


@pytest.fixture(autouse=True)
def clear_registry():
  """Clear the protocol registry before each test."""
  original_registry = PROTOCOL_REGISTRY.copy()
  PROTOCOL_REGISTRY.clear()
  yield
  PROTOCOL_REGISTRY.clear()
  PROTOCOL_REGISTRY.update(original_registry)


# --- Test Classes ---


@pytest.mark.asyncio
class TestOrchestratorExecution:
  """Tests the main execution flows of the Orchestrator."""

  @patch("praxis.backend.core.orchestrator.WorkcellRuntime")
  @patch("praxis.backend.core.orchestrator.AssetManager")
  @patch(
    "praxis.backend.core.orchestrator.get_protocol_definition_orm_by_name_and_version",
  )
  @patch("praxis.backend.core.orchestrator.update_protocol_run_status")
  async def test_execute_protocol_happy_path(
    self,
    mock_update_status: AsyncMock,
    mock_get_protocol_def: AsyncMock,
    mock_asset_manager_cls: MagicMock,
    mock_workcell_runtime_cls: MagicMock,
    orchestrator: Orchestrator,
    mock_db_session: AsyncMock,
    mock_protocol_definition: FunctionProtocolDefinitionModel,
  ):
    """Test a successful protocol execution from start to finish."""
    # Arrange
    mock_get_protocol_def.return_value = mock_protocol_definition
    mock_asset_manager = mock_asset_manager_cls.return_value
    mock_asset_manager.get_all_assets.return_value = {"test_asset": MagicMock()}
    mock_workcell_runtime = mock_workcell_runtime_cls.return_value
    mock_protocol_func = AsyncMock(return_value={"result": "success"})
    runtime_info = ProtocolRuntimeInfo(
      pydantic_definition=mock_protocol_definition,
      function_ref=mock_protocol_func,
      found_state_param_details=None,
    )
    runtime_info.callable_wrapper = mock_protocol_func
    PROTOCOL_REGISTRY[f"{TEST_PROTOCOL_NAME}_v{TEST_PROTOCOL_VERSION}"] = runtime_info

    # Act
    result = await orchestrator.execute_protocol(
      protocol_name=TEST_PROTOCOL_NAME,
      protocol_version=TEST_PROTOCOL_VERSION,
      input_parameters={},
    )

    # Assert
    assert result == {"result": "success"}
    mock_update_status.assert_has_calls(
      [
        call(mock_db_session, TEST_RUN_ID, ProtocolRunStatusEnum.RUNNING),
        call(mock_db_session, TEST_RUN_ID, ProtocolRunStatusEnum.COMPLETED, ANY),
      ],
    )
    mock_workcell_runtime_cls.assert_called_once()
    mock_asset_manager_cls.assert_called_once()
    mock_workcell_runtime.setup.assert_awaited_once()
    mock_workcell_runtime.teardown.assert_awaited_once()
    mock_protocol_func.assert_awaited_once()
    kwargs = mock_protocol_func.get("await_args", {"kwargs": {}}).get("kwargs", {})
    assert "test_asset" in kwargs

  @patch("praxis.backend.core.orchestrator.WorkcellRuntime")
  @patch("praxis.backend.core.orchestrator.AssetManager")
  @patch(
    "praxis.backend.core.orchestrator.get_protocol_definition_orm_by_name_and_version",
  )
  @patch("praxis.backend.core.orchestrator.update_protocol_run_status")
  async def test_execute_protocol_handles_exception(
    self,
    mock_update_status: AsyncMock,
    mock_get_protocol_def: AsyncMock,
    mock_asset_manager_cls: MagicMock,
    mock_workcell_runtime_cls: MagicMock,
    orchestrator: Orchestrator,
    mock_db_session: AsyncMock,
    mock_protocol_definition: FunctionProtocolDefinitionModel,
  ):
    """Test that protocol failures are handled and the status is set to FAILED."""
    # Arrange
    mock_get_protocol_def.return_value = mock_protocol_definition
    mock_workcell_runtime = mock_workcell_runtime_cls.return_value
    error = ValueError("Protocol failed!")
    mock_protocol_func = AsyncMock(side_effect=error)
    runtime_info = ProtocolRuntimeInfo(
      pydantic_definition=mock_protocol_definition,
      function_ref=mock_protocol_func,
      found_state_param_details=None,
    )
    runtime_info.callable_wrapper = mock_protocol_func
    PROTOCOL_REGISTRY[f"{TEST_PROTOCOL_NAME}_v{TEST_PROTOCOL_VERSION}"] = runtime_info

    # Act & Assert
    with pytest.raises(ValueError, match="Protocol failed!"):
      await orchestrator.execute_protocol(
        protocol_name=TEST_PROTOCOL_NAME,
        protocol_version=TEST_PROTOCOL_VERSION,
        input_parameters={},
      )

    mock_update_status.assert_has_calls(
      [
        call(mock_db_session, TEST_RUN_ID, ProtocolRunStatusEnum.RUNNING),
        call(mock_db_session, TEST_RUN_ID, ProtocolRunStatusEnum.FAILED, ANY),
      ],
    )
    mock_workcell_runtime.teardown.assert_awaited_once()

  @patch("praxis.backend.core.orchestrator.WorkcellRuntime")
  @patch("praxis.backend.core.orchestrator.AssetManager")
  @patch(
    "praxis.backend.core.orchestrator.get_protocol_definition_orm_by_name_and_version",
  )
  @patch("praxis.backend.core.orchestrator.update_protocol_run_status")
  async def test_execute_protocol_handles_cancellation(
    self,
    mock_update_status: AsyncMock,
    mock_get_protocol_def: AsyncMock,
    mock_asset_manager_cls: MagicMock,
    mock_workcell_runtime_cls: MagicMock,
    orchestrator: Orchestrator,
    mock_db_session: AsyncMock,
    mock_protocol_definition: FunctionProtocolDefinitionModel,
  ):
    """Test that ProtocolCancelledError is handled gracefully."""
    # Arrange
    mock_get_protocol_def.return_value = mock_protocol_definition
    mock_workcell_runtime = mock_workcell_runtime_cls.return_value
    error = ProtocolCancelledError("User cancelled")
    mock_protocol_func = AsyncMock(side_effect=error)
    runtime_info = ProtocolRuntimeInfo(
      pydantic_definition=mock_protocol_definition,
      function_ref=mock_protocol_func,
      found_state_param_details=None,
    )
    runtime_info.callable_wrapper = mock_protocol_func
    PROTOCOL_REGISTRY[f"{TEST_PROTOCOL_NAME}_v{TEST_PROTOCOL_VERSION}"] = runtime_info

    # Act
    await orchestrator.execute_protocol(
      protocol_name=TEST_PROTOCOL_NAME,
      protocol_version=TEST_PROTOCOL_VERSION,
      input_parameters={},
    )

    # Assert
    failed_call = call(mock_db_session, TEST_RUN_ID, ProtocolRunStatusEnum.FAILED, ANY)
    assert failed_call not in mock_update_status.call_args_list
    mock_workcell_runtime.teardown.assert_awaited_once()


@pytest.mark.asyncio
class TestOrchestratorScenarios:
  """Tests various edge cases and scenarios for the Orchestrator."""

  @patch(
    "praxis.backend.core.orchestrator.get_protocol_definition_orm_by_name_and_version",
  )
  async def test_execute_raises_error_if_protocol_not_found(
    self, mock_get_protocol_def: AsyncMock, orchestrator: Orchestrator,
  ):
    """Test that an error is raised if a protocol definition cannot be found."""
    # Arrange
    mock_get_protocol_def.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="Protocol definition not found"):
      await orchestrator.execute_protocol(
        protocol_name="non_existent_protocol",
        protocol_version="1.0.0",
        input_parameters={},
      )

  @patch("praxis.backend.core.orchestrator.AssetManager")
  @patch(
    "praxis.backend.core.orchestrator.get_protocol_definition_orm_by_name_and_version",
  )
  async def test_execute_raises_error_if_asset_is_missing(
    self,
    mock_get_protocol_def: AsyncMock,
    mock_asset_manager_cls: MagicMock,
    orchestrator: Orchestrator,
    mock_protocol_definition: FunctionProtocolDefinitionModel,
  ):
    """Test that a ValueError is raised if a required asset is not available."""
    # Arrange
    mock_get_protocol_def.return_value = mock_protocol_definition
    mock_asset_manager = mock_asset_manager_cls.return_value
    mock_asset_manager.get_all_assets.return_value = {"wrong_asset": MagicMock()}
    runtime_info = ProtocolRuntimeInfo(
      pydantic_definition=mock_protocol_definition,
      function_ref=AsyncMock(),
      found_state_param_details=None,
    )
    PROTOCOL_REGISTRY[f"{TEST_PROTOCOL_NAME}_v{TEST_PROTOCOL_VERSION}"] = runtime_info

    # Act & Assert
    with pytest.raises(
      ValueError, match="Could not find a required asset 'test_asset'",
    ):
      await orchestrator.execute_protocol(
        protocol_name=TEST_PROTOCOL_NAME,
        protocol_version=TEST_PROTOCOL_VERSION,
        input_parameters={},
      )

  @patch("praxis.backend.core.orchestrator.ProtocolCodeManager")
  @patch(
    "praxis.backend.core.orchestrator.get_protocol_definition_orm_by_name_and_version",
  )
  async def test_execute_loads_protocol_not_in_registry(
    self,
    mock_get_protocol_def: AsyncMock,
    mock_pcm_cls: MagicMock,
    orchestrator: Orchestrator,
    mock_protocol_definition: FunctionProtocolDefinitionModel,
  ):
    """Test that execute_protocol dynamically loads code if protocol not registered."""
    # Arrange
    mock_get_protocol_def.return_value = mock_protocol_definition
    mock_pcm = mock_pcm_cls.return_value
    mock_protocol_func = AsyncMock(side_effect=ProtocolCancelledError)
    runtime_info = ProtocolRuntimeInfo(
      pydantic_definition=mock_protocol_definition,
      function_ref=mock_protocol_func,
      found_state_param_details=None,
    )

    def loader_side_effect(*args, **kwargs):
      PROTOCOL_REGISTRY[f"{TEST_PROTOCOL_NAME}_v{TEST_PROTOCOL_VERSION}"] = runtime_info

    mock_pcm.load_protocol_code.side_effect = loader_side_effect

    # Act
    # We expect a ProtocolCancelledError to exit cleanly after loading
    await orchestrator.execute_protocol(
      protocol_name=TEST_PROTOCOL_NAME,
      protocol_version=TEST_PROTOCOL_VERSION,
      input_parameters={},
    )

    # Assert
    mock_pcm.load_protocol_code.assert_awaited_once_with(mock_protocol_definition)
