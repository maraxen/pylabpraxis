"""WorkcellRuntime Protocol."""

import uuid
from typing import Any, Protocol, runtime_checkable

from pylabrobot.machines import Machine
from pylabrobot.resources import Coordinate, Deck, Resource

from praxis.backend.core.protocols.workcell import IWorkcell
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.resource import ResourceOrm


@runtime_checkable
class IWorkcellRuntime(Protocol):
  """A protocol for a workcell runtime."""

  async def start_workcell_state_sync(self) -> None: ...

  async def stop_workcell_state_sync(self) -> None: ...

  def get_main_workcell(self) -> IWorkcell: ...

  def get_state_snapshot(self) -> dict[str, Any]: ...

  def apply_state_snapshot(self, snapshot_json: dict[str, Any]) -> None: ...

  async def initialize_machine(self, machine_orm: MachineOrm) -> Machine: ...

  async def create_or_get_resource(
    self,
    resource_orm: ResourceOrm,
    resource_definition_fqn: str,
  ) -> Resource: ...

  def get_active_machine(self, machine_orm_accession_id: uuid.UUID) -> Machine: ...

  def get_active_machine_accession_id(self, machine: Machine) -> uuid.UUID: ...

  def get_active_deck_accession_id(self, deck: Deck) -> uuid.UUID: ...

  def get_active_resource(
    self,
    resource_orm_accession_id: uuid.UUID,
  ) -> Resource: ...

  def get_active_resource_accession_id(self, resource: Resource) -> uuid.UUID: ...

  def get_active_deck(self, deck_orm_accession_id: uuid.UUID) -> Deck: ...

  async def shutdown_machine(self, machine_orm_accession_id: uuid.UUID) -> None: ...

  async def assign_resource_to_deck(
    self,
    resource_orm_accession_id: uuid.UUID,
    target: uuid.UUID,
    location: Coordinate | tuple[float, float, float] | None = None,
    position_accession_id: str | int | uuid.UUID | None = None,
  ) -> None: ...

  async def clear_deck_position(
    self,
    deck_orm_accession_id: uuid.UUID,
    position_name: str,
    resource_orm_accession_id: uuid.UUID | None = None,
  ) -> None: ...

  async def execute_machine_action(
    self,
    machine_orm_accession_id: uuid.UUID,
    action_name: str,
    params: dict[str, Any] | None = None,
  ) -> Any: ...

  async def shutdown_all_machines(self) -> None: ...

  async def get_deck_state_representation(
    self,
    deck_orm_accession_id: uuid.UUID,
  ) -> dict[str, Any]: ...

  async def get_last_initialized_deck_object(self) -> Deck | None: ...

  async def clear_resource(self, resource_orm_accession_id: uuid.UUID) -> None: ...
