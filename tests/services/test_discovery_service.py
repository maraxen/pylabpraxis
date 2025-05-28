# pylint: disable=too-few-public-methods,broad-except,fixme,unused-argument,protected-access,too-many-locals,redefined-outer-name
"""
tests/test_discovery_service.py

Tests for the ProtocolDiscoveryService.
"""
import os
import sys
import shutil
import pytest
from unittest.mock import MagicMock, patch, call

from sqlalchemy.orm import Session as DbSession

from praxis.backend.services.discovery_service import ProtocolDiscoveryService
from praxis.backend.protocol_core.definitions import PROTOCOL_REGISTRY, PlrDeck, PlrResource, PraxisState
from praxis.backend.protocol_core.protocol_definition_models import FunctionProtocolDefinitionModel, ParameterMetadataModel, AssetRequirementModel

# Define a dummy ORM class for mocking upsert_function_protocol_definition
class MockProtocolDefinitionOrm:
    def __init__(self, id_val, name, version, module_name, function_name, parameters=None, assets=None):
        self.id = id_val
        self.name = name
        self.version = version
        self.module_name = module_name
        self.function_name = function_name
        self.parameters = parameters if parameters is not None else []
        self.assets = assets if assets is not None else []

@pytest.fixture(autouse=True)
def clear_protocol_registry_and_sys_modules():
    """Clears the PROTOCOL_REGISTRY and relevant sys.modules before each test."""
    PROTOCOL_REGISTRY.clear()
    # Remove any modules that might have been loaded by previous tests
    # This is important to ensure clean re-importing of test protocol files
    modules_to_remove = [m for m in sys.modules if m.startswith("temp_protocols_test_pkg")]
    for mod_name in modules_to_remove:
        del sys.modules[mod_name]
    yield # Test runs here
    PROTOCOL_REGISTRY.clear()
    modules_to_remove = [m for m in sys.modules if m.startswith("temp_protocols_test_pkg")]
    for mod_name in modules_to_remove:
        del sys.modules[mod_name]


@pytest.fixture
def mock_db_session():
    """Provides a mock SQLAlchemy DbSession."""
    return MagicMock(spec=DbSession)

@pytest.fixture
def temp_protocol_dir(tmp_path_factory):
    """Creates a temporary directory for protocol files and ensures it's in sys.path."""
    # Create a unique base directory for each test run to avoid sys.path conflicts
    # if tests were to run in parallel or if pytest reuses paths.
    base_temp_dir = tmp_path_factory.mktemp("protocol_discovery_tests")

    # This is the directory that will contain our 'temp_protocols_test_pkg'
    # and needs to be in sys.path for imports like 'temp_protocols_test_pkg.module_a'
    # to work.
    package_parent_dir = base_temp_dir

    # Create the actual package directory inside the unique base_temp_dir
    protocols_pkg_dir = package_parent_dir / "temp_protocols_test_pkg"
    protocols_pkg_dir.mkdir()
    (protocols_pkg_dir / "__init__.py").touch() # Make it a package

    original_sys_path = list(sys.path)
    if str(package_parent_dir) not in sys.path:
        sys.path.insert(0, str(package_parent_dir))

    yield protocols_pkg_dir # This is the path to 'temp_protocols_test_pkg'

    # Teardown: remove from sys.path and delete directory
    if str(package_parent_dir) in sys.path:
        sys.path.remove(str(package_parent_dir))
    # tmp_path_factory handles cleanup of base_temp_dir

    # Restore original sys.path to be absolutely sure
    sys.path = original_sys_path


def create_dummy_protocol_file(temp_dir, module_name, content):
    """Helper to create a Python file with protocol content in the temp directory."""
    file_path = temp_dir / f"{module_name}.py"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

@pytest.fixture
def discovery_service(mock_db_session):
    """Provides an instance of ProtocolDiscoveryService with a mock DbSession."""
    return ProtocolDiscoveryService(db_session=mock_db_session)

# --- Test Protocol Contents ---
PROTOCOL_CONTENT_DECORATED = """
from praxis.backend.protocol_core.decorators import protocol_function
from praxis.backend.protocol_core.definitions import PraxisState, PlrDeck, PlrResource
from typing import Optional

@protocol_function(name="MyDecoratedProtocol", version="1.0.0", description="A test protocol.", is_top_level=True)
def decorated_protocol_func(state: PraxisState, deck: PlrDeck, samples: int = 8, comment: Optional[str] = None):
    '''This is a docstring for decorated_protocol_func.'''
    return {"status": "decorated_done", "samples": samples}

@protocol_function(name="AnotherProtocol", version="0.1.0")
def another_func(state: PraxisState, tip_box: PlrResource): # Asset example
    return "another_done"
"""

