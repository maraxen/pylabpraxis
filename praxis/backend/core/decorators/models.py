import contextvars
import types
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, cast, runtime_checkable

from praxis.backend.core.run_context import PraxisRunContext
from praxis.backend.models.pydantic_internals.protocol import (
  FunctionProtocolDefinitionCreate,
)
from praxis.backend.utils.logging import get_logger

if TYPE_CHECKING:
  import uuid

logger = get_logger(__name__)

DEFAULT_DECK_PARAM_NAME = "deck"
DEFAULT_STATE_PARAM_NAME = "state"
TOP_LEVEL_NAME_REGEX = r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$"

praxis_run_context_cv: contextvars.ContextVar[PraxisRunContext] = contextvars.ContextVar(
  "praxis_run_context",
)


@dataclass
class DataViewDefinition:
  """Defines a data view required by a protocol for input data.

  Data views allow protocols to declare what input data they need in a structured way.
  The views can reference:
  - PLR state data (e.g., liquid volume tracking, resource positions)
  - Function data outputs from previous protocol runs (e.g., plate reader reads)

  Attributes:
    name: Unique identifier for this data view within the protocol.
    description: Human-readable description of what data this view provides.
    source_type: Type of data source - 'plr_state', 'function_output', or 'external'.
    source_filter: Filter criteria to select specific data.
      For 'plr_state': {"state_key": "tracker.volumes", "resource_pattern": "*plate*"}
      For 'function_output': {"function_fqn": "...", "output_type": "absorbance"}
    schema: Expected data schema for validation (column names, types).
    required: Whether this data view is required for protocol execution.
    default_value: Default value if data is not available and not required.

  """

  name: str
  description: str | None = None
  source_type: str = "function_output"  # "plr_state", "function_output", "external"
  source_filter: dict[str, Any] | None = None
  schema: dict[str, Any] | None = None  # Column definitions for validation
  required: bool = False  # If True, warn (but don't block) if missing
  default_value: Any = None


@dataclass
class SetupInstruction:
  """A setup instruction to display before protocol execution.

  Setup instructions are user-facing messages that communicate required manual
  preparation before execution. They are displayed in the Deck Setup wizard.

  Attributes:
    message: The instruction text to display to the user.
    severity: Importance level - 'required', 'recommended', or 'info'.
      - required: Must be acknowledged before proceeding (highlighted in accent color)
      - recommended: Suggested but not blocking (highlighted in primary color)
      - info: Informational only (muted color)
    position: Optional deck position this instruction relates to (e.g., "3").
    resource_type: Optional expected resource type (e.g., "TipRack").

  """

  message: str
  severity: str = "required"  # "required", "recommended", "info"
  position: str | None = None
  resource_type: str | None = None


@runtime_checkable
class DecoratedProtocolFunc(Protocol):
  """A protocol for a function that has been decorated for use as a Praxis protocol."""

  __name__: str
  __module__: str
  __qualname__: str
  __code__: types.CodeType
  _protocol_runtime_info: "ProtocolRuntimeInfo"
  _protocol_definition: Any

  def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


@dataclass
class CreateProtocolDefinitionData:
  func: DecoratedProtocolFunc | Callable
  name: str | None
  version: str
  description: str | None
  solo: bool
  is_top_level: bool
  preconfigure_deck: bool
  deck_param_name: str
  deck_construction: Callable | None
  deck_layout_path: str | None  # Path to JSON deck layout configuration
  data_views: list[DataViewDefinition] | None  # Input data view definitions
  setup_instructions: list[str | SetupInstruction] | None  # Pre-run setup messages
  state_param_name: str
  param_metadata: dict[str, Any]
  category: str | None
  tags: list[str]
  top_level_name_format: str


class ProtocolRuntimeInfo:
  """A container for runtime information about a protocol function."""

  def __init__(
    self,
    pydantic_definition: FunctionProtocolDefinitionCreate,
    function_ref: Callable,
    found_state_param_details: dict[str, Any] | None,
  ) -> None:
    """Initialize the ProtocolRuntimeInfo.

    Args:
        pydantic_definition (FunctionProtocolDefinitionCreate): The Pydantic model
            definition of the protocol function.
        function_ref (Callable): The actual function reference.
        found_state_param_details (Optional[dict[str, Any]]): Details about the
            state parameter if it exists.

    """
    self.pydantic_definition: FunctionProtocolDefinitionCreate = pydantic_definition
    self.function_ref: Callable = function_ref
    self.callable_wrapper: Callable | None = None
    self.db_accession_id: uuid.UUID | None = None
    self.found_state_param_details: dict[str, Any] | None = found_state_param_details


def get_callable_fqn(func: Callable) -> str:
  """Get the fully qualified name of a callable function.

  Args:
      func (Callable): The callable function.

  Returns:
      str: The fully qualified name (e.g., "module.submodule.function_name").

  """
  f = cast(DecoratedProtocolFunc, func)
  return f"{f.__module__}.{f.__qualname__}"
