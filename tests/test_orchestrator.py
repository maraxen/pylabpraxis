import pytest
from unittest.mock import MagicMock, patch, call, ANY
import time
import uuid
import json # For dummy JSON data

from praxis.backend.core.orchestrator import Orchestrator, ProtocolCancelledError
from praxis.backend.database_models.protocol_definitions_orm import (
    ProtocolRunStatusEnum, 
    FunctionProtocolDefinitionOrm, 
    ProtocolRunOrm,
    FileSystemProtocolSourceOrm # For mock_protocol_def_orm
)
from praxis.utils.state import State as PraxisState
from praxis.backend.protocol_core.definitions import PraxisRunContext
from praxis.backend.protocol_core.protocol_definition_models import FunctionProtocolDefinitionModel, ParameterMetadataModel, AssetRequirementModel

# Mock for services that Orchestrator uses internally
# These would be patched where Orchestrator looks them up.
mock_create_protocol_run = MagicMock()
mock_update_protocol_run_status = MagicMock()
mock_get_protocol_definition_details = MagicMock()

mock_run_control_get = MagicMock()
mock_run_control_clear = MagicMock()

@pytest.fixture
def mock_db_session(): # Removed self
    return MagicMock()

@pytest.fixture
def mock_asset_manager(): # Removed self
    mock_am = MagicMock()
    mock_am.acquire_asset.return_value = (MagicMock(name="live_asset"), 123, "device") # live_obj, orm_id, asset_type_str
    mock_am.release_device = MagicMock()
    mock_am.release_labware = MagicMock()
    return mock_am
    
@pytest.fixture
def mock_protocol_def_orm(): # Removed self
    # Create a somewhat realistic FunctionProtocolDefinitionOrm mock
    pdo = MagicMock(spec=FunctionProtocolDefinitionOrm)
    pdo.id = 1
    pdo.name = "TestProtocol"
    pdo.version = "1.0"
    pdo.module_name = "mock_protocol_module"
    pdo.function_name = "mock_protocol_function"
    pdo.source_repository_id = None
    pdo.source_repository = None
    pdo.file_system_source_id = 1
    pdo.file_system_source = MagicMock(spec=FileSystemProtocolSourceOrm, base_path="dummy/path")
    pdo.commit_hash = None
    pdo.is_top_level = True
    pdo.preconfigure_deck = False
    pdo.deck_param_name = None
    
    mock_pydantic_def = MagicMock(spec=FunctionProtocolDefinitionModel)
    mock_pydantic_def.parameters = [] 
    mock_pydantic_def.assets = []     
    
    mock_decorator_metadata = {
        "name": "TestProtocol",
        "version": "1.0",
        "db_id": 1, 
        "protocol_unique_key": "TestProtocol_v1.0",
        "parameters": {}, 
        "assets": [],     
        "state_param_name": "state",
        "found_state_param_details": {"expects_praxis_state": True},
        "pydantic_definition": mock_pydantic_def 
    }
    return pdo, mock_decorator_metadata


@pytest.fixture
def mock_protocol_run_orm(): # Removed self
    pro = MagicMock(spec=ProtocolRunOrm)
    pro.id = 99
    pro.run_guid = str(uuid.uuid4())
    # Status is set to PREPARING by create_protocol_run initially
    pro.status = ProtocolRunStatusEnum.PREPARING 
    return pro

@pytest.fixture
def orchestrator_instance(mock_db_session, mock_asset_manager): # Removed self from params
    with patch('praxis.backend.core.orchestrator.create_protocol_run', mock_create_protocol_run), \
         patch('praxis.backend.core.orchestrator.update_protocol_run_status', mock_update_protocol_run_status), \
         patch('praxis.backend.core.orchestrator.get_protocol_definition_details', mock_get_protocol_definition_details), \
         patch('praxis.backend.core.orchestrator.get_control_command', mock_run_control_get), \
         patch('praxis.backend.core.orchestrator.clear_control_command', mock_run_control_clear), \
         patch('praxis.backend.core.orchestrator.AssetManager', return_value=mock_asset_manager), \
         patch('time.sleep', MagicMock()) as mock_sleep:
        
        mock_create_protocol_run.reset_mock()
        mock_update_protocol_run_status.reset_mock()
        mock_get_protocol_definition_details.reset_mock()
        mock_run_control_get.reset_mock()
        mock_run_control_clear.reset_mock()
        
        # Reset the main mock_asset_manager and its methods
        mock_asset_manager.reset_mock()
        mock_asset_manager.acquire_asset.reset_mock()
        mock_asset_manager.release_device.reset_mock()
        mock_asset_manager.release_labware.reset_mock()
        
        mock_sleep.reset_mock()

        orch = Orchestrator(db_session=mock_db_session)
        yield orch, mock_sleep

