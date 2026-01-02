# pylint: disable=too-many-arguments, broad-except, fixme
"""Resource management for WorkcellRuntime."""

import uuid
from typing import TYPE_CHECKING, cast

from pylabrobot.machines import Machine
from pylabrobot.resources import Resource

if TYPE_CHECKING:
  from praxis.backend.core.workcell_runtime.core import WorkcellRuntime

from praxis.backend.core.workcell_runtime.utils import (
  get_class_from_fqn,
  log_workcell_runtime_errors,
)
from praxis.backend.models import ResourceOrm, ResourceStatusEnum
from praxis.backend.utils.errors import WorkcellRuntimeError
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class ResourceManagerMixin:
  """Mixin for managing resources in WorkcellRuntime."""

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error creating or getting resource",
    suffix=" - Ensure the resource instance ORM and definition FQN are valid.",
  )
  async def create_or_get_resource(
    self,
    resource_orm: ResourceOrm,
    resource_definition_fqn: str,
  ) -> Resource:
    """Create or retrieve a live PyLabRobot resource object."""
    runtime = cast("WorkcellRuntime", self)
    if not hasattr(resource_orm, "id") or resource_orm.accession_id is None:
      msg = "Invalid resource_orm object passed to create_or_get_resource (no id)."
      raise ValueError(
        msg,
      )

    if resource_orm.accession_id in runtime._active_resources:
      logger.info(
        "WorkcellRuntime: Resource '%s' (ID: %s) already active. Returning existing instance.",
        resource_orm.name,
        resource_orm.accession_id,
      )
      return runtime._active_resources[resource_orm.accession_id]

    shared_plr_instance: Machine | Resource | None = None
    if (
      resource_orm.is_machine
      and resource_orm.machine_counterpart
      and resource_orm.machine_counterpart.is_resource
      and resource_orm.machine_counterpart.resource_counterpart
      and resource_orm.machine_counterpart.resource_counterpart.accession_id
      == resource_orm.accession_id
    ):
      machine_orm = resource_orm.machine_counterpart
      if machine_orm.accession_id in runtime._active_machines:
        shared_plr_instance = runtime._active_machines[machine_orm.accession_id]
        logger.info(
          "WorkcellRuntime: Resource '%s' (ID: %s) is linked to active Machine "
          "'%s' (ID: %s). Reusing existing PLR object as the resource instance.",
          resource_orm.name,
          resource_orm.accession_id,
          machine_orm.name,
          machine_orm.accession_id,
        )
        if not isinstance(shared_plr_instance, Resource):
          msg = (
            f"Linked Machine ID {machine_orm.accession_id} is active but its PLR object "
            f"'{type(shared_plr_instance).__name__}' is not a PyLabRobot Resource. "
            f"Cannot use as resource."
          )
          raise TypeError(
            msg,
          )

    resource: Resource
    if shared_plr_instance:
      resource = cast("Resource", shared_plr_instance)
    else:
      logger.info(
        "Creating new PLR resource '%s' (ID: %s) using definition FQN '%s'.",
        resource_orm.name,
        resource_orm.accession_id,
        resource_definition_fqn,
      )

      try:
        resource_class = get_class_from_fqn(resource_definition_fqn)
        resource = resource_class(name=resource_orm.name)
      except Exception as e:  # pylint: disable=broad-except
        error_message = (
          f"Failed to create PLR resource for "
          f"'{resource_orm.name}' using FQN '"
          f"{resource_definition_fqn}': {str(e)[:250]}"
        )
        if hasattr(resource_orm, "id") and resource_orm.accession_id is not None:
          try:
            async with runtime.db_session_factory() as db_session:
              await runtime.resource_svc.update_resource_location_and_status(
                db=db_session,
                resource_accession_id=resource_orm.accession_id,
                new_status=ResourceStatusEnum.ERROR,
                status_details=error_message,
              )
              await db_session.commit()
          except Exception as db_error:  # pylint: disable=broad-except
            error_message += (
              f" Failed to update resource instance ID {resource_orm.accession_id} "
              f"status to ERROR in DB: {str(db_error)[:250]}"
            )
            raise WorkcellRuntimeError(error_message) from db_error
        raise WorkcellRuntimeError(error_message) from e

    runtime._active_resources[resource_orm.accession_id] = resource
    runtime._main_workcell.add_asset(resource)
    logger.info(
      "WorkcellRuntime: Resource '%s' (ID: %s) stored in _active_resources and added to main "
      "Workcell.",
      resource_orm.name,
      resource_orm.accession_id,
    )

    if (
      resource_orm.is_machine
      and resource_orm.machine_counterpart
      and resource_orm.machine_counterpart.is_resource
      and resource_orm.machine_counterpart.resource_counterpart
      and resource_orm.machine_counterpart.resource_counterpart.accession_id
      == resource_orm.accession_id
    ):
      machine_orm = resource_orm.machine_counterpart
      if isinstance(resource, Machine):
        runtime._active_machines[machine_orm.accession_id] = cast("Machine", resource)
        logger.info(
          "WorkcellRuntime: Resource '%s' (ID: %s) also registered as Machine "
          "'%s' (ID: %s) in _active_machines, sharing the same PLR object.",
          resource_orm.name,
          resource_orm.accession_id,
          machine_orm.name,
          machine_orm.accession_id,
        )
      else:
        logger.warning(
          "WorkcellRuntime: Resource '%s' (ID: %s) is flagged as a machine "
          "counterpart, but its PLR object type '%s' is not a PyLabRobot Machine "
          "subclass. It will not be registered in _active_machines.",
          resource_orm.name,
          resource_orm.accession_id,
          type(resource).__name__,
        )
    return resource

  def get_active_resource(
    self,
    resource_orm_accession_id: uuid.UUID,
  ) -> Resource:
    """Retrieve an active PyLabRobot resource object by its ORM ID."""
    runtime = cast("WorkcellRuntime", self)
    resource = runtime._active_resources.get(resource_orm_accession_id)
    if resource is None:
      msg = f"Resource instance with ORM ID {resource_orm_accession_id} not found in active \
          resources."
      raise WorkcellRuntimeError(
        msg,
      )
    if not isinstance(resource, Resource):
      msg = f"Resource instance with ORM ID {resource_orm_accession_id} is not a valid \
          PyLabRobot Resource instance. Type is {type(resource)}."
      raise TypeError(
        msg,
      )
    return resource

  def get_active_resource_accession_id(self, resource: Resource) -> uuid.UUID:
    """Retrieve the ORM ID of an active PyLabRobot resource object."""
    runtime = cast("WorkcellRuntime", self)
    for orm_accession_id, active_resource in runtime._active_resources.items():
      if active_resource is resource:
        return orm_accession_id
    msg = f"Resource instance {resource}"
    raise WorkcellRuntimeError(msg)

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error clearing resource",
    suffix=" - Ensure the resource is valid and exists in active resources.",
  )
  async def clear_resource(self, resource_orm_accession_id: uuid.UUID) -> None:
    """Clear a resource from the workcell runtime."""
    runtime = cast("WorkcellRuntime", self)
    if resource_orm_accession_id in runtime._active_resources:
      del runtime._active_resources[resource_orm_accession_id]

    async with runtime.db_session_factory() as db_session:
      await runtime.resource_svc.update_resource_location_and_status(
        db=db_session,
        resource_accession_id=resource_orm_accession_id,
        new_status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
        status_details="Resource cleared from active resources.",
      )
      await db_session.commit()

    logger.info(
      "WorkcellRuntime: Cleared resource with ORM ID %s from active resources.",
      resource_orm_accession_id,
    )
