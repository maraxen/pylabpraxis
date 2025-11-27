from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

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


def test_extract_protocol_definitions_from_paths(discovery_service, tmp_path):
    """Test that protocol definitions are extracted from paths."""
    protocol_dir = tmp_path / "my_protocols"
    protocol_dir.mkdir()
    (protocol_dir / "__init__.py").touch()

    protocol_file = protocol_dir / "proto.py"
    protocol_content = """
def my_protocol(volume: float):
    '''A test protocol.'''
    pass
"""
    protocol_file.write_text(protocol_content)

    definitions = discovery_service._extract_protocol_definitions_from_paths([protocol_dir])
    assert len(definitions) == 1
    assert definitions[0]["name"] == "my_protocol"
    assert definitions[0]["description"] == "A test protocol."
    assert len(definitions[0]["parameters"]) == 1
    assert definitions[0]["parameters"][0]["name"] == "volume"
    assert definitions[0]["parameters"][0]["type_hint"] == "float"


def test_extract_protocol_definitions_with_complex_signature(discovery_service, tmp_path):
    """Test that protocol definitions are extracted from a complex signature."""
    protocol_dir = tmp_path / "my_protocols"
    protocol_dir.mkdir()
    (protocol_dir / "__init__.py").touch()

    protocol_file = protocol_dir / "proto.py"
    protocol_content = """
from typing import Optional
def my_protocol(
    a: int,
    b: str = "hello",
    c: Optional[float] = None,
):
    pass
"""
    protocol_file.write_text(protocol_content)

    definitions = discovery_service._extract_protocol_definitions_from_paths([protocol_dir])
    assert len(definitions) == 1
    assert definitions[0]["name"] == "my_protocol"
    parameters = definitions[0]["parameters"]
    assert len(parameters) == 3
    assert parameters[0]["name"] == "a"
    assert parameters[0]["type_hint"] == "int"
    assert not parameters[0]["optional"]
    assert parameters[1]["name"] == "b"
    assert parameters[1]["type_hint"] == "str"
    assert parameters[1]["optional"]
    assert parameters[1]["default_value_repr"] == "'hello'"
    assert parameters[2]["name"] == "c"
    assert parameters[2]["type_hint"] == "Optional[float]"
    assert parameters[2]["optional"]
    assert parameters[2]["default_value_repr"] == "None"


def test_extract_protocol_definitions_with_pylabrobot_resource(discovery_service, tmp_path):
    """Test that pylabrobot resources are correctly identified as assets."""
    protocol_dir = tmp_path / "my_protocols"
    protocol_dir.mkdir()
    (protocol_dir / "__init__.py").touch()

    protocol_file = protocol_dir / "proto.py"
    protocol_content = """
from pylabrobot.resources import Plate
def my_protocol(plate: Plate):
    pass
"""
    protocol_file.write_text(protocol_content)

    definitions = discovery_service._extract_protocol_definitions_from_paths([protocol_dir])
    assert len(definitions) == 1
    assert definitions[0]["name"] == "my_protocol"
    assets = definitions[0]["assets"]
    assert len(assets) == 1
    assert assets[0]["name"] == "plate"
    assert assets[0]["type_hint"] == "Plate"


def test_extract_protocol_definitions_with_invalid_syntax(discovery_service, tmp_path):
    """Test that protocol definitions are not extracted from a file with invalid syntax."""
    protocol_dir = tmp_path / "my_protocols"
    protocol_dir.mkdir()
    (protocol_dir / "__init__.py").touch()

    protocol_file = protocol_dir / "proto.py"
    protocol_content = """
def my_protocol()
    pass
"""
    protocol_file.write_text(protocol_content)

    definitions = discovery_service._extract_protocol_definitions_from_paths([protocol_dir])
    assert len(definitions) == 0
