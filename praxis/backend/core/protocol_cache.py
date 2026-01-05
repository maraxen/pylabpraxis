"""Protocol caching infrastructure using cloudpickle.

This module provides serialization of protocol functions and tracer infrastructure
for caching and cross-platform execution. It handles three use cases:

1. **Backend caching**: Pickle functions for faster re-execution
2. **Distributed execution**: Send pickled functions to worker processes
3. **Browser-compatible**: Pickle tracer infrastructure (no hardware deps)

All operations provide clear error messages on failure, failing early
when possible to avoid cryptic errors later in the pipeline.
"""

from __future__ import annotations

import hashlib
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

import cloudpickle

logger = logging.getLogger(__name__)


# Version for cache invalidation when serialization format changes
CACHE_VERSION = "1.0.0"


# =============================================================================
# Error Types
# =============================================================================


class ProtocolCacheError(Exception):
  """Base exception for protocol caching errors."""

  pass


class SerializationError(ProtocolCacheError):
  """Raised when cloudpickle serialization fails.

  This typically happens when the function captures unpickleable objects
  like open file handles, database connections, or hardware interfaces.
  """

  def __init__(self, func_name: str, original_error: Exception) -> None:
    self.func_name = func_name
    self.original_error = original_error
    super().__init__(
      f"Failed to serialize function '{func_name}': {original_error}\n"
      f"This usually means the function captures unpickleable objects "
      f"(file handles, connections, hardware interfaces)."
    )


class DeserializationError(ProtocolCacheError):
  """Raised when cloudpickle deserialization fails.

  This typically happens due to:
  - Python version mismatch
  - Missing modules in the target environment
  - Corrupted bytecode
  """

  def __init__(self, reason: str, original_error: Exception | None = None) -> None:
    self.reason = reason
    self.original_error = original_error
    msg = f"Failed to deserialize protocol: {reason}"
    if original_error:
      msg += f"\nOriginal error: {original_error}"
    super().__init__(msg)


class CacheValidationError(ProtocolCacheError):
  """Raised when cache validation fails."""

  def __init__(self, reason: str) -> None:
    self.reason = reason
    super().__init__(f"Cache validation failed: {reason}")


# =============================================================================
# Cache Result Types
# =============================================================================


