import pytest # type: ignore
import os
import sys
import tempfile
import shutil
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch, ANY

from sqlalchemy.orm import Session as DbSession # For type hinting if needed

# Modules to test
from praxis.backend.services.discovery_service import ProtocolDiscoveryService
from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.protocol_core.decorators import protocol_function
from praxis.backend.protocol_core.definitions import PraxisState, PraxisRunContext, PlrResource
from praxis.backend.protocol_core.protocol_definition_models import FunctionProtocolDefinitionModel
from praxis.backend.database_models.protocol_definitions_orm import (
    FunctionProtocolDefinitionOrm, ParameterDefinitionOrm, AssetDefinitionOrm,
    ProtocolRunOrm, FunctionCallLogOrm, ProtocolRunStatusEnum, FunctionCallStatusEnum
)
# Need these for the mock_upsert function
from praxis.backend.database_models.protocol_definitions_orm import ProtocolSourceRepositoryOrm, FileSystemProtocolSourceOrm
import json # For serializing in assertions


# Dummy PLR resource for type hinting in test protocols
class IntegrationPipette(PlrResource):
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, size_x=1, size_y=1, size_z=1, **kwargs)
    def pick_up_tip(self):
        print(f"{self.name} picking up tip.")
    def aspirate(self, vol: int):
        print(f"{self.name} aspirating {vol}ul.")
    def dispense(self, vol: int):
        print(f"{self.name} dispensing {vol}ul.")

