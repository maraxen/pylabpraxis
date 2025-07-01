# pylint: disable=too-many-arguments,broad-except
"""Global dependencies for the Praxis API.

This module provides a centralized way to manage global dependencies,
such as the scheduler and asset manager, using a dependency injection
pattern. This avoids the use of global variables and makes the code
more testable and maintainable.
"""

from praxis.backend.configure import PraxisConfiguration
from praxis.backend.core.asset_lock_manager import AssetLockManager
from praxis.backend.core.scheduler import ProtocolScheduler
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class GlobalDependencies:
    """A class to hold global dependencies."""

    def __init__(self):
        self.scheduler: ProtocolScheduler | None = None
        self.asset_lock_manager: AssetLockManager | None = None

    async def initialize(
        self,
        db_session_factory,
        config: PraxisConfiguration = PraxisConfiguration(),
    ):
        """Initialize global scheduler components."""
        self.asset_lock_manager = AssetLockManager(config=config)
        await self.asset_lock_manager.initialize()
        logger.info("AssetLockManager initialized.")

        self.scheduler = ProtocolScheduler(
            db_session_factory=db_session_factory,
            asset_lock_manager=self.asset_lock_manager,
            config=config,
        )
        logger.info("Scheduler components initialized")


dependencies = GlobalDependencies()


def get_scheduler() -> ProtocolScheduler:
    """Get the global scheduler instance."""
    if dependencies.scheduler is None:
        raise RuntimeError("Scheduler not initialized")
    return dependencies.scheduler


def get_asset_manager() -> AssetLockManager:
    """Get the global asset manager instance."""
    if dependencies.asset_lock_manager is None:
        raise RuntimeError("Asset manager not initialized")
    return dependencies.asset_lock_manager
