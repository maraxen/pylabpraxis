"""ProtocolExecutionService Protocol."""

import uuid
from typing import Any, Protocol, runtime_checkable

from praxis.backend.models.domain.protocol import ProtocolRun


@runtime_checkable
class IProtocolExecutionService(Protocol):
  """A protocol for a protocol execution service."""

  async def execute_protocol_immediately(
    self,
    protocol_name: str,
    user_input_params: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    protocol_version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
  ) -> ProtocolRun: ...

  async def schedule_protocol_execution(
    self,
    protocol_name: str,
    user_input_params: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    protocol_version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
  ) -> ProtocolRun: ...

  async def get_protocol_run_status(
    self,
    protocol_run_id: uuid.UUID,
  ) -> dict[str, Any] | None: ...

  async def cancel_protocol_run(self, protocol_run_id: uuid.UUID) -> bool: ...
