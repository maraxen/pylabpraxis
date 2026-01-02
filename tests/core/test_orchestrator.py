"""Tests for core/orchestrator.py."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.models import ProtocolRunStatusEnum
from praxis.backend.models.orm.protocol import ProtocolRunOrm
from praxis.backend.services.state import PraxisState
from praxis.backend.utils.errors import AssetAcquisitionError, ProtocolCancelledError
from praxis.backend.utils.uuid import uuid7


class TestOrchestratorInit:

    """Tests for Orchestrator initialization."""

    def test_orchestrator_initialization(self) -> None:
        """Test Orchestrator initialization."""
        mock_db_session_factory = Mock()
        mock_asset_manager = Mock()
        mock_workcell_runtime = Mock()
        mock_protocol_code_manager = Mock()

        orchestrator = Orchestrator(
            db_session_factory=mock_db_session_factory,
            asset_manager=mock_asset_manager,
            workcell_runtime=mock_workcell_runtime,
            protocol_code_manager=mock_protocol_code_manager,
        )

        assert orchestrator.db_session_factory == mock_db_session_factory
        assert orchestrator.asset_manager == mock_asset_manager
        assert orchestrator.workcell_runtime == mock_workcell_runtime
        assert orchestrator.protocol_code_manager == mock_protocol_code_manager

    def test_orchestrator_initialization_without_code_manager(self) -> None:
        """Test Orchestrator creates code manager when not provided."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=None,
        )

        assert orchestrator.protocol_code_manager is not None


class TestProcessInputParameters:

    """Tests for _process_input_parameters method."""

    def test_process_input_parameters_with_all_params(self) -> None:
        """Test processing when all parameters are provided."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_param = Mock()
        mock_param.name = "volume"
        mock_param.is_deck_param = False
        mock_param.optional = False

        mock_protocol_def = Mock()
        mock_protocol_def.parameters = [mock_param]
        mock_protocol_def.state_param_name = "state"

        input_parameters = {"volume": 100}
        final_args = {}

        orchestrator._process_input_parameters(
            mock_protocol_def,
            input_parameters,
            final_args,
        )

        assert final_args["volume"] == 100

    def test_process_input_parameters_missing_mandatory_param(self) -> None:
        """Test error when mandatory parameter is missing."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_param = Mock()
        mock_param.name = "volume"
        mock_param.is_deck_param = False
        mock_param.optional = False

        mock_protocol_def = Mock()
        mock_protocol_def.parameters = [mock_param]
        mock_protocol_def.state_param_name = "state"
        mock_protocol_def.name = "test_protocol"

        input_parameters = {}
        final_args = {}

        with pytest.raises(ValueError, match="Mandatory parameter"):
            orchestrator._process_input_parameters(
                mock_protocol_def,
                input_parameters,
                final_args,
            )

    def test_process_input_parameters_optional_param_not_provided(self) -> None:
        """Test optional parameter not provided is handled."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_param = Mock()
        mock_param.name = "volume"
        mock_param.is_deck_param = False
        mock_param.optional = True

        mock_protocol_def = Mock()
        mock_protocol_def.parameters = [mock_param]
        mock_protocol_def.state_param_name = "state"

        input_parameters = {}
        final_args = {}

        orchestrator._process_input_parameters(
            mock_protocol_def,
            input_parameters,
            final_args,
        )

        # Optional param not in input, so not added to final_args
        assert "volume" not in final_args

    def test_process_input_parameters_skips_deck_param(self) -> None:
        """Test that deck parameters are skipped."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_param = Mock()
        mock_param.name = "deck"
        mock_param.is_deck_param = True
        mock_param.optional = False

        mock_protocol_def = Mock()
        mock_protocol_def.parameters = [mock_param]
        mock_protocol_def.state_param_name = "state"

        input_parameters = {"deck": "some_deck"}
        final_args = {}

        orchestrator._process_input_parameters(
            mock_protocol_def,
            input_parameters,
            final_args,
        )

        # Deck param should be skipped
        assert "deck" not in final_args


