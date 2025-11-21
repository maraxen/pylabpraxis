import contextvars
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from praxis.backend.core.run_context import PraxisRunContext
from praxis.backend.models.pydantic_internals.protocol import (
    FunctionProtocolDefinitionCreate,
)
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)

DEFAULT_DECK_PARAM_NAME = "deck"
DEFAULT_STATE_PARAM_NAME = "state"
TOP_LEVEL_NAME_REGEX = r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$"

praxis_run_context_cv: contextvars.ContextVar[PraxisRunContext] = contextvars.ContextVar(
    "praxis_run_context",
)


@dataclass
class CreateProtocolDefinitionData:
    func: Callable
    name: str | None
    version: str
    description: str | None
    solo: bool
    is_top_level: bool
    preconfigure_deck: bool
    deck_param_name: str
    deck_construction: Callable | None
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
    return f"{func.__module__}.{func.__qualname__}"
