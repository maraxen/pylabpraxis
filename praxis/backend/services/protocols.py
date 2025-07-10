# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Manage protocol-related data interactions.

praxis/db_services/protocol_data_service.py

Service layer for interacting with protocol-related data in the database.
This includes definitions for protocol sources, static protocol definitions,
protocol run instances, and function call logs.

"""

import datetime
import json
import logging
import uuid
from typing import cast

from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from praxis.backend.models.orm.protocol import (
  FunctionCallLogOrm,
  ProtocolRunOrm,
)
from praxis.backend.models.pydantic.filters import SearchFilters
from praxis.backend.models.pydantic.protocol import (
  ProtocolRunCreate,
  ProtocolRunStatusEnum,
  ProtocolRunUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
)
from praxis.backend.utils.db import Base
from praxis.backend.utils.uuid import uuid7

logger = logging.getLogger(__name__)


class ProtocolRunService(CRUDBase[ProtocolRunOrm, ProtocolRunCreate, ProtocolRunUpdate]):
  """Service for protocol run operations."""

  async def create(self, db: AsyncSession, *, obj_in: ProtocolRunCreate) -> ProtocolRunOrm:
    """Create a new protocol run instance."""
    run_accession_id = uuid7()
    logger.info(
      "Creating new protocol run with GUID '%s' for definition ID %s.",
      run_accession_id,
      obj_in.top_level_protocol_definition_accession_id,
    )
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    db_protocol_run = self.model(
      run_accession_id=run_accession_id,
      top_level_protocol_definition_accession_id=(
        obj_in.top_level_protocol_definition_accession_id
      ),
      status=obj_in.status,
      input_parameters_json=(obj_in.input_parameters_json if obj_in.input_parameters_json else {}),
      initial_state_json=(obj_in.initial_state_json if obj_in.initial_state_json else {}),
      start_time=utc_now if obj_in.status != ProtocolRunStatusEnum.PENDING else None,
    )
    db.add(db_protocol_run)
    try:
      await db.commit()
      await db.refresh(db_protocol_run)
      logger.info(
        "Successfully created protocol run (ID: %s, GUID: %s).",
        db_protocol_run.accession_id,
        db_protocol_run.run_accession_id,
      )
    except IntegrityError as e:
      await db.rollback()
      error_message = (
        f"Integrity error creating protocol run '{run_accession_id}'. This might "
        f"be due to a duplicate GUID. Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    except Exception as e:
      await db.rollback()
      logger.exception(
        "Unexpected error creating protocol run '%s'. Rolling back.",
        run_accession_id,
      )
      raise e
    return db_protocol_run

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
    protocol_definition_accession_id: uuid.UUID | None = None,  # Specific filter
    protocol_name: str | None = None,  # Specific filter
    status: ProtocolRunStatusEnum | None = None,
  ) -> list[ProtocolRunOrm]:
    """List protocol runs with optional filtering and pagination."""
    logger.info(
      "Listing protocol runs with filters: def_accession_id=%s, name='%s', status=%s, ",
      protocol_definition_accession_id,
      protocol_name,
      status,
    )
    stmt = select(self.model).options(
      joinedload(self.model.top_level_protocol_definition),
    )

    if protocol_definition_accession_id is not None:
      stmt = stmt.filter(
        self.model.top_level_protocol_definition_accession_id == protocol_definition_accession_id,
      )
      logger.debug(
        "Filtering by protocol definition ID: %s.",
        protocol_definition_accession_id,
      )
    if protocol_name is not None:
      stmt = stmt.join(
        FunctionProtocolDefinitionOrm,
        self.model.top_level_protocol_definition_accession_id
        == FunctionProtocolDefinitionOrm.accession_id,
      ).filter(FunctionProtocolDefinitionOrm.name == protocol_name)
      logger.debug("Filtering by protocol name: '%s'.", protocol_name)
    if status is not None:
      stmt = stmt.filter(self.model.status == status)
      logger.debug("Filtering by status: '%s'.", status.name)

    stmt = apply_date_range_filters(stmt, filters, cast("Base", self.model).start_time)
    stmt = apply_pagination(stmt, filters)

    stmt = stmt.order_by(
      desc(self.model.start_time),
      desc(self.model.accession_id),
    )
    result = await db.execute(stmt)
    protocol_runs = list(result.scalars().all())
    logger.info("Found %d protocol runs.", len(protocol_runs))
    return protocol_runs

  async def get_by_name(self, db: AsyncSession, name: str) -> ProtocolRunOrm | None:
    """Retrieve a protocol run by its name."""
    logger.info("Retrieving protocol run with name: '%s'.", name)
    stmt = (
      select(self.model)
      .options(
        selectinload(self.model.function_calls)
        .selectinload(FunctionCallLogOrm.executed_function_definition)
        .selectinload(FunctionProtocolDefinitionOrm.source_repository),
        selectinload(self.model.function_calls)
        .selectinload(FunctionCallLogOrm.executed_function_definition)
        .selectinload(FunctionProtocolDefinitionOrm.file_system_source),
        joinedload(self.model.top_level_protocol_definition),
      )
      .join(
        FunctionProtocolDefinitionOrm,
        self.model.top_level_protocol_definition_accession_id
        == FunctionProtocolDefinitionOrm.accession_id,
      )
      .filter(FunctionProtocolDefinitionOrm.name == name)
    )
    result = await db.execute(stmt)
    protocol_run = result.scalar_one_or_none()
    if protocol_run:
      logger.info("Found protocol run with name '%s'.", name)
    else:
      logger.info("Protocol run with name '%s' not found.", name)
    return protocol_run

  async def update_protocol_run_status(
    self,
    db: AsyncSession,
    protocol_run_accession_id: uuid.UUID,
    new_status: ProtocolRunStatusEnum,
    output_data_json: str | None = None,
    final_state_json: str | None = None,
    error_info: dict[str, str] | None = None,
  ) -> ProtocolRunOrm | None:
    """Update the status and details of a protocol run."""
    logger.info(
      "Updating status for protocol run ID %s to '%s'.",
      protocol_run_accession_id,
      new_status.name,
    )
    stmt = select(self.model).filter(
      self.model.accession_id == protocol_run_accession_id,
    )
    result = await db.execute(stmt)
    db_protocol_run = result.scalar_one_or_none()

    if db_protocol_run:
      db_protocol_run.status = new_status
      utc_now = datetime.datetime.now(datetime.timezone.utc)

      if new_status == ProtocolRunStatusEnum.RUNNING and not db_protocol_run.start_time:
        db_protocol_run.start_time = utc_now
        logger.debug(
          "Protocol run ID %s started at %s.",
          protocol_run_accession_id,
          utc_now,
        )

      if new_status in [
        ProtocolRunStatusEnum.COMPLETED,
        ProtocolRunStatusEnum.FAILED,
        ProtocolRunStatusEnum.CANCELLED,
      ]:
        db_protocol_run.end_time = utc_now
        logger.debug(
          "Protocol run ID %s ended at %s with status %s.",
          protocol_run_accession_id,
          utc_now,
          new_status.name,
        )
        if db_protocol_run.start_time and db_protocol_run.end_time:
          duration = db_protocol_run.end_time - db_protocol_run.start_time
          db_protocol_run.completed_duration_ms = int(duration.total_seconds() * 1000)
          logger.debug(
            "Protocol run ID %s duration: %d ms.",
            protocol_run_accession_id,
            db_protocol_run.completed_duration_ms,
          )
        if output_data_json is not None:
          db_protocol_run.output_data_json = json.loads(output_data_json)
          logger.debug(
            "Protocol run ID %s updated with output data.",
            protocol_run_accession_id,
          )
        if final_state_json is not None:
          db_protocol_run.final_state_json = json.loads(final_state_json)
          logger.debug(
            "Protocol run ID %s updated with final state.",
            protocol_run_accession_id,
          )
        if new_status == ProtocolRunStatusEnum.FAILED and error_info:
          db_protocol_run.output_data_json = error_info  # type: ignore
          logger.error(
            "Protocol run ID %s failed with error info: %s",
            protocol_run_accession_id,
            error_info,
          )
      try:
        await db.commit()
        await db.refresh(db_protocol_run)
        logger.info(
          "Successfully updated protocol run ID %s status to '%s'.",
          protocol_run_accession_id,
          new_status.name,
        )
      except Exception as e:
        await db.rollback()
        logger.exception(
          "Unexpected error updating protocol run ID %s status. Rolling back.",
          protocol_run_accession_id,
        )
        raise e
      return db_protocol_run
    logger.warning(
      "Protocol run ID %s not found for status update.",
      protocol_run_accession_id,
    )
    return None


protocol_run_service = ProtocolRunService(ProtocolRunOrm)
