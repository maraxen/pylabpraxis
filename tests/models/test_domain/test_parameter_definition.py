"""Unit tests for ParameterDefinitionOrm model."""
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.protocol import (
    FunctionProtocolDefinitionOrm,
    ParameterDefinitionOrm,
)


@pytest_asyncio.fixture
async def protocol_definition(db_session: AsyncSession) -> FunctionProtocolDefinitionOrm:
    """Create a FunctionProtocolDefinitionOrm for testing."""
    protocol = FunctionProtocolDefinitionOrm(
        name="test_protocol",
        fqn="test.protocols.test_protocol",
        version="1.0.0",
        source_file_path="protocols/test_protocol.py",
        module_name="test.protocols",
        function_name="test_protocol",
    )
    db_session.add(protocol)
    await db_session.flush()
    return protocol


@pytest.mark.asyncio
async def test_parameter_definition_orm_creation_minimal(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test creating ParameterDefinitionOrm with minimal required fields."""
    param = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
    )
    db_session.add(param)
    await db_session.flush()

    # Verify creation with defaults
    assert param.accession_id is not None
    assert param.protocol_definition_accession_id == protocol_definition.accession_id
    assert param.name == ""  # Default
    assert param.type_hint == ""  # Default
    assert param.fqn == ""  # Default
    assert param.is_deck_param is False  # Default
    assert param.optional is False  # Default
    assert param.default_value_repr is None
    assert param.description is None
    assert param.constraints_json is None
    assert param.ui_hint_json is None


@pytest.mark.asyncio
async def test_parameter_definition_orm_creation_with_all_fields(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test creating ParameterDefinitionOrm with all fields populated."""
    constraints = {"min_value": 0, "max_value": 100}
    ui_hint = {"widget_type": "slider"}

    param = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="volume",
        type_hint="int",
        fqn="test.protocols.test_protocol.volume",
        is_deck_param=False,
        optional=True,
        default_value_repr="50",
        description="Volume in microliters",
        constraints_json=constraints,
        ui_hint_json=ui_hint,
    )
    db_session.add(param)
    await db_session.flush()

    # Verify all fields
    assert param.accession_id is not None
    assert param.protocol_definition_accession_id == protocol_definition.accession_id
    assert param.name == "volume"
    assert param.type_hint == "int"
    assert param.fqn == "test.protocols.test_protocol.volume"
    assert param.is_deck_param is False
    assert param.optional is True
    assert param.default_value_repr == "50"
    assert param.description == "Volume in microliters"
    assert param.constraints_json == constraints
    assert param.ui_hint_json == ui_hint


@pytest.mark.asyncio
async def test_parameter_definition_orm_persist_to_database(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test full persistence cycle for ParameterDefinitionOrm."""
    param = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="temperature",
        type_hint="float",
        fqn="test.protocols.test_protocol.temperature",
        optional=False,
        description="Temperature in Celsius",
    )
    db_session.add(param)
    await db_session.flush()

    # Query back
    result = await db_session.execute(
        select(ParameterDefinitionOrm).where(
            ParameterDefinitionOrm.accession_id == param.accession_id,
        ),
    )
    retrieved = result.scalars().first()

    # Verify persistence
    assert retrieved is not None
    assert retrieved.accession_id == param.accession_id
    assert retrieved.name == "temperature"
    assert retrieved.type_hint == "float"
    assert retrieved.fqn == "test.protocols.test_protocol.temperature"
    assert retrieved.optional is False
    assert retrieved.description == "Temperature in Celsius"


@pytest.mark.asyncio
async def test_parameter_definition_orm_unique_constraint(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test unique constraint on (protocol_definition_accession_id, name)."""
    # Create first parameter
    param1 = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="unique_param",
        type_hint="str",
        fqn="test.protocols.test_protocol.unique_param",
    )
    db_session.add(param1)
    await db_session.flush()

    # Try to create another with same protocol and name
    param2 = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="unique_param",  # Duplicate name for same protocol
        type_hint="int",
        fqn="test.protocols.test_protocol.unique_param_2",
    )
    db_session.add(param2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_parameter_definition_orm_deck_param_flag(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test is_deck_param flag for deck parameters."""
    # Regular parameter (not deck)
    regular_param = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="regular_param",
        type_hint="str",
        fqn="test.protocols.test_protocol.regular_param",
        is_deck_param=False,
    )
    db_session.add(regular_param)
    await db_session.flush()
    assert regular_param.is_deck_param is False

    # Deck parameter
    deck_param = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="deck",
        type_hint="Deck",
        fqn="test.protocols.test_protocol.deck",
        is_deck_param=True,
    )
    db_session.add(deck_param)
    await db_session.flush()
    assert deck_param.is_deck_param is True


@pytest.mark.asyncio
async def test_parameter_definition_orm_optional_flag(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test optional flag for parameters."""
    # Required parameter
    required_param = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="required_param",
        type_hint="str",
        fqn="test.protocols.test_protocol.required_param",
        optional=False,
    )
    db_session.add(required_param)
    await db_session.flush()
    assert required_param.optional is False

    # Optional parameter with default
    optional_param = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="optional_param",
        type_hint="str",
        fqn="test.protocols.test_protocol.optional_param",
        optional=True,
        default_value_repr="'default_value'",
    )
    db_session.add(optional_param)
    await db_session.flush()
    assert optional_param.optional is True
    assert optional_param.default_value_repr == "'default_value'"


