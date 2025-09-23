"""AssetManager Protocol."""

import uuid
from typing import Any, Protocol, runtime_checkable

from pylabrobot.resources import Deck

from praxis.backend.models.orm.machine import MachineStatusEnum
from praxis.backend.models.orm.resource import ResourceStatusEnum
from praxis.backend.models.pydantic_internals.asset import AcquireAsset
from praxis.backend.models.pydantic_internals.protocol import AssetRequirementModel


@runtime_checkable
class IAssetManager(Protocol):
  """A protocol for an asset manager."""

  async def apply_deck(
    self,
    deck_orm_accession_id: uuid.UUID,
    protocol_run_accession_id: uuid.UUID,
  ) -> Deck:
    ...

  async def acquire_machine(
    self,
    protocol_run_accession_id: uuid.UUID,
    requested_asset_name_in_protocol: str,
    fqn_constraint: str,
  ) -> tuple[Any, uuid.UUID, str]:
    ...

  async def acquire_resource(
    self,
    resource_data: AcquireAsset,
  ) -> tuple[Any, uuid.UUID, str]:
    ...

  async def acquire_asset(
    self,
    protocol_run_accession_id: uuid.UUID,
    asset_requirement: AssetRequirementModel,
  ) -> tuple[Any, uuid.UUID, str]:
    ...

  async def release_machine(
    self,
    machine_orm_accession_id: uuid.UUID,
    final_status: MachineStatusEnum = MachineStatusEnum.AVAILABLE,
    status_details: str | None = "Released from run",
  ) -> None:
    ...

  async def release_resource(
    self,
    resource_orm_accession_id: uuid.UUID,
    final_status: ResourceStatusEnum,
    final_properties_json_update: dict[str, Any] | None = None,
    clear_from_accession_id: uuid.UUID | None = None,
    clear_from_position_name: str | None = None,
    status_details: str | None = "Released from run",
  ) -> None:
    ...

  async def lock_asset(
    self,
    asset_type: str,
    asset_name: str,
    protocol_run_id: uuid.UUID,
    reservation_id: uuid.UUID,
  ) -> bool:
    ...

  async def unlock_asset(
    self,
    asset_type: str,
    asset_name: str,
    protocol_run_id: uuid.UUID,
    reservation_id: uuid.UUID,
  ) -> bool:
    ...
