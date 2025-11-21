"""Asset Manager package."""

from functools import partial

from praxis.backend.utils.errors import AssetAcquisitionError
from praxis.backend.utils.logging import (
  get_logger,
  log_async_runtime_errors,
  log_runtime_errors,
)

from .core import AssetManager

logger = get_logger(__name__)

async_asset_manager_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  raises_exception=AssetAcquisitionError,
)

asset_manager_errors = partial(
  log_runtime_errors,
  logger_instance=logger,
  raises_exception=AssetAcquisitionError,
)

__all__ = [
  "AssetManager",
  "asset_manager_errors",
  "async_asset_manager_errors",
  "logger",
]