@pytest.mark.asyncio
async def test_parameter_definition_orm_jsonb_constraints(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test JSONB constraints field for parameter validation rules."""
    constraints = {
        "min_value": 0,
        "max_value": 100,
        "regex_pattern": "^[A-Z]+$",
        "options": ["A", "B", "C"],
    }

    param = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="constrained_param",
        type_hint="str",
        fqn="test.protocols.test_protocol.constrained_param",
        constraints_json=constraints,
    )
    db_session.add(param)
    await db_session.flush()

    # Verify JSONB storage and retrieval
    assert param.constraints_json == constraints
    assert param.constraints_json["min_value"] == 0
    assert param.constraints_json["options"] == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_parameter_definition_orm_jsonb_ui_hint(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test JSONB ui_hint field for UI rendering hints."""
    ui_hint = {
        "widget_type": "slider",
        "step": 5,
        "show_value": True,
    }

    param = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="ui_param",
        type_hint="int",
        fqn="test.protocols.test_protocol.ui_param",
        ui_hint_json=ui_hint,
    )
    db_session.add(param)
    await db_session.flush()

    # Verify JSONB storage and retrieval
    assert param.ui_hint_json == ui_hint
    assert param.ui_hint_json["widget_type"] == "slider"
    assert param.ui_hint_json["step"] == 5


@pytest.mark.asyncio
async def test_parameter_definition_orm_relationship_to_protocol(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test relationship between ParameterDefinitionOrm and FunctionProtocolDefinitionOrm."""
    # Create multiple parameters for the same protocol
    param1 = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="param1",
        type_hint="str",
        fqn="test.protocols.test_protocol.param1",
    )

    param2 = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="param2",
        type_hint="int",
        fqn="test.protocols.test_protocol.param2",
    )

    db_session.add(param1)
    db_session.add(param2)
    await db_session.flush()

    # Query protocol and check parameters relationship
    result = await db_session.execute(
        select(FunctionProtocolDefinitionOrm).where(
            FunctionProtocolDefinitionOrm.accession_id == protocol_definition.accession_id,
        ),
    )
    protocol = result.scalars().first()

    # Verify bidirectional relationship
    assert len(protocol.parameters) >= 2
    param_names = [p.name for p in protocol.parameters]
    assert "param1" in param_names
    assert "param2" in param_names


@pytest.mark.asyncio
async def test_parameter_definition_orm_query_by_protocol(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test querying parameters by protocol definition."""
    # Create parameters for this protocol
    param1 = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="query_param1",
        type_hint="str",
        fqn="test.protocols.test_protocol.query_param1",
    )

    param2 = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="query_param2",
        type_hint="int",
        fqn="test.protocols.test_protocol.query_param2",
    )

    db_session.add(param1)
    db_session.add(param2)
    await db_session.flush()

    # Query all parameters for this protocol
    result = await db_session.execute(
        select(ParameterDefinitionOrm).where(
            ParameterDefinitionOrm.protocol_definition_accession_id
            == protocol_definition.accession_id,
        ),
    )
    parameters = result.scalars().all()

    # Should find at least our 2 parameters
    assert len(parameters) >= 2
    param_names = [p.name for p in parameters]
    assert "query_param1" in param_names
    assert "query_param2" in param_names


@pytest.mark.asyncio
async def test_parameter_definition_orm_repr(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> None:
    """Test string representation of ParameterDefinitionOrm."""
    param = ParameterDefinitionOrm(
        protocol_definition_accession_id=protocol_definition.accession_id,
        protocol_definition=protocol_definition,
        name="repr_param",
        type_hint="str",
        fqn="test.protocols.test_protocol.repr_param",
    )

    repr_str = repr(param)
    assert "ParameterDefinitionOrm" in repr_str
    assert "repr_param" in repr_str
    assert str(protocol_definition.accession_id) in repr_str
