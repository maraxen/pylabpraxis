"""Service layer for Function Data Output management.

This module provides comprehensive CRUD operations and specialized functions for
managing data outputs from protocol function calls, with support for resource
attribution, spatial context, and data visualization.
"""

from functools import partial
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.outputs import (
  FunctionDataOutput as FunctionDataOutput,
  WellDataOutput as WellDataOutput,
  ProtocolRunDataSummary,
)
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

log_data_output_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=ValueError,
  raises=True,
  raises_exception=ValueError,
)


async def read_protocol_run_data_summary(
  db: AsyncSession,
  protocol_run_accession_id: UUID,
) -> ProtocolRunDataSummary:
  """Get a summary of all data outputs for a protocol run.

  Args:
    db: Database session
    protocol_run_accession_id: Protocol run ID

  Returns:
    Protocol run data summary

  """
  total_count_result = await db.execute(
    select(func.count(FunctionDataOutput.accession_id)).filter(
      FunctionDataOutput.protocol_run_accession_id == protocol_run_accession_id,
    ),
  )
  total_data_outputs = total_count_result.scalar()

  data_types_result = await db.execute(
    select(FunctionDataOutput.data_type.distinct()).filter(
      FunctionDataOutput.protocol_run_accession_id == protocol_run_accession_id,
    ),
  )
  data_types = [dt.value for dt in data_types_result.scalars().all()]

  machines_result = await db.execute(
    select(FunctionDataOutput.machine_accession_id.distinct()).filter(
      and_(
        FunctionDataOutput.protocol_run_accession_id == protocol_run_accession_id,
        FunctionDataOutput.machine_accession_id.is_not(None),
      ),
    ),
  )
  machines_used = list(machines_result.scalars().all())  # type: ignore[assignment]

  # Get unique resource
  resource_result = await db.execute(
    select(FunctionDataOutput.resource_accession_id.distinct()).filter(
      and_(
        FunctionDataOutput.protocol_run_accession_id == protocol_run_accession_id,
        FunctionDataOutput.resource_accession_id.is_not(None),
      ),
    ),
  )
  resource_with_data = list(resource_result.scalars().all())  # type: ignore[assignment]

  # Get timeline of data capture (simplified)
  timeline_result = await db.execute(
    select(
      FunctionDataOutput.measurement_timestamp,
      FunctionDataOutput.data_type,
      func.count(FunctionDataOutput.accession_id),
    )
    .filter(
      FunctionDataOutput.protocol_run_accession_id == protocol_run_accession_id,
    )
    .group_by(
      FunctionDataOutput.measurement_timestamp,
      FunctionDataOutput.data_type,
    )
    .order_by(FunctionDataOutput.measurement_timestamp),
  )

  data_timeline = [
    {"timestamp": row[0], "data_type": row[1].value, "count": row[2]}
    for row in timeline_result.all()
  ]

  # Get file attachments
  files_result = await db.execute(
    select(
      FunctionDataOutput.file_path,
      FunctionDataOutput.file_size_bytes,
      FunctionDataOutput.data_type,
    ).filter(
      and_(
        FunctionDataOutput.protocol_run_accession_id == protocol_run_accession_id,
        FunctionDataOutput.file_path.is_not(None),
      ),
    ),
  )

  file_attachments = [
    {"file_path": row[0], "file_size_bytes": row[1], "data_type": row[2].value}
    for row in files_result.all()
  ]

  machines_used: list[UUID] = [m for m in machines_used if m is not None]
  resource_with_data: list[UUID] = [r for r in resource_with_data if r is not None]

  return ProtocolRunDataSummary(
    protocol_run_accession_id=protocol_run_accession_id,
    total_data_outputs=total_data_outputs or 0,
    data_types=data_types,
    machines_used=machines_used,
    resource_with_data=resource_with_data,
    data_timeline=data_timeline,
    file_attachments=file_attachments,
  )
