"""Tests for plate parsing service."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models import ResourceDefinitionOrm
from praxis.backend.services.plate_parsing import (
    calculate_well_index,
    parse_well_name,
    read_plate_dimensions,
)


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_read_plate_dimensions_from_num_items(mock_db_session: AsyncMock) -> None:
    """Test reading dimensions from num_items_x/y."""
    resource_def = ResourceDefinitionOrm(
        name="test_plate",
        fqn="test.plate",
        plr_definition_details_json={"num_items_x": 12, "num_items_y": 8},
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = resource_def
    mock_db_session.execute.return_value = mock_result

    dims = await read_plate_dimensions(mock_db_session, uuid.uuid4())
    assert dims == {"rows": 8, "columns": 12}


@pytest.mark.asyncio
async def test_read_plate_dimensions_from_rows_cols(mock_db_session: AsyncMock) -> None:
    """Test reading dimensions from rows/columns in details."""
    resource_def = ResourceDefinitionOrm(
        name="test_plate",
        fqn="test.plate",
        plr_definition_details_json={"rows": 4, "columns": 6},
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = resource_def
    mock_db_session.execute.return_value = mock_result

    dims = await read_plate_dimensions(mock_db_session, uuid.uuid4())
    assert dims == {"rows": 4, "columns": 6}


@pytest.mark.asyncio
async def test_read_plate_dimensions_from_wells(mock_db_session: AsyncMock) -> None:
    """Test reading dimensions from wells layout."""
    resource_def = ResourceDefinitionOrm(
        name="test_plate",
        fqn="test.plate",
        plr_definition_details_json={
            "wells": {
                "A1": {},
                "C4": {},  # Max row C (2), max col 4 (3) -> 3 rows, 4 cols? No, 1-based.
                           # C is index 2, so 3 rows. 4 is index 3, so 4 cols.
                           # Wait, A1 is 0,0. C4 is 2,3.
                           # Dimensions should be max_idx + 1.
                           # So rows=3, columns=4.
            }
        },
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = resource_def
    mock_db_session.execute.return_value = mock_result

    dims = await read_plate_dimensions(mock_db_session, uuid.uuid4())
    assert dims == {"rows": 3, "columns": 4}


@pytest.mark.asyncio
async def test_read_plate_dimensions_fallback_name(mock_db_session: AsyncMock) -> None:
    """Test reading dimensions from name fallback."""
    resource_def = ResourceDefinitionOrm(
        name="Costar 96 Well Plate",
        fqn="test.plate",
        plr_definition_details_json={},
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = resource_def
    mock_db_session.execute.return_value = mock_result

    dims = await read_plate_dimensions(mock_db_session, uuid.uuid4())
    assert dims == {"rows": 8, "columns": 12}

    resource_def.name = "384 Well Plate"
    dims = await read_plate_dimensions(mock_db_session, uuid.uuid4())
    assert dims == {"rows": 16, "columns": 24}


@pytest.mark.asyncio
async def test_read_plate_dimensions_not_found(mock_db_session: AsyncMock) -> None:
    """Test reading dimensions when resource definition is not found."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    dims = await read_plate_dimensions(mock_db_session, uuid.uuid4())
    assert dims is None


def test_parse_well_name() -> None:
    """Test well name parsing."""
    assert parse_well_name("A1") == (0, 0)
    assert parse_well_name("B2") == (1, 1)
    assert parse_well_name("H12") == (7, 11)

    # Current implementation only supports single-letter rows
    with pytest.raises(ValueError):
        parse_well_name("AA1")

    with pytest.raises(ValueError, match="Invalid well name"):
        parse_well_name("")

    with pytest.raises(ValueError, match="Invalid row letter"):
        parse_well_name("11")

    with pytest.raises(ValueError, match="Invalid column number"):
        parse_well_name("AX")


def test_calculate_well_index() -> None:
    """Test linear well index calculation."""
    # 96 well plate (8x12)
    assert calculate_well_index(0, 0, 12) == 0  # A1
    assert calculate_well_index(0, 11, 12) == 11 # A12
    assert calculate_well_index(1, 0, 12) == 12 # B1
    assert calculate_well_index(7, 11, 12) == 95 # H12