class TestInjectPraxisState:

    """Tests for _inject_praxis_state method."""

    def test_inject_praxis_state_as_object(self) -> None:
        """Test injecting PraxisState as object."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_param = Mock()
        mock_param.name = "state"
        mock_param.actual_type_str = "PraxisState"

        mock_protocol_def = Mock()
        mock_protocol_def.parameters = [mock_param]
        mock_protocol_def.state_param_name = "state"

        # Use mock instead of real PraxisState to avoid Redis
        praxis_state = Mock(spec=PraxisState)
        final_args = {}

        orchestrator._inject_praxis_state(
            mock_protocol_def,
            praxis_state,
            final_args,
        )

        assert final_args["state"] == praxis_state

    def test_inject_praxis_state_as_dict(self) -> None:
        """Test injecting PraxisState as dictionary."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_param = Mock()
        mock_param.name = "state"
        mock_param.actual_type_str = "dict[str, Any]"

        mock_protocol_def = Mock()
        mock_protocol_def.parameters = [mock_param]
        mock_protocol_def.state_param_name = "state"

        # Use mock instead of real PraxisState to avoid Redis
        praxis_state = Mock(spec=PraxisState)
        praxis_state.to_dict.return_value = {"key": "value"}
        final_args = {}

        result = orchestrator._inject_praxis_state(
            mock_protocol_def,
            praxis_state,
            final_args,
        )

        assert isinstance(final_args["state"], dict)
        assert result is not None
        assert isinstance(result, dict)

    def test_inject_praxis_state_no_state_param(self) -> None:
        """Test when no state parameter is defined."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_protocol_def = Mock()
        mock_protocol_def.parameters = []
        mock_protocol_def.state_param_name = None

        # Use mock instead of real PraxisState to avoid Redis
        praxis_state = Mock(spec=PraxisState)
        final_args = {}

        result = orchestrator._inject_praxis_state(
            mock_protocol_def,
            praxis_state,
            final_args,
        )

        assert result is None
        assert len(final_args) == 0


class TestAcquireAssets:

    """Tests for _acquire_assets method."""

    @pytest.mark.asyncio
    async def test_acquire_assets_success(self) -> None:
        """Test successful asset acquisition."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_asset_req = Mock()
        mock_asset_req.name = "test_asset"
        mock_asset_req.fqn = "test.Asset"
        mock_asset_req.optional = False

        mock_protocol_def = Mock()
        mock_protocol_def.assets = [mock_asset_req]

        run_id = uuid7()
        asset_id = uuid7()

        mock_live_obj = Mock()
        orchestrator.asset_manager.acquire_asset = AsyncMock(
            return_value=(mock_live_obj, asset_id, "resource"),
        )

        final_args = {}
        acquired_assets_details = {}

        await orchestrator._acquire_assets(
            mock_protocol_def,
            run_id,
            final_args,
            acquired_assets_details,
        )

        assert final_args["test_asset"] == mock_live_obj
        assert asset_id in acquired_assets_details
        assert acquired_assets_details[asset_id]["name_in_protocol"] == "test_asset"

    @pytest.mark.asyncio
    async def test_acquire_assets_optional_asset_fails(self) -> None:
        """Test optional asset failure is handled gracefully."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_asset_req = Mock()
        mock_asset_req.name = "optional_asset"
        mock_asset_req.fqn = "test.Asset"
        mock_asset_req.optional = True

        mock_protocol_def = Mock()
        mock_protocol_def.assets = [mock_asset_req]
        mock_protocol_def.name = "test_protocol"

        run_id = uuid7()

        orchestrator.asset_manager.acquire_asset = AsyncMock(
            side_effect=AssetAcquisitionError("Asset not available"),
        )

        final_args = {}
        acquired_assets_details = {}

        await orchestrator._acquire_assets(
            mock_protocol_def,
            run_id,
            final_args,
            acquired_assets_details,
        )

        # Optional asset should be set to None
        assert final_args["optional_asset"] is None

    @pytest.mark.asyncio
    async def test_acquire_assets_mandatory_asset_fails(self) -> None:
        """Test mandatory asset failure raises error."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_asset_req = Mock()
        mock_asset_req.name = "mandatory_asset"
        mock_asset_req.fqn = "test.Asset"
        mock_asset_req.optional = False

        mock_protocol_def = Mock()
        mock_protocol_def.assets = [mock_asset_req]
        mock_protocol_def.name = "test_protocol"

        run_id = uuid7()

        orchestrator.asset_manager.acquire_asset = AsyncMock(
            side_effect=AssetAcquisitionError("Asset not available"),
        )

        final_args = {}
        acquired_assets_details = {}

        with pytest.raises(ValueError, match="Failed to acquire mandatory asset"):
            await orchestrator._acquire_assets(
                mock_protocol_def,
                run_id,
                final_args,
                acquired_assets_details,
            )


