import pytest # type: ignore
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from praxis.backend.services.discovery_service import ProtocolDiscoveryService
from praxis.backend.protocol_core.protocol_definition_models import FunctionProtocolDefinitionModel
from praxis.backend.core.decorators import protocol_function # To create decorated funcs
from praxis.backend.core.run_context import PraxisState, Resource # For type hints in dummy protocols

# Dummy PLR resource for type hinting in test protocols
class DummyTestPipette(Resource):
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, size_x=1, size_y=1, size_z=1, **kwargs)

@pytest.fixture
def temp_protocol_dir():
    # Create a temporary directory structure for protocol files
    # temp_dir/
    #   protocols_A/
    #     __init__.py
    #     my_protocol_a.py
    #   protocols_B/
    #     __init__.py
    #     my_protocol_b.py
    #     common_utils.py (non-protocol, might have undecorated functions)
    #   __init__.py (making temp_dir a package)

    base_temp_dir = tempfile.mkdtemp()
    # Create a root package directory within the temp system dir, e.g. "test_protocol_pkg"
    # This helps in making imports more realistic if protocols are structured in packages.
    pkg_root_name = "test_protocol_pkg_root"
    pkg_root_dir = os.path.join(base_temp_dir, pkg_root_name)
    os.makedirs(pkg_root_dir)
    with open(os.path.join(pkg_root_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("# Test protocol package root
")

    # protocols_A subdirectory
    dir_a = os.path.join(pkg_root_dir, "protocols_A")
    os.makedirs(dir_a)
    with open(os.path.join(dir_a, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("# Protocols A subpackage
")

    # protocols_B subdirectory
    dir_b = os.path.join(pkg_root_dir, "protocols_B")
    os.makedirs(dir_b)
    with open(os.path.join(dir_b, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("# Protocols B subpackage
")

    # File for decorated protocol
    protocol_a_content = """
from praxis.backend.protocol_core.decorators import protocol_function
from praxis.backend.protocol_core.definitions import PraxisState
# Assuming DummyTestPipette is discoverable or defined here/imported for test
from tests.test_discovery_service import DummyTestPipette # Path relative to where pytest runs

@protocol_function(name="DecoratedProtocolOne", version="1.0", description="Test decorated protocol.")
def decorated_func_one(state: PraxisState, pipette1: DummyTestPipette):
    '''Docstring for decorated_func_one.'''
    print("DecoratedProtocolOne running")
"""
    with open(os.path.join(dir_a, "my_protocol_a.py"), "w", encoding="utf-8") as f:
        f.write(protocol_a_content)

    # File for undecorated protocol and a non-protocol function
    protocol_b_content = """
from praxis.backend.protocol_core.definitions import PraxisState
from tests.test_discovery_service import DummyTestPipette # Path relative to where pytest runs
from typing import Optional

def undecorated_protocol_func(state: PraxisState, count: int, name: Optional[str] = "default"):
    '''Docstring for undecorated_protocol_func.'''
    print(f"Undecorated protocol running with {count} and {name}")

def not_a_protocol_util_func(x: int, y: int) -> int:
    return x + y
"""
    with open(os.path.join(dir_b, "my_protocol_b.py"), "w", encoding="utf-8") as f:
        f.write(protocol_b_content)

    # Path to scan should be the pkg_root_dir, so imports are like test_protocol_pkg_root.protocols_A.my_protocol_a
    yield pkg_root_dir

    shutil.rmtree(base_temp_dir) # Clean up

@pytest.fixture
def discovery_service_mock_db():
    # Mock the database session for ProtocolDiscoveryService
    mock_db_session = MagicMock()
    # Mock ProtocolDataService if it's directly used for complex queries during extraction (not typical)
    # For this step, we primarily care about the extraction output.
    # The upsert part (next plan step) will mock upsert_function_protocol_definition.
    return ProtocolDiscoveryService(db_session=mock_db_session)


class TestProtocolDiscoveryServiceExtraction:

    def test_scan_decorated_function(self, discovery_service_mock_db: ProtocolDiscoveryService, temp_protocol_dir: str):
        # The _extract_protocol_definitions_from_paths expects the path that contains the package root.
        # If temp_protocol_dir is ".../test_protocol_pkg_root", then this is correct.
        # The method itself will try to put its parent on sys.path for import.

        # Add parent of temp_protocol_dir (which is pkg_root_dir) to sys.path to ensure pkg_root_dir itself is importable
        # This mirrors how python might find the top-level package.
        # The _extract_protocol_definitions_from_paths also manipulates sys.path.
        # For robustness, ensure the parent of pkg_root_dir is on path.
        scan_target_path = os.path.join(temp_protocol_dir, "protocols_A") # Scan specific sub-directory

        # Ensure parent of 'test_protocol_pkg_root' is on path for 'import test_protocol_pkg_root....'
        # The discovery service adds `module_root_path` (parent of scan_target_path) to sys.path
        # If scan_target_path = ".../test_protocol_pkg_root/protocols_A"
        # module_root_path = ".../test_protocol_pkg_root" -> this is added to sys.path.
        # So, imports like `test_protocol_pkg_root.protocols_A.my_protocol_a` should work.

        definitions_with_refs = discovery_service_mock_db._extract_protocol_definitions_from_paths(scan_target_path)
        definitions = [d for d, _ in definitions_with_refs]

        assert len(definitions) == 1
        model = definitions[0]
        assert isinstance(model, FunctionProtocolDefinitionModel)
        assert model.name == "DecoratedProtocolOne"
        assert model.version == "1.0"
        assert model.description == "Test decorated protocol."
        assert model.module_name == "test_protocol_pkg_root.protocols_A.my_protocol_a" # Adjusted for package structure
        assert model.function_name == "decorated_func_one"
        assert len(model.parameters) == 1 # state
        assert model.parameters[0].name == "state"
        assert len(model.assets) == 1 # pipette1
        assert model.assets[0].name == "pipette1"
        assert "DummyTestPipette" in model.assets[0].actual_type_str

    def test_scan_undecorated_function(self, discovery_service_mock_db: ProtocolDiscoveryService, temp_protocol_dir: str):
        scan_target_path = os.path.join(temp_protocol_dir, "protocols_B")
        definitions_with_refs = discovery_service_mock_db._extract_protocol_definitions_from_paths(scan_target_path)

        # Expected: undecorated_protocol_func and not_a_protocol_util_func
        # The current _extract logic processes all functions. We might want to filter later.
        assert len(definitions_with_refs) == 2

        model_undecorated = next((d for d, f_ref in definitions_with_refs if f_ref and f_ref.__name__ == "undecorated_protocol_func"), None)
        assert model_undecorated is not None
        assert isinstance(model_undecorated, FunctionProtocolDefinitionModel)
        assert model_undecorated.name == "undecorated_protocol_func"
        assert model_undecorated.version == "0.0.0-inferred"
        assert model_undecorated.description == "Docstring for undecorated_protocol_func."
        assert model_undecorated.module_name == "test_protocol_pkg_root.protocols_B.my_protocol_b"
        assert not model_undecorated.is_top_level

        assert len(model_undecorated.parameters) == 3 # state, count, name
        param_names = {p.name for p in model_undecorated.parameters}
        assert param_names == {"state", "count", "name"}
        count_param = next(p for p in model_undecorated.parameters if p.name == "count")
        assert count_param.actual_type_str == "int"

        model_util = next((d for d, f_ref in definitions_with_refs if f_ref and f_ref.__name__ == "not_a_protocol_util_func"), None)
        assert model_util is not None
        assert model_util.name == "not_a_protocol_util_func"
        assert len(model_util.parameters) == 2 # x, y

    def test_scan_all_finds_both_types(self, discovery_service_mock_db: ProtocolDiscoveryService, temp_protocol_dir: str):
        # Scan the whole package root
        definitions_with_refs = discovery_service_mock_db._extract_protocol_definitions_from_paths(temp_protocol_dir)
        definitions = [d for d, _ in definitions_with_refs]

        # Expect 3 functions to be picked up (decorated_func_one, undecorated_protocol_func, not_a_protocol_util_func)
        assert len(definitions) == 3

        decorated_model = next((d for d in definitions if d.name == "DecoratedProtocolOne"), None)
        undecorated_model = next((d for d in definitions if d.name == "undecorated_protocol_func"), None)

        assert decorated_model is not None
        assert decorated_model.version == "1.0" # Check it's not the inferred one

        assert undecorated_model is not None
        assert undecorated_model.version == "0.0.0-inferred"

    def test_empty_and_non_python_files(self, discovery_service_mock_db: ProtocolDiscoveryService, temp_protocol_dir: str):
        empty_dir = os.path.join(temp_protocol_dir, "empty_dir")
        os.makedirs(empty_dir)
        with open(os.path.join(empty_dir, "data.txt"), "w", encoding="utf-8") as f:
            f.write("not python")

        definitions_with_refs = discovery_service_mock_db._extract_protocol_definitions_from_paths(empty_dir)
        assert len(definitions_with_refs) == 0

    # More tests could include:
    # - Functions with more complex signatures for inference (e.g., various type hints, unions)
    # - Files that raise import errors (ensure graceful handling, already prints warning)
    # - Correctness of source_file_path, module_name, function_name in FunctionProtocolDefinitionModel
    # - Interaction with PROTOCOL_REGISTRY (if _extract_protocol_definitions_from_paths modifies it directly, though current plan is it reads from func._protocol_definition)
