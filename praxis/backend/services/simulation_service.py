"""Protocol simulation service for running state simulation on discovered protocols.

This service integrates the simulation infrastructure with the protocol discovery
pipeline, enabling automatic simulation and caching of results.

It also provides cloudpickle-based bytecode caching for:
- Faster protocol re-execution (no import needed)
- Distributed execution (send pickled functions to workers)
- Early validation with clear error messages
"""

from __future__ import annotations

import importlib
import inspect
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from praxis.backend.core.protocol_cache import (
  CacheValidationError,
  DeserializationError,
  ProtocolCache,
  SerializationError,
)
from praxis.backend.core.simulation import (
  SIMULATION_VERSION,
  ProtocolSimulationResult,
  ProtocolSimulator,
  is_cache_valid,
)

if TYPE_CHECKING:
  from collections.abc import Callable

  from sqlalchemy.ext.asyncio import AsyncSession

  from praxis.backend.models.orm.protocol import FunctionProtocolDefinitionOrm

logger = logging.getLogger(__name__)


class SimulationService:
  """Service for running and caching protocol simulations.

  This service integrates with protocol discovery to run state simulation
  on discovered protocols and cache the results for later use.

  It also provides cloudpickle-based bytecode caching with:
  - Early validation (Python version, cache version checks)
  - Clear error messages on failure
  - Source hash-based invalidation

  Usage:
      service = SimulationService()

      # Simulate a single protocol
      result = await service.simulate_protocol(protocol_orm, session)

      # Simulate all protocols that need it
      await service.simulate_pending_protocols(session, protocol_orms)

      # Get protocol function (from cache or import)
      func = await service.get_protocol_function(protocol_orm)

  """

  def __init__(
    self,
    enable_failure_detection: bool = True,
    max_failure_states: int = 50,
    enable_bytecode_cache: bool = True,
  ) -> None:
    """Initialize the simulation service.

    Args:
        enable_failure_detection: Whether to run failure mode detection.
        max_failure_states: Maximum states to explore for failure detection.
        enable_bytecode_cache: Whether to cache protocol bytecode.

    """
    self._simulator = ProtocolSimulator(
      enable_failure_detection=enable_failure_detection,
      max_failure_states=max_failure_states,
    )
    self._enable_bytecode_cache = enable_bytecode_cache
    self._protocol_cache = ProtocolCache() if enable_bytecode_cache else None

  async def simulate_protocol(
    self,
    protocol_orm: FunctionProtocolDefinitionOrm,
    session: AsyncSession,
    force_resimulate: bool = False,
  ) -> ProtocolSimulationResult | None:
    """Run simulation on a protocol and cache results.

    Args:
        protocol_orm: The protocol definition ORM object.
        session: Database session for saving results.
        force_resimulate: If True, run simulation even if cache is valid.

    Returns:
        ProtocolSimulationResult if successful, None if simulation failed.

    """
    # Check if cache is valid
    if not force_resimulate and is_cache_valid(
      cached_version=protocol_orm.simulation_version,
      source_hash=protocol_orm.source_hash,
      current_source_hash=protocol_orm.source_hash,
    ):
      logger.debug(
        "Simulation cache valid for %s, skipping re-simulation",
        protocol_orm.fqn,
      )
      # Return cached result if available
      if protocol_orm.simulation_result_json:
        return ProtocolSimulationResult.from_cache_dict(
          protocol_orm.simulation_result_json
        )
      return None

    # Try to import and get the protocol function
    protocol_func = self._get_protocol_function(protocol_orm)
    if protocol_func is None:
      logger.warning(
        "Could not import protocol function %s for simulation",
        protocol_orm.fqn,
      )
      return None

    # Extract parameter types from assets and parameters
    parameter_types = self._extract_parameter_types(protocol_orm)

    if not parameter_types:
      logger.warning(
        "No parameter types found for protocol %s, skipping simulation",
        protocol_orm.fqn,
      )
      return None

    # Run simulation
    try:
      result = await self._simulator.analyze_protocol(
        protocol_func=protocol_func,
        parameter_types=parameter_types,
      )

      # Cache results to ORM (including bytecode)
      await self._cache_results(protocol_orm, result, session, protocol_func)

      logger.info(
        "Simulation completed for %s: passed=%s, violations=%d, failure_modes=%d",
        protocol_orm.fqn,
        result.passed,
        len(result.violations),
        len(result.failure_modes),
      )

      return result

    except Exception as e:
      logger.exception(
        "Simulation failed for protocol %s: %s",
        protocol_orm.fqn,
        e,
      )
      return None

  async def simulate_pending_protocols(
    self,
    session: AsyncSession,
    protocol_orms: list[FunctionProtocolDefinitionOrm],
    force_resimulate: bool = False,
  ) -> dict[str, ProtocolSimulationResult | None]:
    """Run simulation on multiple protocols.

    Args:
        session: Database session.
        protocol_orms: List of protocol ORM objects to simulate.
        force_resimulate: If True, run simulation even if cache is valid.

    Returns:
        Dictionary mapping FQN to simulation result.

    """
    results: dict[str, ProtocolSimulationResult | None] = {}

    for protocol_orm in protocol_orms:
      result = await self.simulate_protocol(
        protocol_orm=protocol_orm,
        session=session,
        force_resimulate=force_resimulate,
      )
      results[protocol_orm.fqn] = result

    return results

  def _get_protocol_function(
    self,
    protocol_orm: FunctionProtocolDefinitionOrm,
  ) -> Callable[..., Any] | None:
    """Import the module and get the protocol function.

    Args:
        protocol_orm: Protocol definition ORM object.

    Returns:
        The protocol function if found, None otherwise.

    """
    try:
      module = importlib.import_module(protocol_orm.module_name)
      func = getattr(module, protocol_orm.function_name, None)

      if func is None:
        logger.warning(
          "Function %s not found in module %s",
          protocol_orm.function_name,
          protocol_orm.module_name,
        )
        return None

      if not callable(func):
        logger.warning(
          "Attribute %s in module %s is not callable",
          protocol_orm.function_name,
          protocol_orm.module_name,
        )
        return None

      return func

    except ImportError as e:
      logger.warning(
        "Could not import module %s: %s",
        protocol_orm.module_name,
        e,
      )
      return None
    except Exception as e:
      logger.exception(
        "Unexpected error importing %s.%s: %s",
        protocol_orm.module_name,
        protocol_orm.function_name,
        e,
      )
      return None

  def _extract_parameter_types(
    self,
    protocol_orm: FunctionProtocolDefinitionOrm,
  ) -> dict[str, str]:
    """Extract parameter types from protocol definition.

    Combines asset requirements and regular parameters into a single
    type mapping for simulation.

    Args:
        protocol_orm: Protocol definition ORM object.

    Returns:
        Dictionary mapping parameter names to type hints.

    """
    parameter_types: dict[str, str] = {}

    # Add assets (resources and machines)
    for asset in protocol_orm.assets:
      # Use actual_type_str which is the resolved type
      parameter_types[asset.name] = asset.actual_type_str or asset.type_hint_str

    # Add regular parameters
    for param in protocol_orm.parameters:
      parameter_types[param.name] = param.type_hint

    return parameter_types

  async def _cache_results(
    self,
    protocol_orm: FunctionProtocolDefinitionOrm,
    result: ProtocolSimulationResult,
    session: AsyncSession,
    protocol_func: Callable[..., Any] | None = None,
  ) -> None:
    """Cache simulation results to the database.

    Args:
        protocol_orm: Protocol definition ORM object.
        result: Simulation result to cache.
        session: Database session.
        protocol_func: Optional protocol function for bytecode caching.

    """
    # Update ORM fields
    protocol_orm.simulation_result_json = result.to_cache_dict()
    protocol_orm.inferred_requirements_json = [
      req.model_dump(mode="json") for req in result.inferred_requirements
    ]
    protocol_orm.failure_modes_json = [
      mode.model_dump(mode="json") for mode in result.failure_modes
    ]
    protocol_orm.simulation_version = SIMULATION_VERSION
    protocol_orm.simulation_cached_at = datetime.now(timezone.utc)

    # Cache bytecode if enabled and function available
    if protocol_func and self._enable_bytecode_cache:
      await self._cache_bytecode(protocol_orm, protocol_func)

    # Save to database
    session.add(protocol_orm)
    await session.commit()

  async def _cache_bytecode(
    self,
    protocol_orm: FunctionProtocolDefinitionOrm,
    protocol_func: Callable[..., Any],
  ) -> bool:
    """Cache protocol function bytecode using cloudpickle.

    Args:
        protocol_orm: Protocol definition ORM object.
        protocol_func: The protocol function to cache.

    Returns:
        True if caching succeeded, False otherwise.

    """
    if not self._protocol_cache:
      return False

    try:
      # Get source code for hash
      source_code = self._get_source_code(protocol_func)

      # Cache the function
      cached = self._protocol_cache.cache_protocol(protocol_func, source_code)

      # Update ORM fields
      protocol_orm.cached_bytecode = cached.bytecode
      protocol_orm.bytecode_python_version = cached.python_version
      protocol_orm.bytecode_cache_version = cached.cache_version
      protocol_orm.bytecode_cached_at = cached.created_at

      logger.info(
        "Bytecode cached for %s (%d bytes, Python %s)",
        protocol_orm.fqn,
        len(cached.bytecode),
        cached.python_version,
      )
      return True

    except SerializationError as e:
      # Clear error message - function captures unpickleable objects
      logger.warning(
        "Cannot cache bytecode for %s: %s. "
        "This is non-fatal; protocol will be imported from module at runtime.",
        protocol_orm.fqn,
        e,
      )
      return False

    except Exception as e:
      logger.warning(
        "Unexpected error caching bytecode for %s: %s",
        protocol_orm.fqn,
        e,
      )
      return False

  def _get_source_code(self, func: Callable[..., Any]) -> str | None:
    """Get source code for a function if available.

    Args:
        func: The function to get source for.

    Returns:
        Source code string or None if not available.

    """
    try:
      return inspect.getsource(func)
    except (OSError, TypeError):
      return None

  async def get_protocol_function(
    self,
    protocol_orm: FunctionProtocolDefinitionOrm,
    prefer_cache: bool = True,
  ) -> Callable[..., Any] | None:
    """Get protocol function from cache or import.

    This method provides a unified way to get protocol functions:
    1. First tries to load from bytecode cache (if enabled and valid)
    2. Falls back to importing from module

    Args:
        protocol_orm: Protocol definition ORM object.
        prefer_cache: If True, prefer cached bytecode over import.

    Returns:
        The protocol function or None if not found.

    """
    # Try cache first if enabled and preferred
    if prefer_cache and self._protocol_cache and protocol_orm.cached_bytecode:
      func = self._load_from_cache(protocol_orm)
      if func is not None:
        return func
      # If cache load failed, fall through to import

    # Fall back to import
    return self._get_protocol_function(protocol_orm)

  def _load_from_cache(
    self,
    protocol_orm: FunctionProtocolDefinitionOrm,
  ) -> Callable[..., Any] | None:
    """Load protocol function from bytecode cache.

    Performs early validation and returns clear error messages.

    Args:
        protocol_orm: Protocol definition ORM object.

    Returns:
        The deserialized function or None if loading failed.

    """
    if not self._protocol_cache or not protocol_orm.cached_bytecode:
      return None

    try:
      # Validate cache first (catches Python version mismatches early)
      validation = self._protocol_cache.validate_cache(
        bytecode=protocol_orm.cached_bytecode,
        cached_python_version=protocol_orm.bytecode_python_version,
        cached_cache_version=protocol_orm.bytecode_cache_version,
      )

      if not validation.is_valid:
        logger.info(
          "Bytecode cache invalid for %s: %s. Will re-import from module.",
          protocol_orm.fqn,
          validation.reason,
        )
        return None

      if validation.warnings:
        for warning in validation.warnings:
          logger.debug("Cache warning for %s: %s", protocol_orm.fqn, warning)

      # Load the function
      func = self._protocol_cache.load_protocol(
        bytecode=protocol_orm.cached_bytecode,
        validate=False,  # Already validated above
      )

      logger.debug(
        "Loaded %s from bytecode cache",
        protocol_orm.fqn,
      )
      return func

    except CacheValidationError as e:
      logger.info(
        "Cache validation failed for %s: %s",
        protocol_orm.fqn,
        e.reason,
      )
      return None

    except DeserializationError as e:
      logger.warning(
        "Failed to deserialize %s from cache: %s. "
        "This may indicate a corrupted cache or missing dependencies.",
        protocol_orm.fqn,
        e.reason,
      )
      return None

    except Exception as e:
      logger.warning(
        "Unexpected error loading %s from cache: %s",
        protocol_orm.fqn,
        e,
      )
      return None


# =============================================================================
# Convenience Functions
# =============================================================================


async def simulate_protocol(
  protocol_orm: FunctionProtocolDefinitionOrm,
  session: AsyncSession,
  force_resimulate: bool = False,
) -> ProtocolSimulationResult | None:
  """Convenience function to simulate a single protocol.

  Args:
      protocol_orm: Protocol definition ORM object.
      session: Database session.
      force_resimulate: If True, run simulation even if cache is valid.

  Returns:
      ProtocolSimulationResult if successful, None otherwise.

  """
  service = SimulationService()
  return await service.simulate_protocol(
    protocol_orm=protocol_orm,
    session=session,
    force_resimulate=force_resimulate,
  )
