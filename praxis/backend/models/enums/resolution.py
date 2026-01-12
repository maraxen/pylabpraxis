"""Enumerations for state resolution."""

from enum import Enum


class ResolutionActionEnum(Enum):
  """Actions taken after state resolution."""

  RESUME = "resume"  # Continue protocol execution
  ABORT = "abort"  # Stop protocol execution
  RETRY = "retry"  # Retry the failed operation


class ResolutionTypeEnum(Enum):
  """Types of state resolution."""

  CONFIRMED_SUCCESS = "confirmed_success"  # Effect actually happened
  CONFIRMED_FAILURE = "confirmed_failure"  # Effect did not happen
  PARTIAL = "partial"  # Effect partially happened
  ARBITRARY = "arbitrary"  # User specified custom values
  UNKNOWN = "unknown"  # User cannot determine