class TestHandlePreExecutionChecks:

    """Tests for _handle_pre_execution_checks method."""

    @pytest.mark.asyncio
    async def test_handle_pre_execution_checks_no_command(self) -> None:
        """Test when no control command is present."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_protocol_run = Mock()
        mock_protocol_run.run_accession_id = uuid7()
        mock_protocol_run.accession_id = uuid7()

        mock_db_session = AsyncMock()

        with patch("praxis.backend.core.orchestrator.execution.get_control_command", return_value=None):
            # Should complete without error
            await orchestrator._handle_pre_execution_checks(
                mock_protocol_run,
                mock_db_session,
            )

    @pytest.mark.asyncio
    async def test_handle_pre_execution_checks_cancel_directly(self) -> None:
        """Test when CANCEL command is present before execution."""
        # Create orchestrator with mocked protocol_run_service
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        mock_protocol_run = Mock()
        run_id = uuid7()
        mock_protocol_run.run_accession_id = run_id
        mock_protocol_run.accession_id = run_id

        mock_db_session = AsyncMock()

        with patch("praxis.backend.core.orchestrator.execution.get_control_command", AsyncMock(return_value="CANCEL")):
            with patch("praxis.backend.core.orchestrator.execution.clear_control_command", AsyncMock()) as mock_clear:
                with pytest.raises(ProtocolCancelledError, match="cancelled by user before execution"):
                    await orchestrator._handle_pre_execution_checks(
                        mock_protocol_run,
                        mock_db_session,
                    )

                # Verify control command was cleared
                mock_clear.assert_called_once_with(run_id)

                # Verify status was updated to CANCELLED
                orchestrator.protocol_run_service.update_run_status.assert_called_once()
                call_args = orchestrator.protocol_run_service.update_run_status.call_args
                assert call_args[0][1] == run_id  # protocol_run_id
                assert call_args[0][2] == ProtocolRunStatusEnum.CANCELLED  # status

                # Verify db commit was called
                mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_pre_execution_checks_pause_then_resume(self) -> None:
        """Test PAUSE → RESUME flow."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        mock_protocol_run = Mock()
        run_id = uuid7()
        mock_protocol_run.run_accession_id = run_id
        mock_protocol_run.accession_id = run_id

        mock_db_session = AsyncMock()

        # Mock control commands: PAUSE first, then RESUME after one loop iteration
        with patch("praxis.backend.core.orchestrator.execution.get_control_command", AsyncMock()) as mock_get_cmd:
            with patch("praxis.backend.core.orchestrator.execution.clear_control_command", AsyncMock()) as mock_clear:
                with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
                    # First call returns PAUSE, second call in loop returns RESUME
                    mock_get_cmd.side_effect = ["PAUSE", "RESUME"]

                    # Should complete without error
                    await orchestrator._handle_pre_execution_checks(
                        mock_protocol_run,
                        mock_db_session,
                    )

                    # Verify control commands were called
                    assert mock_get_cmd.call_count == 2  # Initial check + loop check
                    assert mock_clear.call_count == 2  # Clear after PAUSE and RESUME

                    # Verify sleep was called (pause loop)
                    mock_sleep.assert_called_once_with(1)

                    # Verify status transitions: PAUSED → RUNNING
                    assert orchestrator.protocol_run_service.update_run_status.call_count == 2

                    # First call: PAUSED
                    first_call = orchestrator.protocol_run_service.update_run_status.call_args_list[0]
                    assert first_call[0][2] == ProtocolRunStatusEnum.PAUSED

                    # Second call: RUNNING
                    second_call = orchestrator.protocol_run_service.update_run_status.call_args_list[1]
                    assert second_call[0][2] == ProtocolRunStatusEnum.RUNNING

                    # Verify commits
                    assert mock_db_session.commit.call_count == 2

    @pytest.mark.asyncio
    async def test_handle_pre_execution_checks_pause_then_cancel(self) -> None:
        """Test PAUSE → CANCEL flow."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        mock_protocol_run = Mock()
        run_id = uuid7()
        mock_protocol_run.run_accession_id = run_id
        mock_protocol_run.accession_id = run_id

        mock_db_session = AsyncMock()

        with patch("praxis.backend.core.orchestrator.execution.get_control_command", AsyncMock()) as mock_get_cmd:
            with patch("praxis.backend.core.orchestrator.execution.clear_control_command", AsyncMock()) as mock_clear:
                with patch("asyncio.sleep", AsyncMock()):
                    # First call returns PAUSE, second call in loop returns CANCEL
                    mock_get_cmd.side_effect = ["PAUSE", "CANCEL"]

                    with pytest.raises(ProtocolCancelledError, match="cancelled by user during pause"):
                        await orchestrator._handle_pre_execution_checks(
                            mock_protocol_run,
                            mock_db_session,
                        )

                    # Verify control commands cleared twice
                    assert mock_clear.call_count == 2

                    # Verify status transitions: PAUSED → CANCELLED
                    assert orchestrator.protocol_run_service.update_run_status.call_count == 2

                    # First call: PAUSED
                    first_call = orchestrator.protocol_run_service.update_run_status.call_args_list[0]
                    assert first_call[0][2] == ProtocolRunStatusEnum.PAUSED

                    # Second call: CANCELLED with output JSON
                    second_call = orchestrator.protocol_run_service.update_run_status.call_args_list[1]
                    assert second_call[0][2] == ProtocolRunStatusEnum.CANCELLED
                    assert "output_data_json" in second_call[1]

    @pytest.mark.asyncio
    async def test_handle_pre_execution_checks_pause_loop_multiple_iterations(self) -> None:
        """Test pause loop with multiple sleep cycles before RESUME."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        mock_protocol_run = Mock()
        run_id = uuid7()
        mock_protocol_run.run_accession_id = run_id
        mock_protocol_run.accession_id = run_id

        mock_db_session = AsyncMock()

        with patch("praxis.backend.core.orchestrator.execution.get_control_command", AsyncMock()) as mock_get_cmd:
            with patch("praxis.backend.core.orchestrator.execution.clear_control_command", AsyncMock()):
                with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
                    # PAUSE, then None 3 times, then RESUME
                    mock_get_cmd.side_effect = ["PAUSE", None, None, None, "RESUME"]

                    await orchestrator._handle_pre_execution_checks(
                        mock_protocol_run,
                        mock_db_session,
                    )

                    # Verify sleep was called 4 times (once per None + once for RESUME check)
                    assert mock_sleep.call_count == 4

                    # Verify get_command was called 5 times
                    assert mock_get_cmd.call_count == 5

    @pytest.mark.asyncio
    async def test_handle_pre_execution_checks_no_service(self) -> None:
        """Test graceful handling when protocol_run_service is None."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )
        # No protocol_run_service set (remains None)

        mock_protocol_run = Mock()
        run_id = uuid7()
        mock_protocol_run.run_accession_id = run_id
        mock_protocol_run.accession_id = run_id

        mock_db_session = AsyncMock()

        with patch("praxis.backend.core.orchestrator.execution.get_control_command", AsyncMock(return_value="CANCEL")):
            with patch("praxis.backend.core.orchestrator.execution.clear_control_command", AsyncMock()):
                # Should raise ProtocolCancelledError without calling service
                with pytest.raises(ProtocolCancelledError):
                    await orchestrator._handle_pre_execution_checks(
                        mock_protocol_run,
                        mock_db_session,
                    )

                # Verify db commit was still called
                mock_db_session.commit.assert_called_once()


class TestInitializeRunContext:

    """Tests for _initialize_run_context method."""

    @pytest.mark.asyncio
    async def test_initialize_run_context(self) -> None:
        """Test run context initialization."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        run_id = uuid7()
        mock_protocol_run = Mock()
        # FIX: Ensure accession_id is set correctly for both old and new code paths usage
        mock_protocol_run.accession_id = run_id
        mock_protocol_run.run_accession_id = run_id

        mock_db_session = AsyncMock()

        initial_state_data = {"key": "value"}

        orchestrator.workcell_runtime.get_state_snapshot = Mock(return_value={"snapshot": "data"})

        # Mock PraxisState to avoid Redis
        with patch("praxis.backend.core.orchestrator.protocol_preparation.PraxisState") as mock_state_class:
            mock_state = Mock()
            mock_state.update = Mock()
            # FIX: set must be async
            mock_state.set = AsyncMock()
            mock_state_class.return_value = mock_state

            run_context = await orchestrator._initialize_run_context(
                mock_protocol_run,
                initial_state_data,
                mock_db_session,
            )

            assert run_context.run_accession_id == run_id
            assert run_context.canonical_state == mock_state
            assert run_context.current_db_session == mock_db_session


