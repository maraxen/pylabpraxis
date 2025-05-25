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

    # --- Tests for In-Step Command Handling (Decorator Logic) ---

    @patch('praxis.backend.protocol_core.decorators.get_control_command')
    @patch('praxis.backend.protocol_core.decorators.clear_control_command')
    @patch('praxis.backend.protocol_core.decorators.update_protocol_run_status')
    @patch('praxis.backend.protocol_core.decorators.time.sleep')
    def test_pause_resume_during_protocol_step(
        self,
        mock_decorator_sleep,
        mock_decorator_update_status,
        mock_decorator_clear_cmd,
        mock_decorator_get_cmd,
        orchestrator_instance,
        mock_protocol_def_orm,
        mock_protocol_run_orm,
        mock_db_session # For context
    ):
        orchestrator, _ = orchestrator_instance # Orchestrator's sleep mock not used here
        protocol_def, decorator_meta = mock_protocol_def_orm
        
        # Ensure Orchestrator's own pre-execution command checks are bypassed
        mock_run_control_get.side_effect = [None, None] # For Orchestrator's initial checks

        # Mock for the protocol function's context
        mock_praxis_run_context = MagicMock(spec=PraxisRunContext)
        mock_praxis_run_context.run_guid = mock_protocol_run_orm.run_guid
        mock_praxis_run_context.protocol_run_db_id = mock_protocol_run_orm.id
        mock_praxis_run_context.current_db_session = mock_db_session

        # Simulate the sequence of commands the decorator will see
        mock_decorator_get_cmd.side_effect = [
            None,    # First check inside decorator before user code
            "PAUSE", # Second check, PAUSE command received
            None,    # Inside decorator's pause loop
            None,    # Inside decorator's pause loop
            "RESUME" # RESUME command received
        ]

        # This is the mock for the actual user-written protocol function
        user_protocol_function_mock = MagicMock(return_value={"status": "user_code_completed"})

        def mock_protocol_wrapper_side_effect(*args, **kwargs):
            # This simulates the decorator's command handling logic
            # __praxis_run_context__ is passed by the orchestrator to the wrapper
            ctx = kwargs.get('__praxis_run_context__', mock_praxis_run_context) # Fallback for safety

            # Simulate 1st command check in decorator (before user code)
            cmd1 = mock_decorator_get_cmd(ctx.run_guid) # Sees None
            # No command, so it would proceed to call user_protocol_function_mock,
            # but we embed further command checks as if they are part of user_protocol_function_mock's execution flow
            # for this test's purpose, to simulate commands during the step.

            # Simulate decorator checking for command *during* the step (conceptually)
            cmd2 = mock_decorator_get_cmd(ctx.run_guid) # Sees PAUSE
            if cmd2 == "PAUSE":
                mock_decorator_clear_cmd(ctx.run_guid)
                mock_decorator_update_status(ctx.current_db_session, ctx.protocol_run_db_id, ProtocolRunStatusEnum.PAUSING)
                mock_decorator_update_status(ctx.current_db_session, ctx.protocol_run_db_id, ProtocolRunStatusEnum.PAUSED)
                
                paused = True
                while paused:
                    mock_decorator_sleep(1)
                    cmd_in_pause = mock_decorator_get_cmd(ctx.run_guid)
                    if cmd_in_pause == "RESUME":
                        mock_decorator_clear_cmd(ctx.run_guid)
                        mock_decorator_update_status(ctx.current_db_session, ctx.protocol_run_db_id, ProtocolRunStatusEnum.RESUMING)
                        mock_decorator_update_status(ctx.current_db_session, ctx.protocol_run_db_id, ProtocolRunStatusEnum.RUNNING)
                        paused = False
                    elif cmd_in_pause == "CANCEL": # Should not happen in this test's side_effect
                        raise ProtocolCancelledError("Cancelled during pause") 
            
            # If resumed, the actual user function is called
            result = user_protocol_function_mock(*args, **{k:v for k,v in kwargs.items() if k != '__praxis_run_context__'})
            return result

        mock_wrapper_func_instance = MagicMock(side_effect=mock_protocol_wrapper_side_effect)
        # Attach the original metadata, as Orchestrator uses it
        mock_wrapper_func_instance.protocol_metadata = decorator_meta 
        
        orchestrator._prepare_protocol_code = MagicMock(return_value=(mock_wrapper_func_instance, decorator_meta))
        orchestrator._prepare_arguments = MagicMock(return_value=({}, PraxisState(), []))
        mock_get_protocol_definition_details.return_value = protocol_def
        mock_create_protocol_run.return_value = mock_protocol_run_orm

        # Execute
        result = orchestrator.execute_protocol(protocol_name="TestProtocol", user_input_params={})

        # Assertions
        assert result == {"status": "user_code_completed"}
        user_protocol_function_mock.assert_called_once() # Ensure the actual user code ran

        # Check calls to decorator's mocks
        decorator_status_calls = [
            call(mock_db_session, mock_protocol_run_orm.id, ProtocolRunStatusEnum.PAUSING),
            call(mock_db_session, mock_protocol_run_orm.id, ProtocolRunStatusEnum.PAUSED),
            call(mock_db_session, mock_protocol_run_orm.id, ProtocolRunStatusEnum.RESUMING),
            call(mock_db_session, mock_protocol_run_orm.id, ProtocolRunStatusEnum.RUNNING),
        ]
        mock_decorator_update_status.assert_has_calls(decorator_status_calls, any_order=False)
        
        mock_decorator_clear_cmd.assert_has_calls([
            call(mock_protocol_run_orm.run_guid), # For PAUSE
            call(mock_protocol_run_orm.run_guid)  # For RESUME
        ])
        assert mock_decorator_clear_cmd.call_count == 2
        assert mock_decorator_sleep.call_count >= 2 # At least two sleeps during pause

        # Check Orchestrator's status updates (it will still log COMPLETED at the end)
        # The RUNNING status before the pause is handled by the Orchestrator itself.
        orchestrator_final_status_call = call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.COMPLETED, output_data_json=ANY)
        assert mock_update_protocol_run_status.call_args_list[-1] == orchestrator_final_status_call


    @patch('praxis.backend.protocol_core.decorators.get_control_command')
    @patch('praxis.backend.protocol_core.decorators.clear_control_command')
    @patch('praxis.backend.protocol_core.decorators.update_protocol_run_status')
    @patch('praxis.backend.protocol_core.decorators.time.sleep') # Though not used in cancel path
    def test_cancel_during_protocol_step(
        self,
        mock_decorator_sleep,
        mock_decorator_update_status,
        mock_decorator_clear_cmd,
        mock_decorator_get_cmd,
        orchestrator_instance,
        mock_protocol_def_orm,
        mock_protocol_run_orm,
        mock_db_session,
        mock_asset_manager
    ):
        orchestrator, _ = orchestrator_instance
        protocol_def, decorator_meta = mock_protocol_def_orm
        
        mock_run_control_get.side_effect = [None, None] # Orchestrator's pre-execution checks

        mock_praxis_run_context = MagicMock(spec=PraxisRunContext)
        mock_praxis_run_context.run_guid = mock_protocol_run_orm.run_guid
        mock_praxis_run_context.protocol_run_db_id = mock_protocol_run_orm.id
        mock_praxis_run_context.current_db_session = mock_db_session

        mock_decorator_get_cmd.side_effect = [
            None,    # First check inside decorator
            "CANCEL" # CANCEL command received
        ]
        
        user_protocol_function_mock = MagicMock() # This should not be called

        def mock_protocol_wrapper_side_effect(*args, **kwargs):
            ctx = kwargs.get('__praxis_run_context__', mock_praxis_run_context)

            cmd1 = mock_decorator_get_cmd(ctx.run_guid) # Sees None
            
            # Simulate decorator checking for command *during* the step
            cmd2 = mock_decorator_get_cmd(ctx.run_guid) # Sees CANCEL
            if cmd2 == "CANCEL":
                mock_decorator_clear_cmd(ctx.run_guid)
                mock_decorator_update_status(ctx.current_db_session, ctx.protocol_run_db_id, ProtocolRunStatusEnum.CANCELING)
                mock_decorator_update_status(ctx.current_db_session, ctx.protocol_run_db_id, ProtocolRunStatusEnum.CANCELLED, output_data_json=ANY)
                raise ProtocolCancelledError(f"Cancelled by user during step {ctx.run_guid}")
            
            user_protocol_function_mock(*args, **{k:v for k,v in kwargs.items() if k != '__praxis_run_context__'})
            return {"status": "should_not_complete"}


        mock_wrapper_func_instance = MagicMock(side_effect=mock_protocol_wrapper_side_effect)
        mock_wrapper_func_instance.protocol_metadata = decorator_meta
        
        # Simulate acquired assets for release check
        acquired_assets_info = [{"type": "device", "orm_id": 789, "name_in_protocol": "test_device_cancel"}]
        orchestrator._prepare_arguments = MagicMock(return_value=({}, PraxisState(), acquired_assets_info))
        
        orchestrator._prepare_protocol_code = MagicMock(return_value=(mock_wrapper_func_instance, decorator_meta))
        mock_get_protocol_definition_details.return_value = protocol_def
        mock_create_protocol_run.return_value = mock_protocol_run_orm

        with pytest.raises(ProtocolCancelledError, match=f"Cancelled by user during step {mock_protocol_run_orm.run_guid}"):
            orchestrator.execute_protocol(protocol_name="TestProtocol", user_input_params={})

        user_protocol_function_mock.assert_not_called()

        decorator_status_calls = [
            call(mock_db_session, mock_protocol_run_orm.id, ProtocolRunStatusEnum.CANCELING),
            call(mock_db_session, mock_protocol_run_orm.id, ProtocolRunStatusEnum.CANCELLED, output_data_json=ANY),
        ]
        mock_decorator_update_status.assert_has_calls(decorator_status_calls, any_order=False)
        mock_decorator_clear_cmd.assert_called_once_with(mock_protocol_run_orm.run_guid)

        # Check Orchestrator's final status update (should be CANCELLED by the orchestrator itself due to the raised error)
        orchestrator_final_status_call = call(ANY, mock_protocol_run_orm.id, ProtocolRunStatusEnum.CANCELLED, output_data_json=ANY)
        # Ensure the *last* call to the orchestrator's mock_update_protocol_run_status was for CANCELLED
        assert mock_update_protocol_run_status.call_args_list[-1] == orchestrator_final_status_call
        
        # Check asset release
        mock_asset_manager.release_device.assert_called_once_with(device_orm_id=789)
        mock_asset_manager.release_labware.assert_not_called()
```
