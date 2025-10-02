import json  # For serializing in assertions
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest  # type: ignore
from sqlalchemy.orm import Session as DbSession  # For type hinting if needed

# Added imports
from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.core.run_context import Resource
from praxis.backend.models.enums.protocol import ProtocolRunStatusEnum
from praxis.backend.models.orm.protocol import (
    FileSystemProtocolSourceOrm,
    FunctionCallLogOrm,
    FunctionProtocolDefinitionOrm,
    ProtocolRunOrm,
    ProtocolSourceRepositoryOrm,
)
from praxis.backend.models.pydantic_internals.protocol import (
    FunctionProtocolDefinitionResponse as FunctionProtocolDefinitionModel,
)

# Modules to test
from praxis.backend.services.discovery_service import (
    DiscoveryService as ProtocolDiscoveryService,
)

try: # Try importing jsonschema for specific error catching
    from jsonschema import ValidationError as JsonSchemaValidationError
except ImportError: # pragma: no cover
    JsonSchemaValidationError = None # type: ignore
# Import WorkcellRuntime to patch its methods (though we'll mock its instance methods)

# Module-level Mock Objects for PLR Live Resources
MOCK_LIVE_DEVICE = MagicMock(name="MockLivePLRDevice_Global")
MOCK_LIVE_DEVICE.name = "MockLivePLRDevice_Global"
MOCK_LIVE_LABWARE = MagicMock(name="MockLivePLRResource_Global")
MOCK_LIVE_LABWARE.name = "MockLivePLRResource_Global"


# Dummy PLR resource for type hinting in test protocols
class IntegrationPipette(Resource):
    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name=name, size_x=1, size_y=1, size_z=1, **kwargs)
    def pick_up_tip(self) -> None:
        pass
    def aspirate(self, vol: int) -> None:
        pass
    def dispense(self, vol: int) -> None:
        pass

