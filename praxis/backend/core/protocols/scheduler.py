"""ProtocolScheduler Protocol."""

import uuid
from typing import Any, Protocol, runtime_checkable

from praxis.backend.models.orm.protocol import ProtocolRunOrm


@runtime_checkable
class IProtocolScheduler(Protocol):

  """A protocol for a protocol scheduler."""

  async def schedule_protocol_execution(
    self,
    protocol_run_orm: ProtocolRunOrm,
    user_params: dict[str, Any],
    initial_state: dict[str, Any] | None = None,
  ) -> bool: ...

  async def cancel_scheduled_run(self, protocol_run_id: uuid.UUID) -> bool: ...

  async def get_schedule_status(
    self,
    protocol_run_id: uuid.UUID,
  ) -> dict[str, Any] | None: ...

  async def list_active_schedules(self) -> list[dict[str, Any]]: ...