class TestGetProtocolDefinitionOrmFromDb:

    """Tests for _get_protocol_definition_orm_from_db method."""

    @pytest.mark.skip(reason="Complex service integration - svc.read_protocol_definition_by_name not directly patchable")
    @pytest.mark.asyncio
    async def test_get_protocol_definition_orm_from_db(self) -> None:
        """Test fetching protocol definition from database."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_protocol_def = Mock()
        mock_db_session = AsyncMock()

        with patch(
            "praxis.backend.core.orchestrator.protocol_preparation.svc.read_protocol_definition_by_name",
            AsyncMock(return_value=mock_protocol_def),
        ):
            result = await orchestrator._get_protocol_definition_orm_from_db(
                mock_db_session,
                "test_protocol",
            )

        assert result == mock_protocol_def


class TestPrepareProtocolCode:

    """Tests for _prepare_protocol_code method."""

    @pytest.mark.asyncio
    async def test_prepare_protocol_code(self) -> None:
        """Test protocol code preparation."""
        mock_protocol_code_manager = Mock()
        mock_protocol_code_manager.prepare_protocol_code = AsyncMock(
            return_value=(Mock(), Mock()),
        )

        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=mock_protocol_code_manager,
        )

        mock_protocol_def_orm = Mock()

        func, pydantic_def = await orchestrator._prepare_protocol_code(mock_protocol_def_orm)

        assert func is not None
        assert pydantic_def is not None
        mock_protocol_code_manager.prepare_protocol_code.assert_called_once_with(
            mock_protocol_def_orm,
        )


class TestHandleProtocolExecutionError:

    """Tests for _handle_protocol_execution_error method."""

    @pytest.mark.skip(reason="Complex service integration - svc.update_protocol_run_status not directly patchable")
    @pytest.mark.asyncio
    async def test_handle_protocol_execution_error(self) -> None:
        """Test error handling during protocol execution."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        run_id = uuid7()

        # Mock PraxisState to avoid Redis
        praxis_state = Mock(spec=PraxisState)
        praxis_state.get.return_value = {"snapshot": "data"}

        mock_db_session = AsyncMock()

        orchestrator.workcell_runtime.apply_state_snapshot = Mock()
        orchestrator._validate_praxis_state = Mock()

        test_error = ValueError("Test error")

        await orchestrator._handle_protocol_execution_error(
            run_id,
            "test_protocol",
            test_error,
            praxis_state,
            mock_db_session,
        )

        # Should have attempted rollback
        orchestrator.workcell_runtime.apply_state_snapshot.assert_called_once()


class TestModuleStructure:

    """Tests for module structure and exports."""

    def test_module_has_orchestrator_class(self) -> None:
        """Test that module exports Orchestrator."""
        from praxis.backend.core import orchestrator

        assert hasattr(orchestrator, "Orchestrator")

    def test_module_has_logger(self) -> None:
        """Test that module defines logger."""
        from praxis.backend.core import orchestrator

        assert hasattr(orchestrator, "logger")


class TestOrchestratorExecutionFlow:
    """Integration-like tests for Orchestrator execution flow."""

    @pytest.mark.asyncio
    async def test_full_protocol_lifecycle(self) -> None:
        """Test a full protocol lifecycle: Initialize -> Prepare -> Run -> Complete."""
        # 1. Setup Mocks
        mock_db_session = AsyncMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.rollback = AsyncMock()

        mock_db_session_factory = Mock()
        # Configure return value to be an async context manager yielding the session
        mock_db_session_factory.return_value.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_asset_manager = Mock()
        mock_workcell_runtime = Mock()
        mock_workcell_runtime.get_main_workcell.return_value = Mock()
        mock_protocol_code_manager = Mock()

        # Create mock services (added after refactoring)
        mock_protocol_run_service = Mock()
        mock_protocol_definition_service = Mock()

        orchestrator = Orchestrator(
            db_session_factory=mock_db_session_factory,
            asset_manager=mock_asset_manager,
            workcell_runtime=mock_workcell_runtime,
            protocol_code_manager=mock_protocol_code_manager,
            protocol_run_service=mock_protocol_run_service,
            protocol_definition_service=mock_protocol_definition_service,
        )

        # 2. Mock Protocol Definition
        mock_lh = AsyncMock()
        mock_lh.aspirate = AsyncMock(return_value="aspirated")

        async def dummy_protocol(liquid_handler, **kwargs):
            await liquid_handler.aspirate()
            return {"result": "success"}

        # Protocol Def ORM
        mock_protocol_def_orm = Mock()
        mock_protocol_def_orm.name = "test_protocol"
        mock_protocol_def_orm.accession_id = uuid7()
        mock_protocol_def_orm.version = "1.0.0"

        # Protocol Pydantic Def
        mock_pydantic_def = Mock()
        mock_pydantic_def.name = "test_protocol"
        mock_pydantic_def.parameters = []
        mock_pydantic_def.assets = []
        mock_pydantic_def.state_param_name = None
        mock_pydantic_def.preconfigure_deck = False
        mock_pydantic_def.deck_construction_function_fqn = None
        mock_pydantic_def.deck_param_name = None

        # Add an asset requirement for liquid_handler
        mock_asset_req = Mock()
        mock_asset_req.name = "liquid_handler"
        mock_asset_req.optional = False
        mock_pydantic_def.assets = [mock_asset_req]

        # Mock Protocol Code Manager
        # Important: must be AsyncMock as it is awaited
        mock_protocol_code_manager.prepare_protocol_code = AsyncMock(
            return_value=(dummy_protocol, mock_pydantic_def)
        )

        # Mock Asset Acquisition
        mock_asset_manager.acquire_asset = AsyncMock(return_value=(mock_lh, uuid7(), "liquid_handler"))

        # Mock Service calls
        mock_run_orm = Mock()
        mock_run_orm.accession_id = uuid7()
        mock_run_orm.status = ProtocolRunStatusEnum.PREPARING

        # We need to simulate the state updates for status assertions
        run_status = ProtocolRunStatusEnum.PREPARING

        # Setup service mocks (updated after refactoring - services are now instance attributes)
        mock_protocol_definition_service.get_by_name = AsyncMock(return_value=mock_protocol_def_orm)
        mock_protocol_run_service.create = AsyncMock(return_value=mock_run_orm)

        # Mock run status updates
        async def side_effect_update(db, protocol_run_accession_id, new_status, **kwargs):
            nonlocal run_status
            run_status = new_status
            mock_run_orm.status = new_status
            return mock_run_orm

        mock_protocol_run_service.update_run_status = AsyncMock(side_effect=side_effect_update)

        with patch("praxis.backend.core.orchestrator.execution.get_control_command", AsyncMock(return_value=None)):
            with patch("praxis.backend.core.orchestrator.protocol_preparation.PraxisState") as mock_praxis_state_cls:
                # Setup PraxisState mock instance
                mock_state_instance = mock_praxis_state_cls.return_value
                mock_state_instance.set = AsyncMock()
                mock_state_instance.update = Mock()

                # 3. Execute Protocol
                await orchestrator.execute_protocol(
                    protocol_name="test_protocol",
                    input_parameters={},
                )

                # 4. Verification

                # Verify Protocol Code Preparation
                mock_protocol_code_manager.prepare_protocol_code.assert_called_once()

                # Verify Asset Acquisition
                mock_asset_manager.acquire_asset.assert_called()

                # Verify "Hardware" Execution
                mock_lh.aspirate.assert_awaited_once()

                # Verify Status Transitions
                assert run_status == ProtocolRunStatusEnum.COMPLETED

                # Verify DB commit was called
                assert mock_db_session.commit.called