PROTOCOL_CONTENT_INFERRED = """
from praxis.backend.protocol_core.definitions import PraxisState, PlrDeck, PlrResource
from typing import Optional, List

def inferred_protocol_func(state: PraxisState, data_points: List[float], name: str = "default_inferred"):
    '''Docstring for inferred_protocol_func.'''
    return {"status": "inferred_done", "name": name, "points_sum": sum(data_points)}

def simple_utility_func(a: int, b: int) -> int:
    return a + b
"""

PROTOCOL_CONTENT_IMPORT_ERROR = """
import non_existent_module

def protocol_with_import_error():
    return "should_not_be_discovered"
"""

# --- Tests ---

def test_discover_decorated_protocols(discovery_service, temp_protocol_dir, mock_db_session):
    """Test discovery of functions decorated with @protocol_function."""
    create_dummy_protocol_file(temp_protocol_dir, "decorated_protos", PROTOCOL_CONTENT_DECORATED)

    mock_upsert = MagicMock()
    # Simulate upsert_function_protocol_definition returning a mock ORM object
    mock_upsert.side_effect = [
        MockProtocolDefinitionOrm(id_val=1, name="MyDecoratedProtocol", version="1.0.0", module_name="temp_protocols_test_pkg.decorated_protos", function_name="decorated_protocol_func"),
        MockProtocolDefinitionOrm(id_val=2, name="AnotherProtocol", version="0.1.0", module_name="temp_protocols_test_pkg.decorated_protos", function_name="another_func")
    ]

    with patch("praxis.backend.services.discovery_service.upsert_function_protocol_definition", mock_upsert):
        results = discovery_service.discover_and_upsert_protocols(
            search_paths=[str(temp_protocol_dir)],
            file_system_source_id=1
        )

    assert len(results) == 2
    assert mock_upsert.call_count == 2

    # Check PROTOCOL_REGISTRY for db_id and pydantic_definition db_id update
    reg_entry_decorated = PROTOCOL_REGISTRY.get("MyDecoratedProtocol_v1.0.0")
    assert reg_entry_decorated is not None
    assert reg_entry_decorated.get("db_id") == 1
    assert isinstance(reg_entry_decorated.get("pydantic_definition"), FunctionProtocolDefinitionModel)
    assert reg_entry_decorated.get("pydantic_definition").db_id == 1
    # Check that the _protocol_definition attribute on the function itself was updated
    # Need to re-import to get the actual function object as modified by the decorator and discovery service
    import temp_protocols_test_pkg.decorated_protos
    decorated_func_ref = temp_protocols_test_pkg.decorated_protos.decorated_protocol_func
    assert hasattr(decorated_func_ref, '_protocol_definition')
    assert getattr(decorated_func_ref, '_protocol_definition').db_id == 1


    reg_entry_another = PROTOCOL_REGISTRY.get("AnotherProtocol_v0.1.0")
    assert reg_entry_another is not None
    assert reg_entry_another.get("db_id") == 2
    assert reg_entry_another.get("pydantic_definition").db_id == 2

    # Verify arguments to mock_upsert for the first call (MyDecoratedProtocol)
    args_decorated, _ = mock_upsert.call_args_list[0]
    pydantic_model_decorated = args_decorated[1] # protocol_pydantic is the second arg
    assert pydantic_model_decorated.name == "MyDecoratedProtocol"
    assert pydantic_model_decorated.version == "1.0.0"
    assert pydantic_model_decorated.is_top_level is True
    assert len(pydantic_model_decorated.parameters) == 3 # state, deck, samples, comment
    assert any(p.name == "samples" and p.default_value_repr == "8" for p in pydantic_model_decorated.parameters)
    assert any(p.name == "deck" and p.is_deck_param for p in pydantic_model_decorated.parameters)
    assert pydantic_model_decorated.file_system_source_name == "1"


