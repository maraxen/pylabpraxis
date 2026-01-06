# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Manage protocol-related data interactions.

praxis/db_services/protocol_data_service.py

Service layer for interacting with protocol-related data in the database.
This includes definitions for protocol sources, static protocol definitions,
protocol run instances, and function call logs.

"""

import datetime
import enum
import inspect
import json
import logging
import uuid

from sqlalchemy import desc, select
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from praxis.backend.models.enums import FunctionCallStatusEnum
from praxis.backend.models.orm.protocol import (
  FunctionCallLogOrm,
  FunctionProtocolDefinitionOrm,
  ProtocolRunOrm,
)
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.protocol import (
  ProtocolRunCreate,
  ProtocolRunStatusEnum,
  ProtocolRunUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
)
from praxis.backend.utils.db_decorator import handle_db_transaction
from praxis.backend.utils.errors import AssetAcquisitionError, OrchestratorError
from praxis.backend.utils.uuid import uuid7

logger = logging.getLogger(__name__)


class ProtocolRunService(CRUDBase[ProtocolRunOrm, ProtocolRunCreate, ProtocolRunUpdate]):
  """Service for protocol run operations."""

  @handle_db_transaction
  async def create(self, db: AsyncSession, *, obj_in: ProtocolRunCreate) -> ProtocolRunOrm:
    """Create a new protocol run instance."""
    logger.info(
      "Creating new protocol run with GUID '%s' for definition ID %s.",
      obj_in.run_accession_id,
      obj_in.top_level_protocol_definition_accession_id,
    )
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    # Exclude start_time from model_dump since we're setting it manually
    data = obj_in.model_dump(exclude={"start_time"})

    # Map Pydantic field name to ORM field name
    if "run_accession_id" in data:
      data["accession_id"] = data.pop("run_accession_id")

    # Extract accession_id before filtering (since it has init=False in Base)
    accession_id = data.pop("accession_id", None)

    # Filter to only valid constructor parameters
    init_signature = inspect.signature(self.model.__init__)
    valid_params = {p.name for p in init_signature.parameters.values()}
    filtered_data = {key: value for key, value in data.items() if key in valid_params}

    # Convert enum string values back to enum members for SQLAlchemy
    for attr_name, column in sa_inspect(self.model).columns.items():
      if attr_name in filtered_data and hasattr(column.type, "enum_class"):
        enum_class = getattr(column.type, "enum_class", None)
        if enum_class and issubclass(enum_class, enum.Enum):
          value = filtered_data[attr_name]
          if isinstance(value, str):
            for member in enum_class:
              if member.value == value:
                filtered_data[attr_name] = member
                break

    # Use the converted status value for the PENDING check
    status_value = filtered_data.get("status", obj_in.status)

    # Ensure name is set (required by Base)
    if not filtered_data.get("name"):
      filtered_data["name"] = f"run_{obj_in.run_accession_id}"

    db_protocol_run = self.model(
      **filtered_data,
      start_time=utc_now if status_value != ProtocolRunStatusEnum.PENDING else None,
    )

    # Set accession_id manually since it's not a constructor parameter
    if accession_id is not None:
      db_protocol_run.accession_id = accession_id

    db.add(db_protocol_run)
    await db.flush()
    await db.refresh(db_protocol_run)
    logger.info(
      "Successfully created protocol run (ID: %s).",
      db_protocol_run.accession_id,
    )
    # Ensure start_time is aware (SQLite fix)
    if db_protocol_run.start_time and db_protocol_run.start_time.tzinfo is None:
      db_protocol_run.start_time = db_protocol_run.start_time.replace(tzinfo=datetime.timezone.utc)

    return db_protocol_run

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
    protocol_definition_accession_id: uuid.UUID | None = None,
    protocol_name: str | None = None,
    status: ProtocolRunStatusEnum | None = None,
    statuses: list[ProtocolRunStatusEnum] | None = None,
  ) -> list[ProtocolRunOrm]:
    """List protocol runs with optional filtering and pagination."""
    logger.info(
      "Listing protocol runs with filters: def_accession_id=%s, name='%s', status=%s, statuses=%s",
      protocol_definition_accession_id,
      protocol_name,
      status,
      statuses,
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
    if statuses:
      stmt = stmt.filter(self.model.status.in_(statuses))
      logger.debug("Filtering by statuses: %s.", statuses)
    elif status is not None:
      stmt = stmt.filter(self.model.status == status)
      logger.debug("Filtering by status: '%s'.", status.name)

    stmt = apply_date_range_filters(stmt, filters, self.model.created_at)
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

  @handle_db_transaction
  async def update_run_status(
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
    stmt = (
      select(self.model)
      .options(joinedload(self.model.top_level_protocol_definition))
      .filter(
        self.model.accession_id == protocol_run_accession_id,
      )
    )
    result = await db.execute(stmt)
    db_protocol_run = result.scalar_one_or_none()

    if db_protocol_run:
      # Ensure start_time is aware (SQLite fix)
      if db_protocol_run.start_time and db_protocol_run.start_time.tzinfo is None:
        db_protocol_run.start_time = db_protocol_run.start_time.replace(
          tzinfo=datetime.timezone.utc
        )

      db_protocol_run.status = new_status
      utc_now = datetime.datetime.now(datetime.timezone.utc)

      if new_status == ProtocolRunStatusEnum.RUNNING and not db_protocol_run.start_time:
        # Connect to Core: specific handling for starting a run
        try:
          # Import here to avoid circular dependency
          from praxis.backend.api.global_dependencies import (
            get_scheduler,
          )

          scheduler = None
          try:
            scheduler = get_scheduler()
          except (ImportError, RuntimeError) as e:
            # Global dependencies not available or initialized (e.g. in tests)
            logger.warning("Scheduler not initialized, skipping Core integration. Error: %s", e)

          if scheduler:
            # 1. Get Protocol Definition
            protocol_def = db_protocol_run.top_level_protocol_definition

            # 2. Analyze requirements
            # Use input params from DB
            input_params = (
              db_protocol_run.input_parameters_json
              if isinstance(db_protocol_run.input_parameters_json, dict)
              else {}
            )
            requirements = await scheduler.analyze_protocol_requirements(
              protocol_def,
              input_params,
            )

            # 3. Reserve assets
            # This will raise AssetAcquisitionError if failing
            await scheduler.reserve_assets(requirements, db_protocol_run.accession_id)

        except (AssetAcquisitionError, OrchestratorError) as e:
          # Log error
          logger.error("Core exception caught in service: %s", e)

          # Update to FAILED
          db_protocol_run.status = ProtocolRunStatusEnum.FAILED
          db_protocol_run.end_time = utc_now
          db_protocol_run.output_data_json = {
            "error": "Protocol execution failed to start",
            "details": str(e),
          }
          await db.flush()
          await db.refresh(db_protocol_run)
          return db_protocol_run

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
        if db_protocol_run.start_time is not None and db_protocol_run.end_time is not None:
          duration = db_protocol_run.end_time - db_protocol_run.start_time  # type: ignore[optional]
          db_protocol_run.duration_ms = int(duration.total_seconds() * 1000)
          logger.debug(
            "Protocol run ID %s duration: %d ms.",
            protocol_run_accession_id,
            db_protocol_run.duration_ms,
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
          db_protocol_run.output_data_json = error_info
          logger.error(
            "Protocol run ID %s failed with error info: %s",
            protocol_run_accession_id,
            error_info,
          )
      await db.flush()
      await db.refresh(db_protocol_run)
      logger.info(
        "Successfully updated protocol run ID %s status to '%s'.",
        protocol_run_accession_id,
        new_status.name,
      )
      # Ensure start_time/end_time are aware (SQLite fix)
      if db_protocol_run.start_time and db_protocol_run.start_time.tzinfo is None:
        db_protocol_run.start_time = db_protocol_run.start_time.replace(
          tzinfo=datetime.timezone.utc
        )
      if db_protocol_run.end_time and db_protocol_run.end_time.tzinfo is None:
        db_protocol_run.end_time = db_protocol_run.end_time.replace(tzinfo=datetime.timezone.utc)

      return db_protocol_run
    logger.warning(
      "Protocol run ID %s not found for status update.",
      protocol_run_accession_id,
    )
    return None


protocol_run_service = ProtocolRunService(ProtocolRunOrm)


@handle_db_transaction
async def log_function_call_start(
  db: AsyncSession,
  protocol_run_orm_accession_id: uuid.UUID,
  function_definition_accession_id: uuid.UUID,
  sequence_in_run: int,
  input_args_json: str,
  parent_function_call_log_accession_id: uuid.UUID | None = None,
) -> FunctionCallLogOrm:
  """Log the start of a function call."""
  call_id = uuid7()
  db_obj = FunctionCallLogOrm(
    name=f"call_{call_id}",  # kw_only from Base
    protocol_run_accession_id=protocol_run_orm_accession_id,
    function_protocol_definition_accession_id=function_definition_accession_id,
    sequence_in_run=sequence_in_run,
    input_args_json=json.loads(input_args_json),
    parent_function_call_log_accession_id=parent_function_call_log_accession_id,
    status=FunctionCallStatusEnum.SUCCESS,
  )
  db_obj.accession_id = call_id
  db.add(db_obj)
  await db.flush()
  await db.refresh(db_obj)
  return db_obj


@handle_db_transaction
async def log_function_call_end(
  db: AsyncSession,
  function_call_log_accession_id: uuid.UUID,
  status: FunctionCallStatusEnum,
  return_value_json: str | None = None,
  error_message: str | None = None,
  error_traceback: str | None = None,
  duration_ms: float | None = None,
) -> FunctionCallLogOrm | None:
  """Log the end of a function call."""
  stmt = select(FunctionCallLogOrm).filter(
    FunctionCallLogOrm.accession_id == function_call_log_accession_id,
  )
  result = await db.execute(stmt)
  db_obj = result.scalar_one_or_none()
  if db_obj:
    db_obj.status = status
    db_obj.end_time = datetime.datetime.now(datetime.timezone.utc)
    if return_value_json:
      db_obj.return_value_json = json.loads(return_value_json)
    db_obj.error_message_text = error_message
    db_obj.error_traceback_text = error_traceback
    if duration_ms:
      db_obj.duration_ms = int(duration_ms)
    await db.flush()
    await db.refresh(db_obj)
  return db_obj
