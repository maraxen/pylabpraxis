"""Service layer for Function Data Output management.

This module provides comprehensive CRUD operations and specialized functions for
managing data outputs from protocol function calls, with support for resource
attribution, spatial context, and data visualization.
"""

from functools import partial
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.pydantic.outputs import ProtocolRunDataSummary
from praxis.backend.models.orm.outputs import (
  FunctionDataOutputOrm,
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
  # Count total data outputs
  total_count_result = await db.execute(
    select(func.count(FunctionDataOutputOrm.accession_id)).filter(
      FunctionDataOutputOrm.protocol_run_accession_id == protocol_run_accession_id,
    ),
  )
  total_data_outputs = total_count_result.scalar()

  # Get unique data types
  data_types_result = await db.execute(
    select(FunctionDataOutputOrm.data_type.distinct()).filter(
      FunctionDataOutputOrm.protocol_run_accession_id == protocol_run_accession_id,
    ),
  )
  data_types = [dt.value for dt in data_types_result.scalars().all()]

  # Get unique machines
  machines_result = await db.execute(
    select(FunctionDataOutputOrm.machine_accession_id.distinct()).filter(
      and_(
        FunctionDataOutputOrm.protocol_run_accession_id == protocol_run_accession_id,
        FunctionDataOutputOrm.machine_accession_id.is_not(None),
      ),
    ),
  )
  machines_used = list(machines_result.scalars().all())

  # Get unique resource
  resource_result = await db.execute(
    select(FunctionDataOutputOrm.resource_accession_id.distinct()).filter(
      and_(
        FunctionDataOutputOrm.protocol_run_accession_id == protocol_run_accession_id,
        FunctionDataOutputOrm.resource_accession_id.is_not(None),
      ),
    ),
  )
  resource_with_data = list(resource_result.scalars().all())

  # Get timeline of data capture (simplified)
  timeline_result = await db.execute(
    select(
      FunctionDataOutputOrm.measurement_timestamp,
      FunctionDataOutputOrm.data_type,
      func.count(FunctionDataOutputOrm.accession_id),
    )
    .filter(
      FunctionDataOutputOrm.protocol_run_accession_id == protocol_run_accession_id,
    )
    .group_by(
      FunctionDataOutputOrm.measurement_timestamp,
      FunctionDataOutputOrm.data_type,
    )
    .order_by(FunctionDataOutputOrm.measurement_timestamp),
  )

  data_timeline = [
    {"timestamp": row[0], "data_type": row[1].value, "count": row[2]}
    for row in timeline_result.all()
  ]

  # Get file attachments
  files_result = await db.execute(
    select(
      FunctionDataOutputOrm.file_path,
      FunctionDataOutputOrm.file_size_bytes,
      FunctionDataOutputOrm.data_type,
    ).filter(
      and_(
        FunctionDataOutputOrm.protocol_run_accession_id == protocol_run_accession_id,
        FunctionDataOutputOrm.file_path.is_not(None),
      ),
    ),
  )

  file_attachments = [
    {"file_path": row[0], "file_size_bytes": row[1], "data_type": row[2].value}
    for row in files_result.all()
  ]

  machines_used = [m for m in machines_used if m is not None]
  resource_with_data = [r for r in resource_with_data if r is not None]

  return ProtocolRunDataSummary(
    protocol_run_accession_id=protocol_run_accession_id,
    total_data_outputs=total_data_outputs or 0,
    data_types=data_types,
    machines_used=machines_used,  # type: ignore
    resource_with_data=resource_with_data,  # type: ignore
    data_timeline=data_timeline,
    file_attachments=file_attachments,
  )