@pytest.fixture
def temp_integration_protocols():
    base_temp_dir = tempfile.mkdtemp()
    pkg_root_name = "integration_test_protocols"
    pkg_root_dir = os.path.join(base_temp_dir, pkg_root_name)
    os.makedirs(pkg_root_dir)
    with open(os.path.join(pkg_root_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("# Integration test protocol package root
")

    protocol_content = """
from praxis.backend.protocol_core.decorators import protocol_function
from praxis.backend.protocol_core.definitions import PraxisState
# Import the dummy resource from this test file
from tests.test_integration_discovery_execution import IntegrationPipette # Path relative to where pytest runs

@protocol_function(name="NestedProtocolStep", version="1.0")
def nested_step(state: PraxisState, message: str):
    print(f"Nested step executing with message: {message}")
    state.nested_step_ran = True # type: ignore
    return {"nested_output": message.upper()}

@protocol_function(name="MainIntegrationProtocol", version="1.1", is_top_level=True)
def main_protocol(state: PraxisState, pipette: IntegrationPipette, initial_message: str = "hello"):
    '''Main protocol for integration testing.'''
    print(f"MainIntegrationProtocol started with message: {initial_message}, pipette: {pipette.name}")
    state.main_protocol_started = True # type: ignore
    
    pipette.pick_up_tip()
    pipette.aspirate(50)
    
    # Call nested protocol
    nested_result = nested_step(state=state, message="from_main") # No context needed here, wrapper adds it
    
    pipette.dispense(50)
    
    state.main_protocol_completed = True # type: ignore
    return {"status": "main_complete", "nested_result": nested_result, "final_message": initial_message}
"""
    with open(os.path.join(pkg_root_dir, "protocol_module.py"), "w", encoding="utf-8") as f:
        f.write(protocol_content)
    
    yield pkg_root_dir # This is the path to scan (contains the 'integration_test_protocols' package)
    
    shutil.rmtree(base_temp_dir)

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=DbSession) # Mock a synchronous session

# Mock the entire protocol_data_service module that DiscoveryService and Orchestrator try to use
@pytest.fixture
def mock_protocol_data_service():
    with patch.multiple(
        'praxis.backend.services.protocol_data_service', # Path to where it's imported from
        upsert_function_protocol_definition=MagicMock(),
        create_protocol_run=MagicMock(),
        update_protocol_run_status=MagicMock(),
        log_function_call_start=MagicMock(),
        log_function_call_end=MagicMock(),
        get_protocol_definition_details=MagicMock() 
        # Add other functions if they are called during the test flow
    ) as mocks:
        # Configure return values for mocked service functions
        
        # For upsert_function_protocol_definition:
        # It needs to return an ORM-like object with an 'id' and relationships for parameters/assets
        def mock_upsert(db, protocol_pydantic: FunctionProtocolDefinitionModel, **kwargs):
            # Create a mock ORM object based on the Pydantic model
            mock_orm = MagicMock(spec=FunctionProtocolDefinitionOrm)
            mock_orm.id = abs(hash(protocol_pydantic.name + protocol_pydantic.version)) # Dummy ID
            mock_orm.name = protocol_pydantic.name
            mock_orm.version = protocol_pydantic.version
            mock_orm.description = protocol_pydantic.description
            mock_orm.module_name = protocol_pydantic.module_name
            mock_orm.function_name = protocol_pydantic.function_name
            mock_orm.is_top_level = protocol_pydantic.is_top_level
            # ... copy other relevant fields ...
            mock_orm.parameters = [MagicMock(spec=ParameterDefinitionOrm, name=p.name) for p in protocol_pydantic.parameters]
            mock_orm.assets = [MagicMock(spec=AssetDefinitionOrm, name=a.name) for a in protocol_pydantic.assets]
            # Simulate source linkage if needed by Orchestrator's _prepare_protocol_code
            mock_orm.source_repository_id = kwargs.get('source_repository_id')
            mock_orm.source_repository = MagicMock(spec=ProtocolSourceRepositoryOrm, local_checkout_path='dummy/repo/path') if kwargs.get('source_repository_id') else None
            mock_orm.file_system_source_id = kwargs.get('file_system_source_id')
            mock_orm.file_system_source = MagicMock(spec=FileSystemProtocolSourceOrm, base_path=tempfile.gettempdir()) if kwargs.get('file_system_source_id') else None # Use a valid path
            mock_orm.commit_hash = kwargs.get('commit_hash')

            return mock_orm
        mocks['upsert_function_protocol_definition'].side_effect = mock_upsert

        # For get_protocol_definition_details (used by Orchestrator):
        # This needs to return the same type of mock ORM object.
        mocks['get_protocol_definition_details'].return_value = None # Default, test can override

        # For create_protocol_run:
        mock_run_orm = MagicMock(spec=ProtocolRunOrm)
        mock_run_orm.id = 12345 # Dummy ProtocolRunOrm ID
        mock_run_orm.run_guid = "" # Will be set by test
        mocks['create_protocol_run'].return_value = mock_run_orm

        # For log_function_call_start:
        # It's important that this mock returns an object with an 'id' attribute,
        # as this ID is used as parent_function_call_log_id for nested calls.
        def mock_log_start(**kwargs):
            mock_log_entry = MagicMock(spec=FunctionCallLogOrm)
            mock_log_entry.id = abs(hash(kwargs.get('function_definition_id', 'unknown_func') + str(kwargs.get('sequence_in_run', 0))))
            # Store the passed kwargs in the mock for later assertion if needed
            mock_log_entry._custom_kwargs = kwargs 
            return mock_log_entry
        mocks['log_function_call_start'].side_effect = mock_log_start
        
        yield mocks

@pytest.fixture
def mock_redis_for_state():
    with patch('redis.Redis') as mock_redis_constructor:
        mock_instance = MagicMock()
        mock_instance.get.return_value = None # Default to no existing state
        mock_redis_constructor.return_value = mock_instance
        yield mock_instance

class TestIntegrationDiscoveryExecution:

    def test_discovery_and_basic_execution_logging(
        self,
        temp_integration_protocols: str, # This is pkg_root_dir
        mock_db_session: MagicMock,
        mock_protocol_data_service: Dict[str, MagicMock],
        mock_redis_for_state: MagicMock
    ):
        # --- 1. Discovery Phase ---
        discovery_service = ProtocolDiscoveryService(db_session=mock_db_session)
        
        # The discovery service adds the parent of the scan path to sys.path if not present.
        # Here, temp_integration_protocols is ".../integration_test_protocols".
        # Its parent is ".../". If this parent dir is not on sys.path, discovery adds it.
        # This allows "import integration_test_protocols.protocol_module".
        
        discovered_defs_orm_mocks = discovery_service.discover_and_upsert_protocols(
            search_paths=[temp_integration_protocols], # Scan the package root directory
            file_system_source_id=1 
        )

        assert len(discovered_defs_orm_mocks) == 2 
        
        main_proto_orm_mock = next((p for p in discovered_defs_orm_mocks if p.name == "MainIntegrationProtocol"), None)
        nested_proto_orm_mock = next((p for p in discovered_defs_orm_mocks if p.name == "NestedProtocolStep"), None)

        assert main_proto_orm_mock is not None
        assert main_proto_orm_mock.id is not None
        assert nested_proto_orm_mock is not None
        assert nested_proto_orm_mock.id is not None
        
        # Ensure temp_integration_protocols's parent is on sys.path for the import to work in the test
        # The discovery service modifies sys.path temporarily, but for the test to import directly,
        # we need to ensure the path is correct *after* discovery has run and cleaned up.
        # Or, more robustly, re-add it if necessary.
        module_parent_dir = Path(temp_integration_protocols).parent.as_posix()
        if module_parent_dir not in sys.path:
            sys.path.insert(0, module_parent_dir)
            # Schedule cleanup for this path modification if needed, though pytest usually handles test isolation.
            # For this specific test, it might be okay as it's the last part.

        import integration_test_protocols.protocol_module as mod
        
        assert mod.main_protocol._protocol_definition.db_id == main_proto_orm_mock.id
        assert mod.nested_step._protocol_definition.db_id == nested_proto_orm_mock.id
        
        # --- 2. Orchestration Phase ---
        
        mock_protocol_data_service['get_protocol_definition_details'].return_value = main_proto_orm_mock
        # Ensure the mock_orm has a valid file_system_source.base_path for _prepare_protocol_code
        main_proto_orm_mock.file_system_source.base_path = temp_integration_protocols # Orchestrator needs this
        
        orchestrator = Orchestrator(db_session=mock_db_session)
        
        test_run_guid = str(uuid.uuid4())
        mock_protocol_data_service['create_protocol_run'].return_value.run_guid = test_run_guid

        user_params = {"initial_message": "integration_test", "pipette": IntegrationPipette(name="p300_single")}
        initial_state = {"previous_run_count": 5}

        final_run_orm = orchestrator.execute_protocol(
            protocol_name="MainIntegrationProtocol",
            protocol_version="1.1",
            file_system_source_id=1, # This needs to match what _prepare_protocol_code expects
            user_input_params=user_params,
            initial_state_data=initial_state
        )

        assert final_run_orm is not None
        assert final_run_orm.id == mock_protocol_data_service['create_protocol_run'].return_value.id
        
        # --- 3. Verification ---

        mock_protocol_data_service['create_protocol_run'].assert_called_once_with(
            db=mock_db_session,
            run_guid=test_run_guid, 
            top_level_protocol_definition_id=main_proto_orm_mock.id,
            status=ProtocolRunStatusEnum.PREPARING,
            input_parameters_json=json.dumps(user_params, default=lambda o: o.name if isinstance(o, PlrResource) else str(o)), # Simulate basic serialization
            initial_state_json=json.dumps(initial_state)
        )
        
        update_calls = mock_protocol_data_service['update_protocol_run_status'].call_args_list
        assert any(call.kwargs['new_status'] == ProtocolRunStatusEnum.RUNNING for call in update_calls)
        assert any(call.kwargs['new_status'] == ProtocolRunStatusEnum.COMPLETED for call in update_calls)
        
        final_state_json_in_db = json.loads(update_calls[-1].kwargs['final_state_json'])
        assert final_state_json_in_db['main_protocol_started'] == True
        assert final_state_json_in_db['nested_step_ran'] == True
        assert final_state_json_in_db['main_protocol_completed'] == True

        mock_redis_for_state.get.assert_any_call(f"praxis_state:{test_run_guid}")
        assert any(
            call_args[0][0] == f"praxis_state:{test_run_guid}" 
            for call_args in mock_redis_for_state.set.call_args_list
        )
        
        log_start_mock = mock_protocol_data_service['log_function_call_start']
        log_end_mock = mock_protocol_data_service['log_function_call_end']

        assert log_start_mock.call_count == 2 
        assert log_end_mock.call_count == 2

        main_call_start_kwargs = next(c.kwargs for c in log_start_mock.call_args_list if c.kwargs['function_definition_id'] == main_proto_orm_mock.id)
        assert main_call_start_kwargs['protocol_run_orm_id'] == final_run_orm.id
        assert main_call_start_kwargs['parent_function_call_log_id'] is None 
        
        # Get the ID returned by the mock for the main protocol's start log
        main_call_log_id = abs(hash(main_proto_orm_mock.id + 0)) # Based on mock_log_start logic, sequence for first call is 0 if not incremented before.
                                                                    # Let's adjust mock_log_start to use sequence_in_run for hashing to be more robust
                                                                    # Or retrieve it from call object if stored
        main_call_log_entry_mock = next(c.return_value for c in log_start_mock.side_effect_history if c.kwargs['function_definition_id'] == main_proto_orm_mock.id)


        nested_call_start_kwargs = next(c.kwargs for c in log_start_mock.call_args_list if c.kwargs['function_definition_id'] == nested_proto_orm_mock.id)
        assert nested_call_start_kwargs['protocol_run_orm_id'] == final_run_orm.id
        assert nested_call_start_kwargs['parent_function_call_log_id'] == main_call_log_entry_mock.id
        
        final_output = json.loads(update_calls[-1].kwargs['output_data_json'])
        assert final_output['nested_result']['nested_output'] == "FROM_MAIN"

        # Clean up sys.path if modified
        if module_parent_dir in sys.path and module_parent_dir != os.path.dirname(temp_integration_protocols): # Avoid removing if it was there before
             sys.path.remove(module_parent_dir)
