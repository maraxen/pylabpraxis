"""Service layer for Function Data Output management.

This module provides comprehensive CRUD operations and specialized functions for
managing data outputs from protocol function calls, with support for resource
attribution, spatial context, and data visualization.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.resource import (
  Resource as Resource,
)
from praxis.backend.models.domain.resource import (
  ResourceDefinition as ResourceDefinition,
)


async def read_plate_dimensions(
  db: AsyncSession,
  plate_resource_accession_id: UUID,
) -> dict[str, int] | None:
  """Get plate dimensions from the resource definition.

  Args:
    db: Database session
    plate_resource_accession_id: Plate resource instance ID

  Returns:
    Dictionary with 'rows' and 'columns' keys, or None if not found

  """
  # Get the resource instance and its definition
  result = await db.execute(
    select(ResourceDefinition)
    .join(Resource)
    .filter(Resource.accession_id == plate_resource_accession_id),
  )

  resource_def = result.scalar_one_or_none()

  if not resource_def:
    return None

  # Check for plate dimensions in plr_definition_details_json
  if resource_def.plr_definition_details_json:
    details = resource_def.plr_definition_details_json

    # Look for various possible dimension keys
    if "num_items_x" in details and "num_items_y" in details:
      return {"rows": details["num_items_y"], "columns": details["num_items_x"]}

    if "rows" in details and "columns" in details:
      return {"rows": details["rows"], "columns": details["columns"]}

    # Check for well layout in details
    if "wells" in details and isinstance(details["wells"], dict):
      # Extract dimensions from well names
      well_names = list(details["wells"].keys())
      if well_names:
        max_row = 0
        max_col = 0
        for well_name in well_names:
          try:
            row_idx, col_idx = parse_well_name(well_name)
            max_row = max(max_row, row_idx)
            max_col = max(max_col, col_idx)
          except ValueError:
            continue

        if max_row > 0 or max_col > 0:
          return {"rows": max_row + 1, "columns": max_col + 1}

  # Fallback: try to infer from resource name or category
  resource_name = resource_def.name.lower()

  # Common plate formats
  if "96" in resource_name:
    return {"rows": 8, "columns": 12}
  if "384" in resource_name:
    return {"rows": 16, "columns": 24}
  if "1536" in resource_name:
    return {"rows": 32, "columns": 48}
  if "24" in resource_name:
    return {"rows": 4, "columns": 6}
  if "48" in resource_name:
    return {"rows": 6, "columns": 8}

  # Default fallback
  return None


MIN_WELL_NAME_LENGTH = 2


def parse_well_name(well_name: str) -> tuple[int, int]:
  """Parse well name (e.g., 'A1') to row/column indices.

  Args:
    well_name: Well name like 'A1', 'H12', etc.

  Returns:
    Tuple of (row_index, column_index)

  Raises:
    ValueError: If well name format is invalid

  """
  if not well_name or len(well_name) < MIN_WELL_NAME_LENGTH:
    msg = f"Invalid well name: {well_name}"
    raise ValueError(msg)

  # Parse row (letter)
  row_letter = well_name[0].upper()
  if not row_letter.isalpha():
    msg = f"Invalid row letter in well name: {well_name}"
    raise ValueError(msg)

  row_idx = ord(row_letter) - ord("A")

  # Parse column (number)
  try:
    col_num = int(well_name[1:])
    col_idx = col_num - 1  # Convert to 0-based
  except ValueError as e:
    msg = f"Invalid column number in well name: {well_name}"
    raise ValueError(msg) from e

  return row_idx, col_idx


def calculate_well_index(row_idx: int, col_idx: int, num_columns: int) -> int:
  """Calculate linear well index from row/column indices.

  Args:
    row_idx: 0-based row index
    col_idx: 0-based column index
    num_columns: Number of columns in the plate

  Returns:
    Linear well index (0-based)

  """
  return row_idx * num_columns + col_idx
