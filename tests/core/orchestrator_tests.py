# pylint: disable=redefined-outer-name, protected-access, unused-argument, invalid-name, too-many-locals
"""Unit tests for the Orchestrator."""

import uuid
from unittest.mock import ANY, AsyncMock, MagicMock, call, patch

import pytest

from praxis.backend.core.decorators import ProtocolRuntimeInfo
from praxis.backend.core.orchestrator import Orchestrator, ProtocolCancelledError
from praxis.backend.models import (
  AssetRequirementModel,
  FunctionProtocolDefinitionCreate,
  ProtocolRunStatusEnum,
)

# --- Test Constants ---
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


from praxis.backend.utils.uuid import uuid7


@pytest.fixture
def mock_protocol_definition() -> FunctionProtocolDefinitionCreate:
  """Provide a mock protocol definition model."""
  asset_req = AssetRequirementModel(
    accession_id=uuid7(),
    name="test_asset",
    fqn="pylabrobot.resources.resource.Resource",
    type_hint_str="pylabrobot.resources.resource.Resource",
  )
  return FunctionProtocolDefinitionCreate(
    accession_id=uuid7(),
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
  protocol_code_manager = MagicMock()
  return Orchestrator(
    db_session_factory=mock_db_session,
    asset_manager=asset_manager,
    workcell_runtime=workcell_runtime,
    protocol_code_manager=protocol_code_manager,
  )


# --- Test Classes ---


@pytest.mark.asyncio
class TestOrchestratorExecution:

  """Tests the main execution flows of the Orchestrator."""

  @patch("praxis.backend.services.protocols.protocol_run_service.create")
  @patch("praxis.backend.services.protocols.protocol_run_service.update")
  @patch("praxis.backend.services.protocol_definition.protocol_definition_service.get_by_name_and_version")
  async def test_execute_protocol_happy_path(
    self,
    mock_get_protocol_def: AsyncMock,
    mock_update_run: AsyncMock,
    mock_create_run: AsyncMock,
    orchestrator: Orchestrator,
    mock_protocol_definition: FunctionProtocolDefinitionCreate,
  ) -> None:
    """Test a successful protocol execution from start to finish."""
    # Arrange
    mock_get_protocol_def.return_value = mock_protocol_definition
    mock_asset_manager = orchestrator.asset_manager
    mock_asset_manager.acquire_asset.return_value = (MagicMock(), uuid.uuid4(), "resource")
    mock_workcell_runtime = orchestrator.workcell_runtime
    mock_protocol_func = AsyncMock(return_value={"result": "success"})
    runtime_info = ProtocolRuntimeInfo(
      pydantic_definition=mock_protocol_definition,
      function_ref=mock_protocol_func,
      found_state_param_details=None,
    )
    orchestrator.protocol_code_manager.prepare_protocol_code.return_value = (mock_protocol_func, runtime_info.pydantic_definition)

    # Act
    result = await orchestrator.execute_protocol(
      protocol_name=TEST_PROTOCOL_NAME,
      protocol_version=TEST_PROTOCOL_VERSION,
      input_parameters={},
    )

    # Assert
    assert result == {"result": "success"}
    mock_create_run.assert_awaited_once()
    assert mock_update_run.call_count == 2
    mock_workcell_runtime.setup.assert_awaited_once()
    mock_workcell_runtime.teardown.assert_awaited_once()
    mock_protocol_func.assert_awaited_once()
    kwargs = mock_protocol_func.await_args.kwargs
    assert "test_asset" in kwargs

  @patch("praxis.backend.services.protocols.protocol_run_service.create")
  @patch("praxis.backend.services.protocols.protocol_run_service.update")
  @patch("praxis.backend.services.protocol_definition.protocol_definition_service.get_by_name_and_version")
  async def test_execute_protocol_handles_exception(
    self,
    mock_get_protocol_def: AsyncMock,
    mock_update_run: AsyncMock,
    mock_create_run: AsyncMock,
    orchestrator: Orchestrator,
    mock_protocol_definition: FunctionProtocolDefinitionCreate,
  ) -> None:
    """Test that protocol failures are handled and the status is set to FAILED."""
    # Arrange
    mock_get_protocol_def.return_value = mock_protocol_definition
    mock_workcell_runtime = orchestrator.workcell_runtime
    error = ValueError("Protocol failed!")
    mock_protocol_func = AsyncMock(side_effect=error)
    runtime_info = ProtocolRuntimeInfo(
      pydantic_definition=mock_protocol_definition,
      function_ref=mock_protocol_func,
      found_state_param_details=None,
    )
    orchestrator.protocol_code_manager.prepare_protocol_code.return_value = (mock_protocol_func, runtime_info.pydantic_definition)


    # Act & Assert
    with pytest.raises(ValueError, match="Protocol failed!"):
      await orchestrator.execute_protocol(
        protocol_name=TEST_PROTOCOL_NAME,
        protocol_version=TEST_PROTOCOL_VERSION,
        input_parameters={},
      )

    assert mock_update_run.call_count == 2
    final_call = mock_update_run.call_args_list[-1]
    assert final_call.kwargs["obj_in"].status == ProtocolRunStatusEnum.FAILED
    mock_workcell_runtime.teardown.assert_awaited_once()

  @patch("praxis.backend.services.protocols.protocol_run_service.create")
  @patch("praxis.backend.services.protocols.protocol_run_service.update")
  @patch("praxis.backend.services.protocol_definition.protocol_definition_service.get_by_name_and_version")
  async def test_execute_protocol_handles_cancellation(
    self,
    mock_get_protocol_def: AsyncMock,
    mock_update_run: AsyncMock,
    mock_create_run: AsyncMock,
    orchestrator: Orchestrator,
    mock_protocol_definition: FunctionProtocolDefinitionCreate,
  ) -> None:
    """Test that ProtocolCancelledError is handled gracefully."""
    # Arrange
    mock_get_protocol_def.return_value = mock_protocol_definition
    mock_workcell_runtime = orchestrator.workcell_runtime
    error = ProtocolCancelledError("User cancelled")
    mock_protocol_func = AsyncMock(side_effect=error)
    runtime_info = ProtocolRuntimeInfo(
      pydantic_definition=mock_protocol_definition,
      function_ref=mock_protocol_func,
      found_state_param_details=None,
    )
    orchestrator.protocol_code_manager.prepare_protocol_code.return_value = (mock_protocol_func, runtime_info.pydantic_definition)

    # Act
    await orchestrator.execute_protocol(
      protocol_name=TEST_PROTOCOL_NAME,
      protocol_version=TEST_PROTOCOL_VERSION,
      input_parameters={},
    )

    # Assert
    final_call = mock_update_run.call_args_list[-1]
    assert final_call.kwargs["obj_in"].status != ProtocolRunStatusEnum.FAILED
    mock_workcell_runtime.teardown.assert_awaited_once()

@pytest.mark.asyncio
class TestOrchestratorScenarios:

  """Tests various edge cases and scenarios for the Orchestrator."""

  @patch("praxis.backend.services.protocol_definition.protocol_definition_service.get_by_name_and_version")
  async def test_execute_raises_error_if_protocol_not_found(
    self, mock_get_protocol_def: AsyncMock, orchestrator: Orchestrator,
  ) -> None:
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

  @patch("praxis.backend.services.protocol_definition.protocol_definition_service.get_by_name_and_version")
  async def test_execute_raises_error_if_asset_is_missing(
    self,
    mock_get_protocol_def: AsyncMock,
    orchestrator: Orchestrator,
    mock_protocol_definition: FunctionProtocolDefinitionCreate,
  ) -> None:
    """Test that a ValueError is raised if a required asset is not available."""
    # Arrange
    mock_get_protocol_def.return_value = mock_protocol_definition
    orchestrator.asset_manager.acquire_asset.side_effect = ValueError("Asset not found")

    # Act & Assert
    with pytest.raises(
      ValueError, match="Asset not found",
    ):
      await orchestrator.execute_protocol(
        protocol_name=TEST_PROTOCOL_NAME,
        protocol_version=TEST_PROTOCOL_VERSION,
        input_parameters={},
      )
