"""Service layer for Function Data Output management.

praxis.backend.services.plate_viz

This module provides comprehensive CRUD operations and specialized functions for
managing data outputs from protocol function calls, with support for resource
attribution, spatial context, and data visualization.
"""

from functools import partial
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.outputs import (
  FunctionDataOutput,
)
from praxis.backend.models.domain.outputs import (
  PlateDataVisualization,
)
from praxis.backend.models.domain.outputs import (
  WellDataOutput,
)
from praxis.backend.models.enums import DataOutputTypeEnum
from praxis.backend.services.resource import resource_service
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

log_data_output_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=ValueError,
  raises=True,
  raises_exception=ValueError,
)


async def read_plate_data_visualization(
  db: AsyncSession,
  plate_resource_accession_id: UUID,
  data_type: DataOutputTypeEnum,
  protocol_run_accession_id: UUID | None = None,
  function_call_log_accession_id: UUID | None = None,
) -> PlateDataVisualization | None:
  """Get plate data formatted for visualization.

  Args:
      db: Database session
      plate_resource_accession_id: Plate resource ID
      data_type: Type of data to visualize
      protocol_run_accession_id: Optional protocol run filter
      function_call_log_accession_id: Optional function call filter

  Returns:
      Plate data visualization model or None if no data found

  """
  # Build query for well data
  query = (
    select(WellDataOutput)
    .join(FunctionDataOutput)
    .filter(
      and_(
        WellDataOutput.plate_resource_accession_id == plate_resource_accession_id,
        FunctionDataOutput.data_type == data_type,
      ),
    )
  )

  if protocol_run_accession_id:
    query = query.filter(
      FunctionDataOutput.protocol_run_accession_id == protocol_run_accession_id,
    )

  if function_call_log_accession_id:
    query = query.filter(
      FunctionDataOutput.function_call_log_accession_id == function_call_log_accession_id,
    )

  query = query.order_by(FunctionDataOutput.measurement_timestamp.desc())

  result = await db.execute(query)
  well_data_list = list(result.scalars().all())

  if not well_data_list:
    return None

  # Get plate information
  resource = await resource_service.get(db, plate_resource_accession_id)
  plate_layout = {"rows": 8, "columns": 12, "total_wells": 96, "format": "96-well"}

  if resource and resource.resource_definition and resource.resource_definition.properties_json:
    try:
      # Safely extract dimensions from resource definition metadata
      metadata = resource.resource_definition.properties_json
      num_items_x = metadata.get("num_items_x")
      num_items_y = metadata.get("num_items_y")

      if num_items_x and num_items_y:
        plate_layout = {
          "rows": num_items_y,
          "columns": num_items_x,
          "total_wells": num_items_x * num_items_y,
          "format": f"{num_items_x * num_items_y}-well",
        }
    except (AttributeError, KeyError) as e:
      logger.warning(
        "Could not parse plate geometry from resource definition for plate "
        f"{plate_resource_accession_id}. Error: {e}",
      )

  # Calculate data range for visualization scaling
  values = [wd.data_value for wd in well_data_list if wd.data_value is not None]
  data_range = {
    "min": float(min(values)) if values else 0.0,
    "max": float(max(values)) if values else 1.0,
  }

  # Get measurement timestamp (from most recent)
  measurement_timestamp = well_data_list[0].function_data_output.measurement_timestamp

  return PlateDataVisualization(
    plate_resource_accession_id=plate_resource_accession_id,
    plate_name=f"Plate_{plate_resource_accession_id}",
    data_type=data_type,
    measurement_timestamp=measurement_timestamp,
    well_data=[],  # Convert to response models
    plate_layout=plate_layout,
    data_range=data_range,
    units=None,  # Get from data output if available
  )
