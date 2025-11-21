# pylint: disable=too-many-arguments,too-many-locals,fixme,unused-argument
"""The Orchestrator manages the lifecycle of protocol runs."""
# broad-except is justified at method level where necessary.

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from praxis.backend.core.asset_manager import AssetManager
from praxis.backend.core.orchestrator.asset_acquisition import AssetAcquisitionMixin
from praxis.backend.core.orchestrator.error_handling import ErrorHandlingMixin
from praxis.backend.core.orchestrator.execution import ExecutionMixin
from praxis.backend.core.orchestrator.protocol_preparation import ProtocolPreparationMixin
from praxis.backend.core.protocol_code_manager import ProtocolCodeManager
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class Orchestrator(
    ProtocolPreparationMixin,
    AssetAcquisitionMixin,
    ExecutionMixin,
    ErrorHandlingMixin,
):
  """Central component for managing and executing laboratory protocols.

  The Orchestrator is responsible for coordinating the execution of protocols.
  It coordinates asset allocation, runtime environment setup, protocol execution,
  logging, and run control.
  """

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    asset_manager: AssetManager,
    workcell_runtime: WorkcellRuntime,
    protocol_code_manager: ProtocolCodeManager | None = None,
  ) -> None:
    """Initialize the Orchestrator.

    Args:
        db_session_factory: A factory to create SQLAlchemy AsyncSession instances.
        asset_manager: An instance of AssetManager for asset allocation.
        workcell_runtime: An instance of WorkcellRuntime to manage live PLR objects.
        protocol_code_manager: An instance of ProtocolCodeManager for code preparation.
            If None, a new instance will be created.

    Raises:
        ValueError: If any of the arguments are invalid.
        TypeError: If any of the arguments are of the wrong type.

    """
    self.db_session_factory = db_session_factory
    self.asset_manager = asset_manager
    self.workcell_runtime = workcell_runtime
    self.protocol_code_manager = protocol_code_manager or ProtocolCodeManager()
    logger.info("Orchestrator initialized.")
