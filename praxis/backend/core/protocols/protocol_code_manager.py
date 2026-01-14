"""ProtocolCodeManager Protocol."""

from collections.abc import Callable
from typing import Protocol, runtime_checkable

from praxis.backend.models import (
  FunctionProtocolDefinition,
  FunctionProtocolDefinitionCreate,
)


@runtime_checkable
class IProtocolCodeManager(Protocol):
  """A protocol for a protocol code manager."""

  async def prepare_protocol_code(
    self,
    protocol_def_model: FunctionProtocolDefinition,
  ) -> tuple[Callable, FunctionProtocolDefinitionCreate]: ...