def test_discover_inferred_protocols(discovery_service, temp_protocol_dir, mock_db_session):
    """Test discovery and metadata inference for non-decorated functions."""
    create_dummy_protocol_file(temp_protocol_dir, "inferred_protos", PROTOCOL_CONTENT_INFERRED)

    mock_upsert = MagicMock(return_value=MockProtocolDefinitionOrm(id_val=10, name="inferred_protocol_func", version="0.0.0-inferred", module_name="temp_protocols_test_pkg.inferred_protos", function_name="inferred_protocol_func"))

    with patch("praxis.backend.services.discovery_service.upsert_function_protocol_definition", mock_upsert):
        results = discovery_service.discover_and_upsert_protocols(
            search_paths=[str(temp_protocol_dir)],
            file_system_source_id=2
        )

    # Expecting inferred_protocol_func and simple_utility_func (if it's treated as inferrable)
    # Based on current logic, all functions are processed.
    assert len(results) == 2 # inferred_protocol_func and simple_utility_func
    assert mock_upsert.call_count == 2

    # Check inferred_protocol_func
    args_inferred, _ = mock_upsert.call_args_list[0] # Assuming it's the first one processed
    pydantic_model_inferred = args_inferred[1]
    if pydantic_model_inferred.name != "inferred_protocol_func": # Order might vary
        args_inferred, _ = mock_upsert.call_args_list[1]
        pydantic_model_inferred = args_inferred[1]

    assert pydantic_model_inferred.name == "inferred_protocol_func"
    assert pydantic_model_inferred.version == "0.0.0-inferred"
    assert pydantic_model_inferred.description == "Docstring for inferred_protocol_func."
    assert len(pydantic_model_inferred.parameters) == 3 # state, data_points, name
    assert any(p.name == "name" and p.default_value_repr == "'default_inferred'" for p in pydantic_model_inferred.parameters)
    assert pydantic_model_inferred.file_system_source_name == "2"

    # Check that simple_utility_func was also processed (as per current discovery logic)
    args_utility, _ = mock_upsert.call_args_list[1] if pydantic_model_inferred.name == "inferred_protocol_func" else mock_upsert.call_args_list[0]
    pydantic_model_utility = args_utility[1]
    assert pydantic_model_utility.name == "simple_utility_func"
    assert pydantic_model_utility.version == "0.0.0-inferred"
    assert len(pydantic_model_utility.parameters) == 2 # a, b


def test_no_protocols_found(discovery_service, temp_protocol_dir, capsys):
    """Test behavior when no protocol files or functions are found."""
    # Create an empty __init__.py to make it a package, but no protocol files
    (temp_protocol_dir / "__init__.py").touch()

    results = discovery_service.discover_and_upsert_protocols(search_paths=[str(temp_protocol_dir)])
    assert len(results) == 0
    captured = capsys.readouterr()
    assert "No protocol definitions found from scan." in captured.out

def test_non_existent_path(discovery_service, capsys):
    """Test behavior with a non-existent search path."""
    non_existent_path = "/path/to/non_existent_dir_for_discovery"
    results = discovery_service.discover_and_upsert_protocols(search_paths=[non_existent_path])
    assert len(results) == 0
    captured = capsys.readouterr()
    assert f"Warning: Search path '{os.path.abspath(non_existent_path)}' is not a directory. Skipping." in captured.out
    assert "No protocol definitions found from scan." in captured.out


def test_module_import_error(discovery_service, temp_protocol_dir, capsys):
    """Test handling of modules that raise an ImportError during discovery."""
    create_dummy_protocol_file(temp_protocol_dir, "error_proto", PROTOCOL_CONTENT_IMPORT_ERROR)

    # Even if a module fails to import, the service should continue and not crash.
    # It won't find protocols in the faulty module.
    results = discovery_service.discover_and_upsert_protocols(search_paths=[str(temp_protocol_dir)])
    assert len(results) == 0 # No valid protocols should be found
    captured = capsys.readouterr()
    assert "Could not import/process module 'temp_protocols_test_pkg.error_proto'" in captured.out
    assert "No module named 'non_existent_module'" in captured.out # The specific import error

def test_db_session_none(capsys):
    """Test behavior when db_session is None."""
    service_no_db = ProtocolDiscoveryService(db_session=None)
    results = service_no_db.discover_and_upsert_protocols(search_paths=["."]) # Path doesn't matter much here
    assert len(results) == 0
    captured = capsys.readouterr()
    assert "ERROR: DB session not provided to ProtocolDiscoveryService. Cannot upsert definitions." in captured.out

