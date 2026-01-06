"""State resolution models and logic for handling protocol execution errors.

When a protocol operation fails, there is uncertainty about the state that was
supposed to be updated. This module provides:

1. Models to represent uncertain state changes
2. Logic to identify affected state using method contracts and computation graph
3. Resolution models for user-provided state corrections
4. Application logic to update simulation state based on resolutions

Example:
    After a failed dispense operation:
    - Did liquid leave the tip? Unknown
    - Did liquid enter the target well? Unknown

    The system identifies these uncertain states and prompts the user to resolve them.

"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from praxis.backend.core.simulation.method_contracts import (
  MethodContract,
  get_contract,
)
from praxis.backend.core.simulation.state_models import (
  BooleanLiquidState,
  ExactLiquidState,
  SimulationState,
)

# =============================================================================
# Resolution Types
# =============================================================================


class ResolutionType(Enum):
  """Types of state resolutions a user can provide."""

  CONFIRMED_SUCCESS = "confirmed_success"  # Effect actually happened as expected
  CONFIRMED_FAILURE = "confirmed_failure"  # Effect did not happen at all
  PARTIAL = "partial"  # Effect partially happened (e.g., partial volume)
  ARBITRARY = "arbitrary"  # User specifies custom value
  UNKNOWN = "unknown"  # User cannot determine - system uses conservative estimate


class StatePropertyType(Enum):
  """Types of state properties that can be uncertain."""

  VOLUME = "volume"  # Liquid volume in a container
  HAS_LIQUID = "has_liquid"  # Boolean: does container have liquid?
  HAS_TIP = "has_tip"  # Boolean: does tip rack position have a tip?
  TIP_LOADED = "tip_loaded"  # Boolean: is a tip loaded on machine channel?
  TEMPERATURE = "temperature"  # Temperature of a heated resource
  POSITION = "position"  # Position of a movable resource
  ARBITRARY = "arbitrary"  # Generic state property


# =============================================================================
# Uncertain State Models
# =============================================================================


@dataclass
class UncertainStateChange:
  """Represents state that may or may not have changed due to a failed operation.

  When an operation fails, we cannot be sure if the intended state change
  actually occurred. This model captures what state is uncertain and provides
  context for user resolution.

  Attributes:
      state_key: Unique key identifying the state property (e.g., "plate.A1.volume")
      current_value: Value from state snapshot before operation
      expected_value: Expected value if operation succeeded (if known)
      description: Human-readable description of the uncertain state
      resolution_type: Type of input needed for resolution
      resource_name: Name of the associated resource
      property_name: Name of the property that may have changed
      property_type: Type of the state property
      suggested_resolutions: List of common resolution options

  """

  state_key: str
  current_value: Any
  expected_value: Any | None = None
  description: str = ""
  resolution_type: str = "arbitrary"
  resource_name: str | None = None
  property_name: str | None = None
  property_type: StatePropertyType = StatePropertyType.ARBITRARY
  suggested_resolutions: list[str] = field(default_factory=list)

  def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for JSON serialization."""
    return {
      "state_key": self.state_key,
      "current_value": self.current_value,
      "expected_value": self.expected_value,
      "description": self.description,
      "resolution_type": self.resolution_type,
      "resource_name": self.resource_name,
      "property_name": self.property_name,
      "property_type": self.property_type.value,
      "suggested_resolutions": self.suggested_resolutions,
    }

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> UncertainStateChange:
    """Create from dictionary."""
    return cls(
      state_key=data["state_key"],
      current_value=data["current_value"],
      expected_value=data.get("expected_value"),
      description=data.get("description", ""),
      resolution_type=data.get("resolution_type", "arbitrary"),
      resource_name=data.get("resource_name"),
      property_name=data.get("property_name"),
      property_type=StatePropertyType(data.get("property_type", "arbitrary")),
      suggested_resolutions=data.get("suggested_resolutions", []),
    )


