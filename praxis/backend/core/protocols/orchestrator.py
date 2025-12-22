"""Orchestrator Protocol."""

from typing import Any, Protocol, runtime_checkable

from praxis.backend.models.orm.protocol import ProtocolRunOrm


@runtime_checkable
class IOrchestrator(Protocol):

  """A protocol for an orchestrator."""

  async def execute_protocol(
    self,
    protocol_name: str,
    input_parameters: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    protocol_version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
    is_simulation: bool = False,
  ) -> ProtocolRunOrm: ...

  async def execute_existing_protocol_run(
    self,
    protocol_run_orm: ProtocolRunOrm,
    user_input_params: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    is_simulation: bool = False,
  ) -> ProtocolRunOrm: ...