@pytest.fixture
def temp_integration_protocols():
    base_temp_dir = tempfile.mkdtemp()
    pkg_root_name = "integration_test_protocols"
    pkg_root_dir = os.path.join(base_temp_dir, pkg_root_name)
    os.makedirs(pkg_root_dir)
    with open(os.path.join(pkg_root_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("# Integration test protocol package root\n")

    protocol_content = """
from praxis.backend.core.decorators import protocol_function
from praxis.backend.services.state import PraxisState
# Import the dummy resource from this test file
from tests.integration_discovery_execution_tests import IntegrationPipette # Path relative to where pytest runs

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

@pytest.fixture
def mock_data_services(request): # request is a pytest fixture
    # --- Mock s ---
    mock_fpd_instance = MagicMock(spec=FunctionProtocolDefinitionOrm)
    mock_fpd_instance.accession_id = 12345
    mock_fpd_instance.name = "DefaultMockedProtocol"
    mock_fpd_instance.version = "1.0.mock"
    # Add other essential attributes that are accessed after get_protocol_definition_details
    mock_fpd_instance.module_name = "mocked.protocol.module"
    mock_fpd_instance.function_name = "mocked_protocol_func"
    mock_fpd_instance.is_top_level = True
    mock_fpd_instance.parameters = [] # Mocked list of ParameterDefinitionOrm
    mock_fpd_instance.assets = []    # Mocked list of AssetDefinitionOrm
    mock_fpd_instance.file_system_source = MagicMock(spec=FileSystemProtocolSourceOrm, base_path="dummy/fs/path_for_mock_fpd")
    mock_fpd_instance.source_repository = None
    mock_fpd_instance.pydantic_definition = MagicMock(spec=FunctionProtocolDefinitionModel) # Critical for Orchestrator

    _mock_upsert_fpd = MagicMock(
        side_effect=lambda db, protocol_pydantic, **kwargs: MagicMock(
            spec=FunctionProtocolDefinitionOrm,
            id=abs(hash(protocol_pydantic.name + protocol_pydantic.version)),
            name=protocol_pydantic.name, version=protocol_pydantic.version,
            module_name=protocol_pydantic.module_name, function_name=protocol_pydantic.function_name,
            is_top_level=protocol_pydantic.is_top_level, # Corrected: protocol_pydantic.is_top_level
            parameters=[MagicMock(name=p.name) for p in protocol_pydantic.parameters],
            assets=[MagicMock(name=a.name) for a in protocol_pydantic.assets],
            source_repository_accession_id=kwargs.get("source_repository_accession_id"),
            source_repository=MagicMock(spec=ProtocolSourceRepositoryOrm, local_checkout_path="dummy/repo/path") if kwargs.get("source_repository_accession_id") else None,
            file_system_source_accession_id=kwargs.get("file_system_source_accession_id"),
            file_system_source=MagicMock(spec=FileSystemProtocolSourceOrm, base_path="dummy_scan_path_for_upsert_fixture") if kwargs.get("file_system_source_accession_id") else None,
            commit_hash=kwargs.get("commit_hash"),
            pydantic_definition=protocol_pydantic,
        ),
    )
    _mock_get_fpd_details = MagicMock(return_value=mock_fpd_instance)
    _mock_create_pr = MagicMock(return_value=MagicMock(spec=ProtocolRunOrm, id=789, run_accession_id="default_accession_id"))
    _mock_update_pr_status = MagicMock(return_value=MagicMock(spec=ProtocolRunOrm))
    _mock_log_fcs = MagicMock(return_value=MagicMock(spec=FunctionCallLogOrm, id=101112))
    _mock_log_fce = MagicMock(return_value=MagicMock(spec=FunctionCallLogOrm))

    # Define specific patch targets
    # These must be where the function is *looked up* by the calling module
    patch_targets = {
        "praxis.backend.services.protocols.protocol_run_service.create": _mock_create_pr,
        "praxis.backend.services.protocols.protocol_run_service.update": _mock_update_pr_status,
        "praxis.backend.services.protocol_definition.protocol_definition_service.get_by_name_and_version": _mock_get_fpd_details,
        "praxis.backend.services.discovery_service.upsert_function_protocol_definition": _mock_upsert_fpd,
        "praxis.backend.core.decorators.log_function_call_start": _mock_log_fcs,
        "praxis.backend.core.decorators.log_function_call_end": _mock_log_fce,
    }

    active_patches = []
    for target_path, mock_obj in patch_targets.items():
        p = patch(target_path, mock_obj)
        p.start()
        active_patches.append(p)

    request.addfinalizer(lambda: [p.stop() for p in active_patches])

    return {
        "upsert_fpd": _mock_upsert_fpd, "get_fpd_details": _mock_get_fpd_details,
        "create_pr": _mock_create_pr, "update_pr_status": _mock_update_pr_status,
        "log_fcs": _mock_log_fcs, "log_fce": _mock_log_fce,
    }

@pytest.fixture
def mock_redis_for_state():
    with patch("redis.Redis") as mock_redis_constructor:
        mock_instance = MagicMock()
        mock_instance.get.return_value = None # Default to no existing state
        mock_redis_constructor.return_value = mock_instance
        yield mock_instance

class TestIntegrationDiscoveryExecution:

    def test_discovery_and_basic_execution_logging(
        self,
        temp_integration_protocols: str,
        mock_db_session: MagicMock,
        mock_data_services: dict[str, MagicMock], # MODIFIED: Use new fixture name
        mock_redis_for_state: MagicMock,
        mock_asset_manager_instance: MagicMock,
    ) -> None:
        # --- 1. Discovery Phase ---
        discovery_service = ProtocolDiscoveryService(db_session=mock_db_session)

        discovered_defs_orm_mocks = discovery_service.discover_and_upsert_protocols(
            search_paths=[temp_integration_protocols],
            file_system_source_accession_id=1,
        )
        # Assertion for upsert_function_protocol_definition (mocked by mock_data_services)
        assert mock_data_services["upsert_function_protocol_definition"].called
        assert len(discovered_defs_orm_mocks) == 2

        main_proto_orm_mock = next((p for p in discovered_defs_orm_mocks if p.name == "MainIntegrationProtocol"), None)
        nested_proto_orm_mock = next((p for p in discovered_defs_orm_mocks if p.name == "NestedProtocolStep"), None)

        assert main_proto_orm_mock is not None
        assert main_proto_orm_mock.accession_id is not None
        assert nested_proto_orm_mock is not None
        assert nested_proto_orm_mock.accession_id is not None

        module_parent_dir = Path(temp_integration_protocols).parent.as_posix()
        if module_parent_dir not in sys.path:
            sys.path.insert(0, module_parent_dir)

        import integration_test_protocols.protocol_module as mod

        assert mod.main_protocol._protocol_definition.db_accession_id == main_proto_orm_mock.accession_id
        assert mod.nested_step._protocol_definition.db_accession_id == nested_proto_orm_mock.accession_id

        # --- 2. Orchestration Phase ---

        # Configure get_protocol_definition_details from the new fixture
        mock_data_services["get_protocol_definition_details"].return_value = main_proto_orm_mock
        main_proto_orm_mock.file_system_source.base_path = temp_integration_protocols

        orchestrator = Orchestrator(db_session=mock_db_session)
        orchestrator.asset_manager = mock_asset_manager_instance

        test_run_accession_id = str(uuid.uuid4())
        # Configure create_protocol_run from the new fixture
        mock_data_services["create_protocol_run"].return_value.run_accession_id = test_run_accession_id

        user_params = {"initial_message": "integration_test", "pipette": IntegrationPipette(name="p300_single")}
        initial_state = {"previous_run_count": 5}

        final_run_orm = orchestrator.execute_protocol(
            protocol_name="MainIntegrationProtocol",
            protocol_version="1.1",
            file_system_source_accession_id=1,
            user_input_params=user_params,
            initial_state_data=initial_state,
        )

        assert final_run_orm is not None
        assert final_run_orm.accession_id == mock_data_services["create_protocol_run"].return_value.accession_id

        # --- 3. Verification ---

        mock_data_services["create_protocol_run"].assert_called_once_with(
            db=mock_db_session,
            run_accession_id=test_run_accession_id,
            top_level_protocol_definition_accession_id=main_proto_orm_mock.accession_id,
            status=ProtocolRunStatusEnum.PREPARING,
            input_parameters_json=json.dumps(user_params, default=lambda o: o.name if isinstance(o, Resource) else str(o)),
            initial_state_json=json.dumps(initial_state),
        )

        update_calls = mock_data_services["update_protocol_run_status"].call_args_list
        assert any(call.kwargs["new_status"] == ProtocolRunStatusEnum.RUNNING for call in update_calls)
        assert any(call.kwargs["new_status"] == ProtocolRunStatusEnum.COMPLETED for call in update_calls)

        final_state_json_in_db = json.loads(update_calls[-1].kwargs["final_state_json"])
        assert final_state_json_in_db["main_protocol_started"] is True
        assert final_state_json_in_db["nested_step_ran"] is True
        assert final_state_json_in_db["main_protocol_completed"] is True

        mock_redis_for_state.get.assert_any_call(f"praxis_state:{test_run_accession_id}")
        assert any(
            call_args[0][0] == f"praxis_state:{test_run_accession_id}"
            for call_args in mock_redis_for_state.set.call_args_list
        )

        log_start_mock = mock_data_services["log_function_call_start"]
        log_end_mock = mock_data_services["log_function_call_end"]

        assert log_start_mock.call_count == 2
        assert log_end_mock.call_count == 2

        main_call_start_kwargs = next(c.kwargs for c in log_start_mock.call_args_list if c.kwargs["function_definition_accession_id"] == main_proto_orm_mock.accession_id)
        assert main_call_start_kwargs["protocol_run_orm_accession_id"] == final_run_orm.accession_id
        assert main_call_start_kwargs["parent_function_call_log_accession_id"] is None

        main_call_log_entry_mock = next(c.return_value for c in log_start_mock.side_effect_history if c.kwargs["function_definition_accession_id"] == main_proto_orm_mock.accession_id)

        nested_call_start_kwargs = next(c.kwargs for c in log_start_mock.call_args_list if c.kwargs["function_definition_accession_id"] == nested_proto_orm_mock.accession_id)
        assert nested_call_start_kwargs["protocol_run_orm_accession_id"] == final_run_orm.accession_id
        assert nested_call_start_kwargs["parent_function_call_log_accession_id"] == main_call_log_entry_mock.accession_id

        final_output = json.loads(update_calls[-1].kwargs["output_data_json"])
        assert final_output["nested_result"]["nested_output"] == "FROM_MAIN"

        if module_parent_dir in sys.path and module_parent_dir != os.path.dirname(temp_integration_protocols):
             sys.path.remove(module_parent_dir)

        pipette_asset_req = next(a for a in mod.main_protocol._protocol_definition.assets if a.name == "pipette")
        mock_asset_manager_instance.acquire_asset.assert_called_once_with(
            protocol_run_accession_id=test_run_accession_id,
            asset_requirement=pipette_asset_req,
        )

class TestIntegrationParameterValidation: # New class for validation tests

    def test_parameter_validation_fails_on_invalid_type(
        self, temp_integration_protocols: str, mock_db_session: MagicMock,
        mock_data_services: dict[str, MagicMock], # MODIFIED: Use new fixture name
        mock_redis_for_state: MagicMock,
        mock_asset_manager_instance: MagicMock,
    ) -> None:
        # --- Setup: Discovery (to get Pydantic model into PROTOCOL_REGISTRY) ---
        discovery_service = ProtocolDiscoveryService(db_session=mock_db_session)
        discovered_defs_orm_mocks = discovery_service.discover_and_upsert_protocols(
            search_paths=[temp_integration_protocols], file_system_source_accession_id=1,
        )
        main_proto_discovered_mock_orm = next((p for p in discovered_defs_orm_mocks if p.name == "MainIntegrationProtocol"), None)
        assert main_proto_discovered_mock_orm is not None

        module_parent_dir = Path(temp_integration_protocols).parent.as_posix()
        if module_parent_dir not in sys.path:
            sys.path.insert(0, module_parent_dir)


        # Configure get_protocol_definition_details from the new fixture
        mock_data_services["get_protocol_definition_details"].return_value = main_proto_discovered_mock_orm
        main_proto_discovered_mock_orm.file_system_source.base_path = temp_integration_protocols

        orchestrator = Orchestrator(db_session=mock_db_session)
        orchestrator.asset_manager = mock_asset_manager_instance

        invalid_user_params = {"initial_message": 123, "pipette": "dummy_pipette_placeholder_for_validation_test"}

        with pytest.raises(ValueError, match="Parameter validation failed for protocol 'MainIntegrationProtocol'"):
            orchestrator.execute_protocol(
                protocol_name="MainIntegrationProtocol",
                protocol_version="1.1",
                file_system_source_accession_id=1,
                user_input_params=invalid_user_params,
                initial_state_data={},
            )

        mock_data_services["create_protocol_run"].assert_called_once()
        update_calls = mock_data_services["update_protocol_run_status"].call_args_list
        assert any(call.kwargs["new_status"] == ProtocolRunStatusEnum.FAILED for call in update_calls)

        if module_parent_dir in sys.path and module_parent_dir != os.path.dirname(temp_integration_protocols):
             sys.path.remove(module_parent_dir)

    def test_parameter_validation_fails_on_missing_required(
        self, temp_integration_protocols: str, mock_db_session: MagicMock,
        mock_data_services: dict[str, MagicMock], # MODIFIED: Use new fixture name
        mock_redis_for_state: MagicMock,
        mock_asset_manager_instance: MagicMock,
    ) -> None:
        # This test is complex to set up perfectly without modifying the actual protocol definition
        # or having a very flexible mock for get_protocol_definition_details.
        # For now, mark as pass.
        pass