@dataclass
class StateResolution:
  """User's resolution of uncertain state changes.

  After viewing uncertain states, the user provides resolutions indicating
  what actually happened. This is used to update simulation state and
  logged for audit purposes.

  Attributes:
      operation_id: ID of the failed operation being resolved
      resolution_type: Overall resolution type (success, failure, partial, etc.)
      resolved_values: Mapping of state_key -> actual value as specified by user
      resolved_by: Identifier of who resolved (user ID or "system")
      resolved_at: Timestamp of resolution
      notes: Optional notes from the user about the resolution

  """

  operation_id: str
  resolution_type: ResolutionType
  resolved_values: dict[str, Any] = field(default_factory=dict)
  resolved_by: str = "user"
  resolved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
  notes: str | None = None

  def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for JSON serialization."""
    return {
      "operation_id": self.operation_id,
      "resolution_type": self.resolution_type.value,
      "resolved_values": self.resolved_values,
      "resolved_by": self.resolved_by,
      "resolved_at": self.resolved_at.isoformat(),
      "notes": self.notes,
    }

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> StateResolution:
    """Create from dictionary."""
    resolved_at = data.get("resolved_at")
    if isinstance(resolved_at, str):
      resolved_at = datetime.fromisoformat(resolved_at)
    elif resolved_at is None:
      resolved_at = datetime.now(timezone.utc)

    return cls(
      operation_id=data["operation_id"],
      resolution_type=ResolutionType(data["resolution_type"]),
      resolved_values=data.get("resolved_values", {}),
      resolved_by=data.get("resolved_by", "user"),
      resolved_at=resolved_at,
      notes=data.get("notes"),
    )


@dataclass
class OperationRecord:
  """Record of a failed operation for state resolution context.

  Attributes:
      operation_id: Unique ID of the operation
      method_name: Name of the method that failed (e.g., "dispense")
      receiver_type: Type of the receiver (e.g., "liquid_handler")
      args: Positional arguments as strings
      kwargs: Keyword arguments
      error_message: Error message from the failure
      error_type: Type of error (e.g., "PressureFault")

  """

  operation_id: str
  method_name: str
  receiver_type: str
  args: list[str] = field(default_factory=list)
  kwargs: dict[str, Any] = field(default_factory=dict)
  error_message: str = ""
  error_type: str = ""


# =============================================================================
# State Identification Logic
# =============================================================================


def identify_uncertain_states(
  failed_operation: OperationRecord,
  state_snapshot: SimulationState | None = None,
) -> list[UncertainStateChange]:
  """Identify uncertain states from a failed operation.

  This function determines what state may or may not have changed due to
  the failed operation. It uses method contracts when available for precise
  identification, falling back to generic analysis of operation arguments.

  Args:
      failed_operation: The operation that failed
      state_snapshot: Current simulation state (optional, for current values)

  Returns:
      List of UncertainStateChange representing affected state

  """
  uncertain: list[UncertainStateChange] = []

  # Try to get method contract for precise identification
  contract = get_contract(
    failed_operation.receiver_type,
    failed_operation.method_name,
  )

  if contract is not None:
    uncertain.extend(_identify_from_contract(failed_operation, contract, state_snapshot))
  else:
    # Fallback: generic analysis of operation arguments
    uncertain.extend(_identify_from_args_generic(failed_operation, state_snapshot))

  return uncertain


def _identify_from_contract(
  operation: OperationRecord,
  contract: MethodContract,
  state_snapshot: SimulationState | None,
) -> list[UncertainStateChange]:
  """Identify uncertain states using method contract definitions.

  Args:
      operation: The failed operation
      contract: Method contract defining expected effects
      state_snapshot: Current simulation state

  Returns:
      List of uncertain state changes based on contract effects

  """
  uncertain: list[UncertainStateChange] = []
  arg_map = _build_arg_map(operation, contract)

  # Check each effect type defined in the contract
  if contract.aspirates_from:
    source_name = arg_map.get(contract.aspirates_from, "unknown")
    volume = _get_volume_from_args(arg_map, contract.aspirate_volume_arg)

    current_value = None
    if state_snapshot and isinstance(state_snapshot.liquid_state, ExactLiquidState):
      current_value = state_snapshot.liquid_state.get_volume(source_name)

    uncertain.append(
      UncertainStateChange(
        state_key=f"{source_name}.volume",
        current_value=current_value,
        expected_value=(current_value - volume if current_value and volume else None),
        description=f"Volume in {source_name} after aspiration of {volume}µL",
        resolution_type="volume",
        resource_name=source_name,
        property_name="volume",
        property_type=StatePropertyType.VOLUME,
        suggested_resolutions=[
          "Confirm aspiration succeeded",
          "Confirm aspiration failed (volume unchanged)",
          "Enter actual volume remaining",
        ],
      )
    )

  if contract.dispenses_to:
    dest_name = arg_map.get(contract.dispenses_to, "unknown")
    volume = _get_volume_from_args(arg_map, contract.dispense_volume_arg)

    current_value = None
    if state_snapshot and isinstance(state_snapshot.liquid_state, ExactLiquidState):
      current_value = state_snapshot.liquid_state.get_volume(dest_name)

    uncertain.append(
      UncertainStateChange(
        state_key=f"{dest_name}.volume",
        current_value=current_value,
        expected_value=(current_value + volume if current_value and volume else None),
        description=f"Volume in {dest_name} after dispense of {volume}µL",
        resolution_type="volume",
        resource_name=dest_name,
        property_name="volume",
        property_type=StatePropertyType.VOLUME,
        suggested_resolutions=[
          "Confirm dispense succeeded",
          "Confirm dispense failed (volume unchanged)",
          "Enter actual volume in well",
        ],
      )
    )

  if contract.loads_tips:
    # Tip loading operation - use 'tips' from requires_on_deck if available
    tip_rack_name = "tip_rack"
    if contract.requires_on_deck:
      tip_rack_name = arg_map.get(contract.requires_on_deck[0], "tip_rack")

    uncertain.append(
      UncertainStateChange(
        state_key=f"{tip_rack_name}.tips",
        current_value=None,  # Would need tip state
        expected_value=None,
        description=f"Tip pick-up from {tip_rack_name}",
        resolution_type="boolean",
        resource_name=tip_rack_name,
        property_name="tips",
        property_type=StatePropertyType.HAS_TIP,
        suggested_resolutions=[
          "Confirm tips picked up successfully",
          "Confirm tips NOT picked up",
        ],
      )
    )

    # Also track tip loaded state on machine
    uncertain.append(
      UncertainStateChange(
        state_key="machine.tips_loaded",
        current_value=False,
        expected_value=True,
        description="Tips loaded on machine channels",
        resolution_type="boolean",
        resource_name=None,
        property_name="tips_loaded",
        property_type=StatePropertyType.TIP_LOADED,
        suggested_resolutions=[
          "Confirm tips are loaded",
          "Confirm tips are NOT loaded",
        ],
      )
    )

  if contract.drops_tips:
    # Tip drop operation
    uncertain.append(
      UncertainStateChange(
        state_key="machine.tips_loaded",
        current_value=True,
        expected_value=False,
        description="Tips dropped from machine channels",
        resolution_type="boolean",
        resource_name=None,
        property_name="tips_loaded",
        property_type=StatePropertyType.TIP_LOADED,
        suggested_resolutions=[
          "Confirm tips were dropped",
          "Confirm tips are still loaded",
        ],
      )
    )

  return uncertain


def _identify_from_args_generic(
  operation: OperationRecord,
  state_snapshot: SimulationState | None,
) -> list[UncertainStateChange]:
  """Fallback identification when no method contract exists.

  Analyzes operation arguments to identify resources that may have been
  affected, marking all their mutable properties as potentially uncertain.

  Args:
      operation: The failed operation
      state_snapshot: Current simulation state

  Returns:
      List of uncertain state changes based on argument analysis

  """
  uncertain: list[UncertainStateChange] = []

  # Extract resource references from args
  for i, arg in enumerate(operation.args):
    # Skip obvious non-resource arguments (numbers, strings)
    if _looks_like_resource_ref(arg):
      uncertain.append(
        UncertainStateChange(
          state_key=f"{arg}.state",
          current_value=None,
          expected_value=None,
          description=f"State of {arg} may have changed (arg {i})",
          resolution_type="arbitrary",
          resource_name=arg,
          property_name="state",
          property_type=StatePropertyType.ARBITRARY,
          suggested_resolutions=[
            "Inspect resource and confirm state",
          ],
        )
      )

  # Check kwargs for resource references
  for key, value in operation.kwargs.items():
    if isinstance(value, str) and _looks_like_resource_ref(value):
      uncertain.append(
        UncertainStateChange(
          state_key=f"{value}.state",
          current_value=None,
          expected_value=None,
          description=f"State of {value} may have changed ({key}=)",
          resolution_type="arbitrary",
          resource_name=value,
          property_name="state",
          property_type=StatePropertyType.ARBITRARY,
          suggested_resolutions=[
            "Inspect resource and confirm state",
          ],
        )
      )

  return uncertain


def _looks_like_resource_ref(value: str) -> bool:
  """Check if a string value looks like a resource reference."""
  if not isinstance(value, str):
    return False
  # Skip numeric strings
  try:
    float(value)
    return False
  except ValueError:
    pass
  # Skip common non-resource strings
  if value.lower() in ("true", "false", "none", "null"):
    return False
  # Resource refs typically have dots or brackets
  return "." in value or "[" in value or value.isidentifier()


def _build_arg_map(
  operation: OperationRecord,
  contract: MethodContract,
) -> dict[str, Any]:
  """Build a mapping of argument names to values.

  Uses contract parameter names and operation args/kwargs to create
  a unified argument mapping.

  Args:
      operation: The operation record
      contract: Method contract with parameter info

  Returns:
      Dictionary mapping parameter names to values

  """
  arg_map: dict[str, Any] = {}

  # Common PLR argument naming patterns
  common_param_names = [
    "source",
    "dest",
    "resource",
    "tip_rack",
    "volume",
    "wells",
    "channels",
  ]

  # Map positional args to common names
  for i, arg in enumerate(operation.args):
    if i < len(common_param_names):
      arg_map[common_param_names[i]] = arg

  # Override with kwargs
  arg_map.update(operation.kwargs)

  return arg_map


def _get_volume_from_args(
  arg_map: dict[str, Any],
  volume_arg_name: str | None,
) -> float | None:
  """Extract volume value from argument map.

  Args:
      arg_map: Mapping of argument names to values
      volume_arg_name: Name of the volume argument

  Returns:
      Volume as float, or None if not found

  """
  if volume_arg_name is None:
    # Try common names
    for name in ("volume", "vol", "vols"):
      if name in arg_map:
        return _parse_volume(arg_map[name])
    return None

  if volume_arg_name in arg_map:
    return _parse_volume(arg_map[volume_arg_name])

  return None


def _parse_volume(value: Any) -> float | None:
  """Parse a volume value to float."""
  if isinstance(value, int | float):
    return float(value)
  if isinstance(value, str):
    try:
      return float(value)
    except ValueError:
      return None
  return None


# =============================================================================
# Resolution Application
# =============================================================================


def apply_resolution(
  resolution: StateResolution,
  state: SimulationState,
) -> SimulationState:
  """Apply a user's resolution to update simulation state.

  This function takes the user's resolution of uncertain states and
  updates the simulation state accordingly.

  Args:
      resolution: User's state resolution
      state: Current simulation state

  Returns:
      Updated simulation state

  """
  # Create a copy to avoid mutating the original
  # Note: For now, we update in place since SimulationState doesn't have copy()
  # TODO: Implement proper state copying if needed

  for state_key, value in resolution.resolved_values.items():
    _apply_single_resolution(state, state_key, value)

  return state


def _apply_single_resolution(
  state: SimulationState,
  state_key: str,
  value: Any,
) -> None:
  """Apply a single state resolution.

  Args:
      state: Simulation state to update
      state_key: Key identifying the state property (e.g., "plate.A1.volume")
      value: New value to set

  """
  # Parse state key
  parts = state_key.split(".")
  if len(parts) < 2:
    return

  resource_name = parts[0]
  property_name = parts[-1]

  # Apply based on property type
  if property_name == "volume" and isinstance(state.liquid_state, ExactLiquidState):
    if isinstance(value, int | float):
      state.liquid_state.set_volume(resource_name, float(value))

  elif property_name in ("has_liquid", "liquid"):
    if isinstance(state.liquid_state, BooleanLiquidState):
      state.liquid_state.set_has_liquid(resource_name, bool(value))

  elif property_name == "tips_loaded":
    if bool(value):
      state.tip_state.load_tips()
    else:
      state.tip_state.drop_tips()
