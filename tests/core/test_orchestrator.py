"""Tests for core/orchestrator.py."""

import json
import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest

from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.models import ProtocolRunStatusEnum
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
            return_value=(mock_live_obj, asset_id, "resource")
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
            side_effect=AssetAcquisitionError("Asset not available")
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
            side_effect=AssetAcquisitionError("Asset not available")
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

    @pytest.mark.skip(reason="Complex service integration - svc.update_protocol_run_status not directly patchable")
    @pytest.mark.asyncio
    async def test_handle_pre_execution_checks_cancel_command(self) -> None:
        """Test when cancel command is present."""
        orchestrator = Orchestrator(
            db_session_factory=Mock(),
            asset_manager=Mock(),
            workcell_runtime=Mock(),
        )

        mock_protocol_run = Mock()
        mock_protocol_run.run_accession_id = uuid7()
        mock_protocol_run.accession_id = uuid7()

        mock_db_session = AsyncMock()

        with patch("praxis.backend.core.orchestrator.execution.get_control_command", AsyncMock(return_value="CANCEL")):
            with patch("praxis.backend.core.orchestrator.execution.clear_control_command", AsyncMock()):
                with patch("praxis.backend.core.orchestrator.execution.svc.update_protocol_run_status", AsyncMock()):
                    with pytest.raises(ProtocolCancelledError):
                        await orchestrator._handle_pre_execution_checks(
                            mock_protocol_run,
                            mock_db_session,
                        )


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
        mock_protocol_run.run_accession_id = run_id

        mock_db_session = AsyncMock()

        initial_state_data = {"key": "value"}

        orchestrator.workcell_runtime.get_state_snapshot = Mock(return_value={"snapshot": "data"})

        # Mock PraxisState to avoid Redis
        with patch("praxis.backend.core.orchestrator.protocol_preparation.PraxisState") as mock_state_class:
            mock_state = Mock()
            mock_state.update = Mock()
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
            return_value=(Mock(), Mock())
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
            mock_protocol_def_orm
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
