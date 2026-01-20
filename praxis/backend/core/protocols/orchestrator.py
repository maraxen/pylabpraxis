"""Orchestrator Protocol."""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
  from praxis.backend.core.protocol_code_manager import ProtocolCodeManager

from praxis.backend.models.domain.protocol import ProtocolRun


@runtime_checkable
class IOrchestrator(Protocol):
  """A protocol for an orchestrator."""

  protocol_code_manager: "ProtocolCodeManager"

  async def execute_protocol(
    self,
    protocol_name: str,
    input_parameters: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    protocol_version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
    is_simulation: bool = False,
  ) -> ProtocolRun: ...

  async def execute_existing_protocol_run(
    self,
    protocol_run_model: ProtocolRun,
    user_input_params: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    is_simulation: bool = False,
  ) -> ProtocolRun: ...
