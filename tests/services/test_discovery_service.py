from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.pydantic_internals.protocol import FunctionProtocolDefinitionCreate
from praxis.backend.services.discovery_service import DiscoveryService
from praxis.backend.services.machine_type_definition import MachineTypeDefinitionService
from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.resource_type_definition import ResourceTypeDefinitionService


@pytest.fixture
def mock_db_session_factory():
    session = AsyncMock(spec=AsyncSession)
    factory = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock()))
    return factory

@pytest.fixture
def mock_protocol_service():
    service = AsyncMock(spec=ProtocolDefinitionCRUDService)
    return service

@pytest.fixture
def mock_resource_service():
    service = AsyncMock(spec=ResourceTypeDefinitionService)
    return service

@pytest.fixture
def mock_machine_service():
    service = AsyncMock(spec=MachineTypeDefinitionService)
    return service

@pytest.fixture
def discovery_service(
    mock_db_session_factory,
    mock_protocol_service,
    mock_resource_service,
    mock_machine_service,
):
    return DiscoveryService(
        db_session_factory=mock_db_session_factory,
        protocol_definition_service=mock_protocol_service,
        resource_type_definition_service=mock_resource_service,
        machine_type_definition_service=mock_machine_service,
    )

def test_ensure_path_type(discovery_service, tmp_path):
    # Valid paths
    p1 = tmp_path / "p1"
    p1.mkdir()
    p2 = tmp_path / "p2"
    p2.mkdir()

    paths = discovery_service._ensure_path_type([str(p1), p2])
    assert len(paths) == 2
    assert paths[0] == p1
    assert paths[1] == p2

    # Invalid path
    paths = discovery_service._ensure_path_type(["/non/existent/path"])
    assert len(paths) == 0

@pytest.mark.asyncio
async def test_discover_and_sync_all_definitions(discovery_service):
    with patch.object(discovery_service, "discover_and_upsert_protocols", new_callable=AsyncMock) as mock_upsert:
        await discovery_service.discover_and_sync_all_definitions(
            protocol_search_paths=["/tmp"],
        )

        discovery_service.resource_type_definition_service.discover_and_synchronize_type_definitions.assert_called_once()
        discovery_service.machine_type_definition_service.discover_and_synchronize_type_definitions.assert_called_once()
        mock_upsert.assert_called_once()

@pytest.mark.asyncio
async def test_discover_and_upsert_protocols(discovery_service, mock_protocol_service, mock_db_session_factory):
    # Mock extraction
    mock_def = FunctionProtocolDefinitionCreate(
        name="test_func",
        fqn="test.module.test_func",
        source_file_path="/test.py",
        module_name="test.module",
        function_name="test_func",
    )
    mock_func = MagicMock()

    with patch.object(discovery_service, "_extract_protocol_definitions_from_paths", return_value=[(mock_def, mock_func)]):
        # Mock get_by_fqn returning None (create)
        mock_protocol_service.get_by_fqn.return_value = None
        mock_protocol_service.create.return_value = MagicMock(accession_id="123")

        await discovery_service.discover_and_upsert_protocols(search_paths=["/tmp"])

        mock_protocol_service.get_by_fqn.assert_called_once()
        mock_protocol_service.create.assert_called_once()
        mock_protocol_service.update.assert_not_called()

@pytest.mark.asyncio
async def test_discover_and_upsert_protocols_update(discovery_service, mock_protocol_service, mock_db_session_factory):
    # Mock extraction
    mock_def = FunctionProtocolDefinitionCreate(
        name="test_func",
        fqn="test.module.test_func",
        source_file_path="/test.py",
        module_name="test.module",
        function_name="test_func",
    )
    mock_func = MagicMock()

    with patch.object(discovery_service, "_extract_protocol_definitions_from_paths", return_value=[(mock_def, mock_func)]):
        # Mock get_by_fqn returning existing (update)
        mock_protocol_service.get_by_fqn.return_value = MagicMock()
        mock_protocol_service.update.return_value = MagicMock(accession_id="123")

        await discovery_service.discover_and_upsert_protocols(search_paths=["/tmp"])

        mock_protocol_service.get_by_fqn.assert_called_once()
        mock_protocol_service.create.assert_not_called()
        mock_protocol_service.update.assert_called_once()

def test_extract_protocol_definitions_integration(discovery_service, tmp_path):
    """Integration test for extraction logic."""
    # Create a dummy protocol file
    pkg_dir = tmp_path / "my_protocols"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").touch()

    protocol_file = pkg_dir / "proto.py"
    protocol_content = """
def my_protocol(volume: float):
    '''A test protocol.'''
    pass

def not_a_protocol():
    pass
"""
    protocol_file.write_text(protocol_content)

    # Run extraction
    # We need to handle import issues. The logic modifies sys.path so it should work if we point to tmp_path (parent of my_protocols) or pkg_dir?
    # Logic says: "potential_package_parent = abs_path_item.parent".
    # If pass pkg_dir, parent is tmp_path. tmp_path added to sys.path.
    # Then it walks pkg_dir. proto.py is found. Rel path is "proto.py"?
    # Wait, rel path to potential_package_parent.
    # If search_path is pkg_dir, parent is tmp_path.
    # rel_path of pkg_dir/proto.py to tmp_path is "my_protocols/proto.py".
    # Module name: "my_protocols.proto". This matches importlib expectation.

    definitions = discovery_service._extract_protocol_definitions_from_paths([pkg_dir])

    # Should find my_protocol and not_a_protocol?
    # It inspects all functions.
    # my_protocol has type hint, so it might be inferred.
    # not_a_protocol has no type hints. Logic:
    # sig.parameters.items()...
    # inferred_model created.

    # Assert we found something
    found_names = [d[0].name for d in definitions]
    assert "my_protocol" in found_names
    assert "not_a_protocol" in found_names

    # Check my_protocol metadata
    proto_def = next(d[0] for d in definitions if d[0].name == "my_protocol")
    assert proto_def.description == "A test protocol."
    assert len(proto_def.parameters) == 1
    assert proto_def.parameters[0].name == "volume"
