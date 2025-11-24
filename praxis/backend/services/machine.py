# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Service layer for Machine Data Management.

praxis/db_services/machine_data_service.py

Service layer for interacting with machine-related data in the database.
This includes Machine Definitions, Machine Instances, and Machine configurations.
"""

import datetime
import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from praxis.backend.models.orm.machine import MachineOrm, MachineStatusEnum
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.machine import MachineCreate, MachineUpdate
from praxis.backend.services.entity_linking import (
  _create_or_link_resource_counterpart_for_machine,
  synchronize_machine_resource_names,
)
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
  apply_specific_id_filters,
)
from praxis.backend.utils.db_decorator import handle_db_transaction
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class MachineService(CRUDBase[MachineOrm, MachineCreate, MachineUpdate]):

  """Service for machine-related operations."""

  @handle_db_transaction
  async def create(
    self,
    db: AsyncSession,
    *,
    obj_in: MachineCreate,
  ) -> MachineOrm:
    """Create a new machine in the database."""
    log_prefix = f"Machine (Name: '{obj_in.name}', creating new):"
    logger.info("%s Attempting to create new machine.", log_prefix)

    result = await db.execute(select(MachineOrm).filter(MachineOrm.name == obj_in.name))
    if result.scalar_one_or_none():
      error_message = (
        f"{log_prefix} A machine with name '{obj_in.name}' already exists. Use the update "
        f"function for existing machines."
      )
      logger.error(error_message)
      raise ValueError(error_message)

    machine_orm = await super().create(db=db, obj_in=obj_in)
    logger.info("%s Initialized new machine for creation.", log_prefix)

    if obj_in.resource_counterpart_accession_id or obj_in.resource_def_name:
      await _create_or_link_resource_counterpart_for_machine(
        db=db,
        machine_orm=machine_orm,
        resource_counterpart_accession_id=obj_in.resource_counterpart_accession_id,
        resource_definition_name=obj_in.resource_def_name,
        resource_properties_json=obj_in.resource_properties_json,
        resource_status=obj_in.resource_initial_status,
      )

    await db.flush()
    await db.refresh(machine_orm, attribute_names=["resource_counterpart"])
    if machine_orm.resource_counterpart:
      await db.refresh(machine_orm.resource_counterpart)
    logger.info("%s Successfully committed new machine.", log_prefix)
    return machine_orm

  @handle_db_transaction
  async def update(
    self,
    db: AsyncSession,
    *,
    db_obj: MachineOrm,
    obj_in: MachineUpdate,
  ) -> MachineOrm:
    """Update an existing machine with the provided data."""
    update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
    log_prefix = f"Machine (ID: {db_obj.accession_id}, updating):"
    logger.info("%s Attempting to update machine.", log_prefix)

    name = update_data.get("name")
    if name is not None and db_obj.name != name:
      existing_name_check = await db.execute(
        select(MachineOrm)
        .filter(MachineOrm.name == name)
        .filter(MachineOrm.accession_id != db_obj.accession_id),
      )
      if existing_name_check.scalar_one_or_none():
        error_message = (
          f"{log_prefix} Cannot update name to '{name}' as it already exists for another machine."
        )
        logger.error(error_message)
        raise ValueError(error_message)
      db_obj.name = name

      await synchronize_machine_resource_names(db, db_obj, name)

    updated_machine = await super().update(db=db, db_obj=db_obj, obj_in=obj_in)

    logger.info("%s Initialized machine for update.", log_prefix)
    if (
      updated_machine.resource_counterpart is not None
      or update_data.get("resource_counterpart_accession_id")
      or update_data.get("resource_def_name")
    ):
      await _create_or_link_resource_counterpart_for_machine(
        db=db,
        machine_orm=updated_machine,
        resource_counterpart_accession_id=update_data.get(
          "resource_counterpart_accession_id",
        ),
        resource_definition_name=update_data.get("resource_def_name"),
        resource_properties_json=update_data.get("resource_properties_json"),
        resource_status=update_data.get("resource_initial_status"),
      )

      await db.flush()
      await db.refresh(updated_machine, attribute_names=["resource_counterpart"])
      if updated_machine.resource_counterpart:
        await db.refresh(updated_machine.resource_counterpart)
      logger.info("%s Successfully committed updated machine.", log_prefix)
    return updated_machine

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
    status: MachineStatusEnum | None = None,
    pylabrobot_class_filter: str | None = None,
    name_filter: str | None = None,
  ) -> list[MachineOrm]:
    """List all machines with optional filtering and pagination."""
    logger.info(
      "Listing machines with filters: %s",
      filters.model_dump_json(),
    )
    stmt = select(self.model).options(joinedload(self.model.resource_counterpart))

    if status:
      stmt = stmt.filter(self.model.status == status)
    if pylabrobot_class_filter:
      stmt = stmt.filter(self.model.fqn.like(f"%{pylabrobot_class_filter}%"))
    if name_filter:
      stmt = stmt.filter(self.model.name.ilike(f"%{name_filter}%"))
    stmt = apply_specific_id_filters(stmt, filters, self.model)
    stmt = apply_date_range_filters(stmt, filters, self.model.created_at)
    stmt = apply_pagination(stmt, filters)
    stmt = stmt.order_by(self.model.name)
    result = await db.execute(stmt)
    machines = list(result.scalars().all())
    logger.info("Found %d machines.", len(machines))
    return machines

  @handle_db_transaction
  async def update_machine_status(
    self,
    db: AsyncSession,
    machine_accession_id: uuid.UUID,
    new_status: MachineStatusEnum,
    status_details: str | None = None,
    current_protocol_run_accession_id: uuid.UUID | None = None,
  ) -> MachineOrm | None:
    """Update the status of a specific machine."""
    logger.info(
      "Attempting to update status for machine ID %s to '%s'.",
      machine_accession_id,
      new_status.value,
    )
    machine_orm = await self.get(db, accession_id=machine_accession_id)
    if not machine_orm:
      logger.warning(
        "Machine with ID %s not found for status update.",
        machine_accession_id,
      )
      return None

    logger.debug(
      "Machine '%s' (ID: %s) status changing from '%s' to '%s'.",
      machine_orm.name,
      machine_accession_id,
      machine_orm.status.value,
      new_status.value,
    )
    machine_orm.status = new_status
    machine_orm.status_details = status_details

    if new_status == MachineStatusEnum.IN_USE:
      machine_orm.current_protocol_run_accession_id = current_protocol_run_accession_id
      logger.debug(
        "Machine '%s' (ID: %s) set to IN_USE with protocol run GUID: %s.",
        machine_orm.name,
        machine_accession_id,
        current_protocol_run_accession_id,
      )
    elif machine_orm.current_protocol_run_accession_id == current_protocol_run_accession_id:
      machine_orm.current_protocol_run_accession_id = None
      logger.debug(
        "Machine '%s' (ID: %s) protocol run GUID cleared as it matches the "
        "current one and status is no longer IN_USE.",
        machine_orm.name,
        machine_accession_id,
      )

    if new_status != MachineStatusEnum.OFFLINE:
      machine_orm.last_seen_online = datetime.datetime.now(datetime.timezone.utc)
      logger.debug(
        "Machine '%s' (ID: %s) last seen online updated.",
        machine_orm.name,
        machine_accession_id,
      )

    await db.flush()
    await db.refresh(machine_orm)
    logger.info(
      "Successfully updated status for machine ID %s to '%s'.",
      machine_accession_id,
      new_status.value,
    )
    return machine_orm

  @handle_db_transaction
  async def remove(self, db: AsyncSession, *, accession_id: UUID) -> MachineOrm | None:
    """Delete a specific machine by its ID."""
    logger.info("Attempting to delete machine with ID: %s.", accession_id)
    machine_orm = await super().remove(db, accession_id=accession_id)
    if not machine_orm:
      logger.warning("Machine with ID %s not found for deletion.", accession_id)
      return None
    logger.info(
      "Successfully deleted machine ID %s: '%s'.",
      accession_id,
      machine_orm.name,
    )
    return machine_orm


machine_service = MachineService(MachineOrm)