def test_source_linkage_passed_to_upsert(discovery_service, temp_protocol_dir):
    """Test that source linkage information is passed to the upsert function."""
    create_dummy_protocol_file(temp_protocol_dir, "linkage_proto", PROTOCOL_CONTENT_DECORATED) # Use decorated for simplicity

    mock_upsert = MagicMock()
    mock_upsert.return_value = MockProtocolDefinitionOrm(id_val=1, name="MyDecoratedProtocol", version="1.0.0", module_name="temp_protocols_test_pkg.linkage_proto", function_name="decorated_protocol_func")


    with patch("praxis.backend.services.discovery_service.upsert_function_protocol_definition", mock_upsert):
        discovery_service.discover_and_upsert_protocols(
            search_paths=[str(temp_protocol_dir)],
            source_repository_id=123,
            commit_hash="abcdef12345"
        )

    assert mock_upsert.call_count > 0 # At least MyDecoratedProtocol
    # Check args of the first relevant call (could be MyDecoratedProtocol or AnotherProtocol)
    found_call = False
    for call_args_tuple in mock_upsert.call_args_list:
        args, kwargs = call_args_tuple
        pydantic_model = args[1] # protocol_pydantic
        if pydantic_model.name == "MyDecoratedProtocol":
            assert kwargs.get("source_repository_id") == 123
            assert kwargs.get("commit_hash") == "abcdef12345"
            assert pydantic_model.source_repository_name == "123" # Check model update
            assert pydantic_model.commit_hash == "abcdef12345"
            found_call = True
            break
    assert found_call

    mock_upsert.reset_mock()
    with patch("praxis.backend.services.discovery_service.upsert_function_protocol_definition", mock_upsert):
         mock_upsert.return_value = MockProtocolDefinitionOrm(id_val=1, name="MyDecoratedProtocol", version="1.0.0", module_name="temp_protocols_test_pkg.linkage_proto", function_name="decorated_protocol_func")
         discovery_service.discover_and_upsert_protocols(
            search_paths=[str(temp_protocol_dir)],
            file_system_source_id=789
        )
    found_call_fs = False
    for call_args_tuple in mock_upsert.call_args_list:
        args, kwargs = call_args_tuple
        pydantic_model = args[1] # protocol_pydantic
        if pydantic_model.name == "MyDecoratedProtocol":
            assert kwargs.get("file_system_source_id") == 789
            assert pydantic_model.file_system_source_name == "789" # Check model update
            found_call_fs = True
            break
    assert found_call_fs


def test_sys_path_management(discovery_service, tmp_path):
    """
    Test that sys.path is correctly modified and restored.
    This is a more direct test of the sys.path logic.
    """
    original_sys_path = list(sys.path)

    # Create a nested structure: base_dir / package_parent / my_protocols / my_module.py
    base_dir = tmp_path / "sys_path_test_base"
    base_dir.mkdir()

    package_parent = base_dir / "package_parent_dir"
    package_parent.mkdir()

    my_protocols_dir = package_parent / "my_protocols_pkg"
    my_protocols_dir.mkdir()
    (my_protocols_dir / "__init__.py").touch()

    protocol_file = my_protocols_dir / "protocol_module.py"
    protocol_file.write_text(
        "def simple_proto(): pass"
    )

    # The search path is 'my_protocols_pkg'
    # The 'package_parent_dir' should be added to sys.path

    # Mock _extract_protocol_definitions_from_paths to just check sys.path
    # when it's called, and then when it would return.

    # Store sys.path state at different points
    sys_path_at_call_start = []
    sys_path_after_addition = []
    sys_path_before_removal = []

    real_os_walk = os.walk

    def mock_os_walk(path, topdown=True, onerror=None, followlinks=False):
        # Capture sys.path state when os.walk would be processing our target path
        if str(my_protocols_dir) in str(path): # Check if we are walking inside my_protocols_dir
            sys_path_after_addition.extend(list(sys.path))
        return real_os_walk(path, topdown, onerror, followlinks)

    with patch('os.walk', mock_os_walk):
        # We don't need to mock upsert for this specific test
        with patch("praxis.backend.services.discovery_service.upsert_function_protocol_definition", MagicMock()):
            sys_path_at_call_start.extend(list(sys.path))
            discovery_service.discover_and_upsert_protocols(search_paths=[str(my_protocols_dir)])
            sys_path_before_removal.extend(list(sys.path)) # After the call, before our fixture's teardown

    assert str(package_parent) not in sys_path_at_call_start
    assert str(package_parent) in sys_path_after_addition

    # After discover_and_upsert_protocols completes, the path should be removed by the method itself
    assert str(package_parent) not in sys_path_before_removal

    # Final check: ensure sys.path is restored to its original state by the fixture + method
    assert sys.path == original_sys_path