class TestOrchestratorExecutionControl:

    @pytest.fixture
    def mock_protocol_wrapper_func(self): # Removed self
        mf = MagicMock(name="mock_protocol_wrapper_func")
        mf.return_value = {"status": "mock_protocol_completed"}
        return mf

    def test_pause_and_resume_flow(self, orchestrator_instance, mock_protocol_def_orm, mock_protocol_run_orm, mock_protocol_wrapper_func):
        orchestrator, mock_sleep = orchestrator_instance
        protocol_def, decorator_meta = mock_protocol_def_orm
        
        mock_protocol_wrapper_func.protocol_metadata = decorator_meta

        mock_get_protocol_definition_details.return_value = protocol_def
        # Simulate create_protocol_run setting the initial state to PREPARING
        mock_create_protocol_run.return_value = mock_protocol_run_orm 
        
        orchestrator._prepare_protocol_code = MagicMock(return_value=(mock_protocol_wrapper_func, decorator_meta))
        orchestrator._prepare_arguments = MagicMock(return_value=({}, None, [])) # No assets for this test

        mock_run_control_get.side_effect = [
            None,       # Initial check right after run creation
            None,       # Check before main execution logic (after _prepare_arguments)
            "PAUSE",    # Check inside the loop before protocol_wrapper_func call
            None,       # Inside pause loop (stay paused)
            None,       # Inside pause loop (stay paused)
            "RESUME",   # Inside pause loop (resume command)
            None        # Any subsequent checks (e.g. within protocol steps, not tested here)
        ]
        
        orchestrator.execute_protocol(
            protocol_name="TestProtocol",
            user_input_params={}
        )

        mock_run_control_clear.assert_any_call(mock_protocol_run_orm.run_guid) 
        assert mock_run_control_clear.call_count == 2 # For PAUSE and RESUME

        expected_status_calls = [
            call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.RUNNING), # Set after successful prep & before pause check
            call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.PAUSING),
            call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.PAUSED),
            call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.RESUMING),
            call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.RUNNING), # Set after resume
            call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.COMPLETED, output_data_json=ANY) 
        ]
        
        actual_calls = mock_update_protocol_run_status.call_args_list
        assert actual_calls == expected_status_calls
        
        mock_protocol_wrapper_func.assert_called_once() 
        assert mock_sleep.call_count >= 2 

    def test_cancel_during_pause_flow(self, orchestrator_instance, mock_protocol_def_orm, mock_protocol_run_orm, mock_protocol_wrapper_func):
        orchestrator, mock_sleep = orchestrator_instance
        protocol_def, decorator_meta = mock_protocol_def_orm
        mock_protocol_wrapper_func.protocol_metadata = decorator_meta

        mock_get_protocol_definition_details.return_value = protocol_def
        mock_create_protocol_run.return_value = mock_protocol_run_orm
        orchestrator._prepare_protocol_code = MagicMock(return_value=(mock_protocol_wrapper_func, decorator_meta))
        
        acquired_assets_info = [{"type": "device", "orm_id": 123, "name_in_protocol": "mock_device"}]
        orchestrator._prepare_arguments = MagicMock(return_value=({}, None, acquired_assets_info)) 

        mock_run_control_get.side_effect = [
            None,    # Initial check
            None,    # Check before pause loop
            "PAUSE", # Detected before wrapper call
            None,    # In pause loop
            "CANCEL" # Detected in pause loop
        ]

        with pytest.raises(ProtocolCancelledError, match="cancelled by user during pause"):
            orchestrator.execute_protocol(protocol_name="TestProtocol", user_input_params={})

        mock_run_control_clear.assert_any_call(mock_protocol_run_orm.run_guid) 
        assert mock_run_control_clear.call_count == 2
        
        actual_calls = mock_update_protocol_run_status.call_args_list
        
        assert actual_calls[0] == call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.RUNNING)
        assert actual_calls[1] == call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.PAUSING)
        assert actual_calls[2] == call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.PAUSED)
        assert actual_calls[3] == call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.CANCELING)
        assert actual_calls[4] == call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.CANCELLED, output_data_json=json.dumps({"status": "Cancelled by user during pause."}))

        mock_protocol_wrapper_func.assert_not_called() 
        
        orchestrator.asset_manager.release_device.assert_called_once_with(device_orm_id=123)
        orchestrator.asset_manager.release_labware.assert_not_called()

    # TODO: Add more tests here for:
    # - test_cancel_before_execution_starts (after _prepare_arguments, before pause loop)
    # - test_cancel_at_very_beginning (first command check)
    # - test_normal_execution_no_commands
    # - test_asset_release_on_cancel_with_multiple_assets
    # - test_asset_release_on_failure_with_acquired_assets
    # - test_run_status_when_protocol_def_not_found
    # - test_run_status_when_prepare_code_fails
    # - test_run_status_when_prepare_args_fails (e.g., asset acquisition)
```