@dataclass
class CachedProtocol:
  """Result of caching a protocol function."""

  bytecode: bytes
  """Cloudpickle serialized function"""

  source_hash: str
  """SHA-256 hash of source code for invalidation"""

  python_version: str
  """Python version used for pickling"""

  cache_version: str
  """Cache format version"""

  created_at: datetime
  """When the cache was created"""

  function_name: str
  """Name of the cached function"""

  module_name: str
  """Module where function is defined"""

  def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for storage."""
    return {
      "bytecode": self.bytecode,  # bytes stored directly
      "source_hash": self.source_hash,
      "python_version": self.python_version,
      "cache_version": self.cache_version,
      "created_at": self.created_at.isoformat(),
      "function_name": self.function_name,
      "module_name": self.module_name,
    }


@dataclass
class CacheValidationResult:
  """Result of validating a cached protocol."""

  is_valid: bool
  """Whether the cache is valid for use"""

  reason: str | None = None
  """Why the cache is invalid (if is_valid=False)"""

  warnings: list[str] | None = None
  """Non-fatal warnings about the cache"""


# =============================================================================
# Protocol Cache
# =============================================================================


class ProtocolCache:
  """Manages protocol function caching using cloudpickle.

  This class provides methods to:
  - Serialize protocol functions for caching
  - Validate cached bytecode before use
  - Deserialize and execute cached functions
  - Track Python versions for compatibility

  Usage:
      cache = ProtocolCache()

      # Cache a function
      try:
          cached = cache.cache_protocol(my_func, source_code)
          store_in_db(cached.bytecode, cached.source_hash)
      except SerializationError as e:
          logger.warning(f"Cannot cache {e.func_name}: {e}")

      # Load and execute cached function
      try:
          func = cache.load_protocol(bytecode)
          result = await func(**args)
      except DeserializationError as e:
          logger.error(f"Cache corrupted: {e}")
          # Fall back to importing module directly

  """

  def __init__(self) -> None:
    """Initialize the cache."""
    self._python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

  def cache_protocol(
    self,
    protocol_func: Callable[..., Any],
    source_code: str | None = None,
  ) -> CachedProtocol:
    """Serialize a protocol function for caching.

    Args:
        protocol_func: The protocol function to cache.
        source_code: Optional source code for hash-based invalidation.

    Returns:
        CachedProtocol with bytecode and metadata.

    Raises:
        SerializationError: If the function cannot be pickled.

    """
    func_name = getattr(protocol_func, "__name__", "<unknown>")
    module_name = getattr(protocol_func, "__module__", "<unknown>")

    # Attempt serialization
    try:
      bytecode = cloudpickle.dumps(protocol_func)
    except Exception as e:
      raise SerializationError(func_name, e) from e

    # Compute source hash if provided
    source_hash = ""
    if source_code:
      source_hash = hashlib.sha256(source_code.encode()).hexdigest()

    return CachedProtocol(
      bytecode=bytecode,
      source_hash=source_hash,
      python_version=self._python_version,
      cache_version=CACHE_VERSION,
      created_at=datetime.now(timezone.utc),
      function_name=func_name,
      module_name=module_name,
    )

  def validate_cache(
    self,
    bytecode: bytes,
    source_hash: str | None = None,
    current_source_hash: str | None = None,
    cached_python_version: str | None = None,
    cached_cache_version: str | None = None,
  ) -> CacheValidationResult:
    """Validate cached bytecode before attempting to load it.

    Performs early validation to catch issues before deserialization.

    Args:
        bytecode: The cached bytecode to validate.
        source_hash: Hash stored with the cache.
        current_source_hash: Hash of current source (for staleness check).
        cached_python_version: Python version when cache was created.
        cached_cache_version: Cache format version.

    Returns:
        CacheValidationResult indicating if cache is usable.

    """
    warnings: list[str] = []

    # Check bytecode is not empty
    if not bytecode:
      return CacheValidationResult(
        is_valid=False,
        reason="Cached bytecode is empty",
      )

    # Check cache version
    if cached_cache_version and cached_cache_version != CACHE_VERSION:
      return CacheValidationResult(
        is_valid=False,
        reason=f"Cache version mismatch: cached={cached_cache_version}, current={CACHE_VERSION}",
      )

    # Check Python version (major.minor must match)
    if cached_python_version:
      cached_major_minor = ".".join(cached_python_version.split(".")[:2])
      current_major_minor = f"{sys.version_info.major}.{sys.version_info.minor}"

      if cached_major_minor != current_major_minor:
        return CacheValidationResult(
          is_valid=False,
          reason=f"Python version mismatch: cached={cached_python_version}, current={self._python_version}. "
          f"Bytecode is not compatible across Python minor versions.",
        )

      # Warn on micro version difference
      if cached_python_version != self._python_version:
        warnings.append(
          f"Python micro version differs: cached={cached_python_version}, current={self._python_version}"
        )

    # Check source hash for staleness
    if source_hash and current_source_hash:
      if source_hash != current_source_hash:
        return CacheValidationResult(
          is_valid=False,
          reason="Source code has changed since cache was created",
        )

    return CacheValidationResult(
      is_valid=True,
      warnings=warnings if warnings else None,
    )

  def load_protocol(
    self,
    bytecode: bytes,
    validate: bool = True,
    cached_python_version: str | None = None,
    cached_cache_version: str | None = None,
  ) -> Callable[..., Any]:
    """Deserialize a cached protocol function.

    Args:
        bytecode: The cloudpickle bytecode to deserialize.
        validate: Whether to run validation before loading.
        cached_python_version: Python version when cached (for validation).
        cached_cache_version: Cache version (for validation).

    Returns:
        The deserialized protocol function.

    Raises:
        DeserializationError: If loading fails.
        CacheValidationError: If validation fails (when validate=True).

    """
    # Validate first if requested
    if validate:
      validation = self.validate_cache(
        bytecode=bytecode,
        cached_python_version=cached_python_version,
        cached_cache_version=cached_cache_version,
      )
      if not validation.is_valid:
        raise CacheValidationError(validation.reason or "Unknown validation error")
      if validation.warnings:
        for warning in validation.warnings:
          logger.warning("Cache warning: %s", warning)

    # Attempt deserialization
    try:
      func = cloudpickle.loads(bytecode)
    except ModuleNotFoundError as e:
      raise DeserializationError(
        f"Missing module: {e.name}. The cached function depends on a module "
        f"that is not available in this environment.",
        e,
      ) from e
    except Exception as e:
      raise DeserializationError(
        f"Cloudpickle deserialization failed: {type(e).__name__}",
        e,
      ) from e

    if not callable(func):
      raise DeserializationError(
        f"Deserialized object is not callable: {type(func).__name__}"
      )

    return func

  def is_cache_valid(
    self,
    source_code: str,
    cached_hash: str,
  ) -> bool:
    """Quick check if cache is valid based on source hash.

    Args:
        source_code: Current source code.
        cached_hash: Hash stored with cache.

    Returns:
        True if source hasn't changed.

    """
    current_hash = hashlib.sha256(source_code.encode()).hexdigest()
    return current_hash == cached_hash


# =============================================================================
# Tracer Serialization (Browser-Compatible)
# =============================================================================


class TracerCache:
  """Serialization for tracer infrastructure (browser-compatible).

  Unlike full protocol functions, tracers don't depend on PLR hardware
  modules and can be safely pickled for use in Pyodide.

  This enables browser-side simulation using our tracer infrastructure
  without needing to import actual PLR modules.
  """

  def serialize_tracer_state(
    self,
    state: Any,
  ) -> bytes:
    """Serialize simulation state for browser use.

    Args:
        state: SimulationState or similar tracer state object.

    Returns:
        Cloudpickle bytecode.

    Raises:
        SerializationError: If serialization fails.

    """
    try:
      return cloudpickle.dumps(state)
    except Exception as e:
      raise SerializationError("tracer_state", e) from e

  def deserialize_tracer_state(
    self,
    bytecode: bytes,
  ) -> Any:
    """Deserialize tracer state.

    Args:
        bytecode: Cloudpickle bytecode.

    Returns:
        Deserialized state object.

    Raises:
        DeserializationError: If deserialization fails.

    """
    try:
      return cloudpickle.loads(bytecode)
    except Exception as e:
      raise DeserializationError(
        "Failed to deserialize tracer state",
        e,
      ) from e


# =============================================================================
# Convenience Functions
# =============================================================================


def cache_protocol(
  protocol_func: Callable[..., Any],
  source_code: str | None = None,
) -> CachedProtocol:
  """Convenience function to cache a protocol.

  Args:
      protocol_func: The function to cache.
      source_code: Optional source for hash-based invalidation.

  Returns:
      CachedProtocol with bytecode and metadata.

  """
  cache = ProtocolCache()
  return cache.cache_protocol(protocol_func, source_code)


def load_protocol(bytecode: bytes) -> Callable[..., Any]:
  """Convenience function to load a cached protocol.

  Args:
      bytecode: The cloudpickle bytecode.

  Returns:
      The deserialized function.

  """
  cache = ProtocolCache()
  return cache.load_protocol(bytecode)