# ==============================================================================
# Phase 2: Main Execution Flow Tests
# ==============================================================================


class TestExecuteProtocolMainLogic:

    """Tests for _execute_protocol_main_logic method."""

    @pytest.mark.asyncio
    async def test_execute_protocol_main_logic_success(self) -> None:
        """Test successful execution of main protocol logic."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )

        # Setup mocks
        mock_protocol_run = Mock()
        run_id = uuid7()
        mock_protocol_run.accession_id = run_id
        mock_protocol_run.resolved_assets_json = {}

        mock_protocol_def = Mock()
        mock_protocol_def.accession_id = uuid7()
        mock_protocol_def.name = "test_protocol"

        mock_db_session = AsyncMock()
        mock_praxis_state = Mock(spec=PraxisState)
        mock_run_context = Mock()

        # Mock protocol code preparation
        async def mock_protocol_func(**kwargs):
            return {"result": "success", "data": 42}

        mock_pydantic_def = Mock()
        mock_pydantic_def.name = "test_protocol"
        mock_pydantic_def.deck_construction_function_fqn = None

        orchestrator._prepare_protocol_code = AsyncMock(
            return_value=(mock_protocol_func, mock_pydantic_def)
        )

        # Mock workcell
        mock_workcell = Mock()
        orchestrator.workcell_runtime.get_main_workcell = Mock(return_value=mock_workcell)

        # Mock argument preparation with acquired assets
        asset_id = uuid7()
        acquired_assets_info = {asset_id: {"name_in_protocol": "liquid_handler", "type": "machine"}}
        orchestrator._prepare_arguments = AsyncMock(
            return_value=({"param1": "value1"}, None, acquired_assets_info)
        )

        # Execute
        result, returned_assets = await orchestrator._execute_protocol_main_logic(
            mock_protocol_run,
            mock_protocol_def,
            {"input": "data"},
            mock_praxis_state,
            mock_run_context,
            mock_db_session,
        )

        # Verify
        assert result == {"result": "success", "data": 42}
        assert returned_assets == acquired_assets_info
        assert mock_protocol_run.resolved_assets_json == acquired_assets_info
        mock_db_session.merge.assert_called_once_with(mock_protocol_run)
        mock_db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_protocol_main_logic_no_workcell(self) -> None:
        """Test error when main workcell is not available."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )

        # Setup mocks
        mock_protocol_run = Mock()
        mock_protocol_run.accession_id = uuid7()

        mock_protocol_def = Mock()
        mock_protocol_def.accession_id = uuid7()

        # Mock protocol code preparation
        mock_pydantic_def = Mock()
        orchestrator._prepare_protocol_code = AsyncMock(
            return_value=(Mock(), mock_pydantic_def)
        )

        # Mock no workcell available
        orchestrator.workcell_runtime.get_main_workcell = Mock(return_value=None)

        # Execute and verify error
        with pytest.raises(RuntimeError, match="Main Workcell container not available"):
            await orchestrator._execute_protocol_main_logic(
                mock_protocol_run,
                mock_protocol_def,
                {},
                Mock(),
                Mock(),
                AsyncMock(),
            )

    @pytest.mark.asyncio
    async def test_execute_protocol_with_deck_construction(self) -> None:
        """Test protocol execution with deck construction function."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )

        # Setup mocks
        mock_protocol_run = Mock()
        run_id = uuid7()
        mock_protocol_run.accession_id = run_id
        mock_protocol_run.resolved_assets_json = {}

        mock_protocol_def = Mock()
        mock_protocol_def.accession_id = uuid7()

        mock_db_session = AsyncMock()

        # Mock deck construction function
        deck_construction_called = []

        async def mock_deck_construction(liquid_handler):
            deck_construction_called.append(True)

        # Mock protocol function
        protocol_called = []

        async def mock_protocol_func(**kwargs):
            protocol_called.append(True)
            return {"result": "success"}

        mock_pydantic_def = Mock()
        mock_pydantic_def.name = "test_protocol"
        mock_pydantic_def.deck_construction_function_fqn = "module.deck_func"

        orchestrator._prepare_protocol_code = AsyncMock(
            return_value=(mock_protocol_func, mock_pydantic_def)
        )

        # Mock deck construction loading
        orchestrator.protocol_code_manager._load_callable_from_fqn = Mock(
            return_value=mock_deck_construction
        )

        # Mock workcell and arguments
        mock_workcell = Mock()
        orchestrator.workcell_runtime.get_main_workcell = Mock(return_value=mock_workcell)

        mock_lh = Mock()
        prepared_args = {"liquid_handler": mock_lh, "other_param": "value"}
        orchestrator._prepare_arguments = AsyncMock(
            return_value=(prepared_args, None, {})
        )

        # Execute
        await orchestrator._execute_protocol_main_logic(
            mock_protocol_run,
            mock_protocol_def,
            {},
            Mock(),
            Mock(),
            mock_db_session,
        )

        # Verify deck construction was called before protocol
        assert len(deck_construction_called) == 1
        assert len(protocol_called) == 1

        # Verify deck construction func was loaded
        orchestrator.protocol_code_manager._load_callable_from_fqn.assert_called_once_with(
            "module.deck_func"
        )


class TestExecuteProtocol:

    """Tests for execute_protocol method."""

    @pytest.mark.asyncio
    async def test_execute_protocol_not_found(self) -> None:
        """Test error when protocol definition is not found."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        # __aexit__ must return None (not truthy) to not suppress exceptions
        mock_db_session.__aexit__ = AsyncMock(return_value=None)

        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Mock protocol not found
        orchestrator._get_protocol_definition_orm_from_db = AsyncMock(return_value=None)

        # Execute and verify error
        with pytest.raises(ValueError, match="Protocol 'nonexistent_protocol'.*not found"):
            await orchestrator.execute_protocol(
                protocol_name="nonexistent_protocol",
            )

    @pytest.mark.asyncio
    async def test_execute_protocol_invalid_accession_id(self) -> None:
        """Test error when protocol definition has no accession_id."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        # __aexit__ must return None (not truthy) to not suppress exceptions
        mock_db_session.__aexit__ = AsyncMock(return_value=None)

        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Mock protocol with no accession_id
        mock_protocol = Mock()
        mock_protocol.accession_id = None
        orchestrator._get_protocol_definition_orm_from_db = AsyncMock(return_value=mock_protocol)

        # Execute and verify error
        with pytest.raises(ValueError, match="not found or invalid DB ID"):
            await orchestrator.execute_protocol(
                protocol_name="test_protocol",
            )


# ==============================================================================
# Phase 3: Error Handling & Recovery Tests
# ==============================================================================


class TestExecuteProtocolErrors:

    """Tests for error handling in execute_protocol method."""

    @pytest.mark.asyncio
    async def test_execute_protocol_cancelled_error_handling(self) -> None:
        """Test that ProtocolCancelledError during main logic is handled gracefully."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.create = AsyncMock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock(return_value=None)
        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Mock protocol definition
        mock_protocol_def = Mock()
        mock_protocol_def.accession_id = uuid7()
        mock_protocol_def.name = "test_protocol"
        orchestrator._get_protocol_definition_orm_from_db = AsyncMock(
            return_value=mock_protocol_def
        )

        # Mock protocol run creation
        mock_run = Mock()
        mock_run.accession_id = uuid7()
        mock_run.status = ProtocolRunStatusEnum.PREPARING
        orchestrator.protocol_run_service.create.return_value = mock_run

        # Mock run context initialization
        mock_run_context = Mock()
        mock_run_context.canonical_state = Mock()
        orchestrator._initialize_run_context = AsyncMock(return_value=mock_run_context)

        # Mock pre-execution checks - no errors here
        orchestrator._handle_pre_execution_checks = AsyncMock()

        # Mock main logic - raise ProtocolCancelledError here (inside try/except)
        orchestrator._execute_protocol_main_logic = AsyncMock(
            side_effect=ProtocolCancelledError("Cancelled during execution")
        )

        # Mock finalization
        orchestrator._finalize_protocol_run = AsyncMock()

        # Execute - should not raise, error should be handled
        await orchestrator.execute_protocol(
            protocol_name="test_protocol",
        )

        # Verify finalization was called despite cancellation
        orchestrator._finalize_protocol_run.assert_called_once()

        # Verify the exception handler passed (status not updated after cancellation)
        # The update_run_status should be called to set RUNNING, but NOT COMPLETED
        assert any(
            call[0][2] == ProtocolRunStatusEnum.RUNNING
            for call in orchestrator.protocol_run_service.update_run_status.call_args_list
        ), "Should update to RUNNING before main logic"

        # Verify db commit was attempted in finally block
        mock_db_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_execute_protocol_generic_exception(self) -> None:
        """Test generic exception handling during protocol execution."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.create = AsyncMock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock()
        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Mock protocol definition
        mock_protocol_def = Mock()
        mock_protocol_def.accession_id = uuid7()
        mock_protocol_def.name = "test_protocol"
        orchestrator._get_protocol_definition_orm_from_db = AsyncMock(
            return_value=mock_protocol_def
        )

        # Mock protocol run creation
        mock_run = Mock()
        mock_run.accession_id = uuid7()
        mock_run.status = ProtocolRunStatusEnum.RUNNING
        orchestrator.protocol_run_service.create.return_value = mock_run

        # Mock run context
        mock_run_context = Mock()
        mock_praxis_state = Mock()
        mock_run_context.canonical_state = mock_praxis_state
        orchestrator._initialize_run_context = AsyncMock(return_value=mock_run_context)

        # Mock pre-execution checks
        orchestrator._handle_pre_execution_checks = AsyncMock()

        # Mock main logic to raise exception
        orchestrator._execute_protocol_main_logic = AsyncMock(
            side_effect=ValueError("Test error in protocol execution")
        )

        # Mock error handler
        orchestrator._handle_protocol_execution_error = AsyncMock()

        # Mock finalization
        orchestrator._finalize_protocol_run = AsyncMock()

        # Execute
        await orchestrator.execute_protocol(
            protocol_name="test_protocol",
        )

        # Verify error handler was called
        orchestrator._handle_protocol_execution_error.assert_called_once()
        call_args = orchestrator._handle_protocol_execution_error.call_args[0]
        assert call_args[1] == "test_protocol"  # protocol name
        assert isinstance(call_args[2], ValueError)  # exception
        assert call_args[3] == mock_praxis_state  # praxis_state

        # Verify finalization was called despite error
        orchestrator._finalize_protocol_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_protocol_commit_failure_triggers_rollback(self) -> None:
        """Test that commit failure triggers rollback."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.create = AsyncMock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session with commit failure
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock()

        # Make final commit fail
        commit_call_count = []

        async def mock_commit():
            commit_call_count.append(1)
            if len(commit_call_count) >= 2:  # Final commit fails
                msg = "Database commit failed"
                raise Exception(msg)

        mock_db_session.commit = mock_commit
        mock_db_session.rollback = AsyncMock()

        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Mock protocol definition
        mock_protocol_def = Mock()
        mock_protocol_def.accession_id = uuid7()
        mock_protocol_def.name = "test_protocol"
        orchestrator._get_protocol_definition_orm_from_db = AsyncMock(
            return_value=mock_protocol_def
        )

        # Mock protocol run
        mock_run = Mock()
        mock_run.accession_id = uuid7()
        mock_run.status = ProtocolRunStatusEnum.PREPARING
        orchestrator.protocol_run_service.create.return_value = mock_run

        # Mock run context
        mock_run_context = Mock()
        mock_run_context.canonical_state = Mock()
        orchestrator._initialize_run_context = AsyncMock(return_value=mock_run_context)

        # Mock pre-execution and main logic
        orchestrator._handle_pre_execution_checks = AsyncMock()
        orchestrator._execute_protocol_main_logic = AsyncMock(return_value=({}, {}))

        # Mock finalization
        orchestrator._finalize_protocol_run = AsyncMock()

        # Execute - should not raise despite commit failure
        await orchestrator.execute_protocol(
            protocol_name="test_protocol",
        )

        # Verify rollback was called
        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_protocol_finalization_always_runs(self) -> None:
        """Test that finalization always runs even with errors."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.create = AsyncMock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock()
        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Mock protocol definition
        mock_protocol_def = Mock()
        mock_protocol_def.accession_id = uuid7()
        mock_protocol_def.name = "test_protocol"
        orchestrator._get_protocol_definition_orm_from_db = AsyncMock(
            return_value=mock_protocol_def
        )

        # Mock protocol run
        mock_run = Mock()
        run_id = uuid7()
        mock_run.accession_id = run_id
        mock_run.status = ProtocolRunStatusEnum.RUNNING
        orchestrator.protocol_run_service.create.return_value = mock_run

        # Mock run context
        mock_run_context = Mock()
        mock_praxis_state = Mock()
        mock_run_context.canonical_state = mock_praxis_state
        orchestrator._initialize_run_context = AsyncMock(return_value=mock_run_context)

        # Mock pre-execution checks
        orchestrator._handle_pre_execution_checks = AsyncMock()

        # Mock main logic to raise exception
        uuid7()
        orchestrator._execute_protocol_main_logic = AsyncMock(
            side_effect=RuntimeError("Protocol execution failed")
        )

        # Mock error handler
        orchestrator._handle_protocol_execution_error = AsyncMock()

        # Mock finalization
        finalization_called = []

        async def mock_finalize(run_orm, state, assets, db):
            finalization_called.append((run_orm, state, assets))

        orchestrator._finalize_protocol_run = mock_finalize

        # Execute
        await orchestrator.execute_protocol(
            protocol_name="test_protocol",
        )

        # Verify finalization was called with correct args
        assert len(finalization_called) == 1
        assert finalization_called[0][1] == mock_praxis_state  # praxis_state passed
        # acquired_assets should be empty dict since error happened before asset acquisition
        assert finalization_called[0][2] == {}


# ==============================================================================
# Phase 4: execute_existing_protocol_run() - Celery Entry Point Tests
# ==============================================================================


class TestExecuteExistingProtocolRun:
    """Tests for execute_existing_protocol_run method (Celery worker entry point)."""

    @pytest.mark.asyncio
    async def test_execute_existing_protocol_run_success(self) -> None:
        """Test successful execution of existing protocol run."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock(return_value=None)
        mock_db_session.get = AsyncMock()  # For ORM refresh in finally
        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Create mock protocol run with definition
        mock_protocol_def = Mock()
        mock_protocol_def.name = "test_protocol"
        mock_protocol_def.accession_id = uuid7()

        mock_run = Mock()
        run_id = uuid7()
        mock_run.accession_id = run_id
        mock_run.status = ProtocolRunStatusEnum.PREPARING
        mock_run.top_level_protocol_definition = mock_protocol_def

        # Mock for ORM refresh in finally block
        mock_db_session.get.return_value = mock_run

        # Mock run context
        mock_run_context = Mock()
        mock_run_context.canonical_state = Mock()
        orchestrator._initialize_run_context = AsyncMock(return_value=mock_run_context)

        # Mock pre-execution checks
        orchestrator._handle_pre_execution_checks = AsyncMock()

        # Mock main logic execution
        orchestrator._execute_protocol_main_logic = AsyncMock(
            return_value=({"result": "success"}, {})
        )

        # Mock finalization
        orchestrator._finalize_protocol_run = AsyncMock()

        # Execute
        await orchestrator.execute_existing_protocol_run(
            protocol_run_orm=mock_run,
            user_input_params={"param": "value"},
            initial_state_data={"state": "data"},
        )

        # Verify status transitions
        assert any(
            call[0][2] == ProtocolRunStatusEnum.RUNNING
            for call in orchestrator.protocol_run_service.update_run_status.call_args_list
        )
        assert any(
            call[0][2] == ProtocolRunStatusEnum.COMPLETED
            for call in orchestrator.protocol_run_service.update_run_status.call_args_list
        )

        # Verify finalization called
        orchestrator._finalize_protocol_run.assert_called_once()

        # Verify ORM refreshed before finalization
        mock_db_session.get.assert_called_with(ProtocolRunOrm, run_id)

    @pytest.mark.asyncio
    async def test_execute_existing_protocol_run_no_definition(self) -> None:
        """Test error when protocol run has no protocol definition."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock(return_value=None)
        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Create mock protocol run WITHOUT definition
        mock_run = Mock()
        run_id = uuid7()
        mock_run.accession_id = run_id
        mock_run.top_level_protocol_definition = None

        # Execute and verify error
        with pytest.raises(ValueError, match="Protocol definition not found"):
            await orchestrator.execute_existing_protocol_run(protocol_run_orm=mock_run)

        # Verify status updated to FAILED
        orchestrator.protocol_run_service.update_run_status.assert_called_once()
        call_args = orchestrator.protocol_run_service.update_run_status.call_args
        assert call_args[0][2] == ProtocolRunStatusEnum.FAILED

    @pytest.mark.asyncio
    async def test_execute_existing_protocol_run_from_queued_status(self) -> None:
        """Test execution starting from QUEUED status (not just PREPARING)."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock(return_value=None)
        mock_db_session.get = AsyncMock()
        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Create mock protocol run with QUEUED status
        mock_protocol_def = Mock()
        mock_protocol_def.name = "test_protocol"
        mock_protocol_def.accession_id = uuid7()

        mock_run = Mock()
        run_id = uuid7()
        mock_run.accession_id = run_id
        mock_run.status = ProtocolRunStatusEnum.QUEUED  # Start from QUEUED
        mock_run.top_level_protocol_definition = mock_protocol_def

        mock_db_session.get.return_value = mock_run

        # Mock dependencies
        mock_run_context = Mock()
        mock_run_context.canonical_state = Mock()
        orchestrator._initialize_run_context = AsyncMock(return_value=mock_run_context)
        orchestrator._handle_pre_execution_checks = AsyncMock()
        orchestrator._execute_protocol_main_logic = AsyncMock(return_value=({}, {}))
        orchestrator._finalize_protocol_run = AsyncMock()

        # Execute
        await orchestrator.execute_existing_protocol_run(protocol_run_orm=mock_run)

        # Verify status updated from QUEUED to RUNNING
        assert any(
            call[0][2] == ProtocolRunStatusEnum.RUNNING
            for call in orchestrator.protocol_run_service.update_run_status.call_args_list
        ), "Should update QUEUED status to RUNNING"

    @pytest.mark.asyncio
    async def test_execute_existing_protocol_run_cancelled_error(self) -> None:
        """Test ProtocolCancelledError handling in existing run."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock(return_value=None)
        mock_db_session.get = AsyncMock()
        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Create mock protocol run
        mock_protocol_def = Mock()
        mock_protocol_def.name = "test_protocol"

        mock_run = Mock()
        run_id = uuid7()
        mock_run.accession_id = run_id
        mock_run.status = ProtocolRunStatusEnum.PREPARING
        mock_run.top_level_protocol_definition = mock_protocol_def

        mock_db_session.get.return_value = mock_run

        # Mock dependencies
        mock_run_context = Mock()
        mock_run_context.canonical_state = Mock()
        orchestrator._initialize_run_context = AsyncMock(return_value=mock_run_context)
        orchestrator._handle_pre_execution_checks = AsyncMock()

        # Main logic raises ProtocolCancelledError
        orchestrator._execute_protocol_main_logic = AsyncMock(
            side_effect=ProtocolCancelledError("Cancelled")
        )

        orchestrator._finalize_protocol_run = AsyncMock()

        # Execute - should not raise
        await orchestrator.execute_existing_protocol_run(protocol_run_orm=mock_run)

        # Verify finalization still called
        orchestrator._finalize_protocol_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_existing_protocol_run_generic_exception(self) -> None:
        """Test generic exception handling in existing run."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock(return_value=None)
        mock_db_session.get = AsyncMock()
        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Create mock protocol run
        mock_protocol_def = Mock()
        mock_protocol_def.name = "test_protocol"

        mock_run = Mock()
        run_id = uuid7()
        mock_run.accession_id = run_id
        mock_run.status = ProtocolRunStatusEnum.PREPARING
        mock_run.top_level_protocol_definition = mock_protocol_def

        mock_db_session.get.return_value = mock_run

        # Mock dependencies
        mock_run_context = Mock()
        mock_run_context.canonical_state = Mock()
        orchestrator._initialize_run_context = AsyncMock(return_value=mock_run_context)
        orchestrator._handle_pre_execution_checks = AsyncMock()

        # Main logic raises generic exception
        orchestrator._execute_protocol_main_logic = AsyncMock(
            side_effect=RuntimeError("Test error")
        )

        orchestrator._handle_protocol_execution_error = AsyncMock()
        orchestrator._finalize_protocol_run = AsyncMock()

        # Execute
        await orchestrator.execute_existing_protocol_run(protocol_run_orm=mock_run)

        # Verify error handler called
        orchestrator._handle_protocol_execution_error.assert_called_once()

        # Verify finalization still called
        orchestrator._finalize_protocol_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_existing_protocol_run_orm_not_found_for_finalization(
        self,
    ) -> None:
        """Test edge case when ORM cannot be retrieved for finalization."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session
        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock(return_value=None)
        mock_db_session.get = AsyncMock(return_value=None)  # ORM not found!
        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Create mock protocol run
        mock_protocol_def = Mock()
        mock_protocol_def.name = "test_protocol"

        mock_run = Mock()
        run_id = uuid7()
        mock_run.accession_id = run_id
        mock_run.status = ProtocolRunStatusEnum.PREPARING
        mock_run.top_level_protocol_definition = mock_protocol_def

        # Mock dependencies
        mock_run_context = Mock()
        mock_run_context.canonical_state = Mock()
        orchestrator._initialize_run_context = AsyncMock(return_value=mock_run_context)
        orchestrator._handle_pre_execution_checks = AsyncMock()
        orchestrator._execute_protocol_main_logic = AsyncMock(return_value=({}, {}))
        orchestrator._finalize_protocol_run = AsyncMock()

        # Execute - should not crash even if ORM not found
        await orchestrator.execute_existing_protocol_run(protocol_run_orm=mock_run)

        # Verify finalization NOT called (ORM was None)
        orchestrator._finalize_protocol_run.assert_not_called()

        # Verify error logged (implicit - no crash means logger.error was called)

    @pytest.mark.asyncio
    async def test_execute_existing_protocol_run_commit_failure(self) -> None:
        """Test commit failure triggers rollback in existing run."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
            protocol_code_manager=Mock(),
        )
        orchestrator.protocol_run_service = Mock()
        orchestrator.protocol_run_service.update_run_status = AsyncMock()

        # Mock database session with commit failure
        commit_call_count = []

        async def mock_commit():
            commit_call_count.append(1)
            if len(commit_call_count) >= 2:  # Final commit fails
                msg = "Database commit failed"
                raise Exception(msg)

        mock_db_session = AsyncMock()
        mock_db_session.__aenter__ = AsyncMock(return_value=mock_db_session)
        mock_db_session.__aexit__ = AsyncMock(return_value=None)
        mock_db_session.commit = mock_commit
        mock_db_session.rollback = AsyncMock()
        mock_db_session.get = AsyncMock()
        orchestrator.db_session_factory = Mock(return_value=mock_db_session)

        # Create mock protocol run
        mock_protocol_def = Mock()
        mock_protocol_def.name = "test_protocol"

        mock_run = Mock()
        run_id = uuid7()
        mock_run.accession_id = run_id
        mock_run.status = ProtocolRunStatusEnum.PREPARING
        mock_run.top_level_protocol_definition = mock_protocol_def

        mock_db_session.get.return_value = mock_run

        # Mock dependencies
        mock_run_context = Mock()
        mock_run_context.canonical_state = Mock()
        orchestrator._initialize_run_context = AsyncMock(return_value=mock_run_context)
        orchestrator._handle_pre_execution_checks = AsyncMock()
        orchestrator._execute_protocol_main_logic = AsyncMock(return_value=({}, {}))
        orchestrator._finalize_protocol_run = AsyncMock()

        # Execute
        await orchestrator.execute_existing_protocol_run(protocol_run_orm=mock_run)

        # Verify rollback was called after commit failure
        mock_db_session.rollback.assert_called_once()
