"""State-aware tracers for protocol simulation.

This module extends the base tracing infrastructure with state tracking,
enabling validation of preconditions and application of effects during
symbolic protocol execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from praxis.backend.core.simulation.method_contracts import (
  MethodContract,
  get_contract,
)
from praxis.backend.core.simulation.state_models import (
  BooleanLiquidState,
  ExactLiquidState,
  SimulationState,
  StateLevel,
  StateViolation,
  SymbolicLiquidState,
  ViolationType,
)
from praxis.backend.core.tracing.tracers import (
  TracedMachine,
  TracedMethodResult,
  TracedResource,
  TracedValue,
  TracedWell,
  TracedWellCollection,
)

# =============================================================================
# Stateful Traced Machine
# =============================================================================


@dataclass
class StatefulTracedMachine(TracedMachine):
  """Machine tracer that tracks and validates state.

  Extends TracedMachine to:
  1. Check preconditions before each operation
  2. Apply effects after each operation
  3. Collect violations for reporting

  This enables detection of issues like:
  - Aspirating without tips loaded
  - Aspirating from empty wells
  - Dispensing to full wells
  """

  state: SimulationState = field(default_factory=SimulationState.default_boolean)
  """Current simulation state"""

  violations: list[StateViolation] = field(default_factory=list)
  """Collected violations during execution"""

  continue_on_violation: bool = True
  """Whether to continue execution after a violation"""

  _op_counter: int = field(default=0, init=False)
  """Counter for generating operation IDs"""

  def _generate_op_id(self) -> str:
    """Generate a unique operation ID."""
    self._op_counter += 1
    return f"sim_op_{self._op_counter}"

  def __getattr__(self, name: str) -> Any:
    """Intercept method calls to check preconditions and apply effects."""
    # Skip internal attributes
    if name.startswith("_"):
      raise AttributeError(name)

    def method_proxy(*args: Any, **kwargs: Any) -> TracedMethodResult:
      """Check preconditions, record operation, apply effects."""
      op_id = self._generate_op_id()

      # Get method contract
      contract = get_contract(self.machine_type, name)

      if contract:
        # Check preconditions
        violations = self._check_preconditions(op_id, name, contract, args, kwargs)
        self.violations.extend(violations)

        if violations and not self.continue_on_violation:
          # Return early without applying effects
          return TracedMethodResult(
            name=f"{self.name}.{name}()",
            recorder=self.recorder,
            declared_type="Any",
            operation_id=op_id,
          )

        # Apply effects (even if violation, to continue simulation)
        self._apply_effects(name, contract, args, kwargs)

      # Convert traced arguments to their symbolic names
      recorded_args = []
      for arg in args:
        if isinstance(arg, TracedValue):
          recorded_args.append(arg.name)
        else:
          recorded_args.append(repr(arg))

      recorded_kwargs = {}
      for k, v in kwargs.items():
        if isinstance(v, TracedValue):
          recorded_kwargs[k] = v.name
        else:
          recorded_kwargs[k] = repr(v)

      # Record the operation
      self.recorder.record_operation(
        receiver=self.name,
        receiver_type=self.machine_type,
        method=name,
        args=recorded_args,
        kwargs=recorded_kwargs,
      )

      return TracedMethodResult(
        name=f"{self.name}.{name}()",
        recorder=self.recorder,
        declared_type="Any",
        operation_id=op_id,
      )

    return method_proxy

  def _check_preconditions(
    self,
    op_id: str,
    method_name: str,
    contract: MethodContract,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> list[StateViolation]:
    """Check preconditions for an operation.

    Args:
        op_id: Operation identifier
        method_name: Name of the method
        contract: Method contract
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        List of violations found

    """
    violations: list[StateViolation] = []

    # Build argument mapping for contract checking
    arg_map = self._build_arg_map(contract, args, kwargs)

    # Check tips requirement
    if contract.requires_tips:
      if not self.state.tip_state.tips_loaded:
        violations.append(
          StateViolation(
            violation_type=ViolationType.TIPS_NOT_LOADED,
            operation_id=op_id,
            method_name=method_name,
            message=f"Method '{method_name}' requires tips to be loaded",
            suggested_fix="Add pick_up_tips() before this operation",
            state_level=self.state.level,
          )
        )

      # Check tip count if specified
      if contract.requires_tips_count:
        if self.state.tip_state.tips_count < contract.requires_tips_count:
          violations.append(
            StateViolation(
              violation_type=ViolationType.INSUFFICIENT_TIPS,
              operation_id=op_id,
              method_name=method_name,
              message=f"Method '{method_name}' requires {contract.requires_tips_count} tips, "
              f"but only {self.state.tip_state.tips_count} loaded",
              suggested_fix=f"Use pick_up_tips96() or ensure {contract.requires_tips_count} tips",
              state_level=self.state.level,
              details={
                "required": contract.requires_tips_count,
                "loaded": self.state.tip_state.tips_count,
              },
            )
          )

    # Check deck placement
    for arg_name in contract.requires_on_deck:
      resource = arg_map.get(arg_name)
      if resource:
        resource_name = self._get_resource_name(resource)
        if not self.state.deck_state.is_on_deck(resource_name):
          violations.append(
            StateViolation(
              violation_type=ViolationType.RESOURCE_NOT_ON_DECK,
              operation_id=op_id,
              method_name=method_name,
              resource_name=resource_name,
              message=f"Resource '{resource_name}' must be on deck for '{method_name}'",
              suggested_fix=f"Place '{resource_name}' on deck before this operation",
              state_level=self.state.level,
            )
          )

    # Check liquid requirements
    if contract.requires_liquid_in:
      resource = arg_map.get(contract.requires_liquid_in)
      if resource:
        resource_name = self._get_resource_name(resource)
        violation = self._check_liquid_present(op_id, method_name, resource_name)
        if violation:
          violations.append(violation)

    # Check capacity requirements
    if contract.requires_capacity_in:
      resource = arg_map.get(contract.requires_capacity_in)
      if resource:
        resource_name = self._get_resource_name(resource)
        violation = self._check_capacity_present(op_id, method_name, resource_name)
        if violation:
          violations.append(violation)

    return violations

  def _check_liquid_present(
    self,
    op_id: str,
    method_name: str,
    resource_name: str,
  ) -> StateViolation | None:
    """Check if liquid is present at appropriate precision level."""
    liquid_state = self.state.liquid_state

    if isinstance(liquid_state, BooleanLiquidState):
      if not liquid_state.check_has_liquid(resource_name):
        return StateViolation(
          violation_type=ViolationType.NO_LIQUID,
          operation_id=op_id,
          method_name=method_name,
          resource_name=resource_name,
          message=f"Resource '{resource_name}' has no liquid",
          suggested_fix=f"Ensure '{resource_name}' contains liquid before aspiration",
          state_level=StateLevel.BOOLEAN,
        )

    elif isinstance(liquid_state, SymbolicLiquidState):
      vol = liquid_state.volumes.get(resource_name)
      if vol and vol.symbol == "0":
        return StateViolation(
          violation_type=ViolationType.NO_LIQUID,
          operation_id=op_id,
          method_name=method_name,
          resource_name=resource_name,
          message=f"Resource '{resource_name}' has no liquid (symbolic: {vol.symbol})",
          state_level=StateLevel.SYMBOLIC,
        )

    elif isinstance(liquid_state, ExactLiquidState):
      vol = liquid_state.get_volume(resource_name)
      if vol <= 0:
        return StateViolation(
          violation_type=ViolationType.NO_LIQUID,
          operation_id=op_id,
          method_name=method_name,
          resource_name=resource_name,
          message=f"Resource '{resource_name}' has no liquid (volume: {vol}µL)",
          state_level=StateLevel.EXACT,
          details={"volume": vol},
        )

    return None

  def _check_capacity_present(
    self,
    op_id: str,
    method_name: str,
    resource_name: str,
  ) -> StateViolation | None:
    """Check if capacity is available at appropriate precision level."""
    liquid_state = self.state.liquid_state

    if isinstance(liquid_state, BooleanLiquidState):
      if not liquid_state.check_has_capacity(resource_name):
        return StateViolation(
          violation_type=ViolationType.NO_CAPACITY,
          operation_id=op_id,
          method_name=method_name,
          resource_name=resource_name,
          message=f"Resource '{resource_name}' has no remaining capacity",
          suggested_fix=f"Ensure '{resource_name}' has capacity before dispense",
          state_level=StateLevel.BOOLEAN,
        )

    elif isinstance(liquid_state, ExactLiquidState):
      cap = liquid_state.get_capacity(resource_name)
      if cap <= 0:
        return StateViolation(
          violation_type=ViolationType.NO_CAPACITY,
          operation_id=op_id,
          method_name=method_name,
          resource_name=resource_name,
          message=f"Resource '{resource_name}' has no capacity (remaining: {cap}µL)",
          state_level=StateLevel.EXACT,
          details={"capacity": cap},
        )

    return None

  def _apply_effects(
    self,
    method_name: str,
    contract: MethodContract,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> None:
    """Apply state effects from an operation.

    Args:
        method_name: Name of the method
        contract: Method contract
        args: Positional arguments
        kwargs: Keyword arguments

    """
    arg_map = self._build_arg_map(contract, args, kwargs)

    # Tip effects
    if contract.loads_tips:
      count = contract.loads_tips_count or 1
      source = arg_map.get("tips") or arg_map.get("tip_rack")
      source_name = self._get_resource_name(source) if source else None
      self.state.tip_state.load_tips(count, source_name)

    if contract.drops_tips:
      self.state.tip_state.drop_tips()

    # Liquid effects
    liquid_state = self.state.liquid_state

    if contract.aspirates_from:
      resource = arg_map.get(contract.aspirates_from)
      if resource:
        resource_name = self._get_resource_name(resource)
        if isinstance(liquid_state, BooleanLiquidState):
          liquid_state.aspirate(resource_name)
        elif isinstance(liquid_state, SymbolicLiquidState):
          vol_arg = arg_map.get(contract.aspirate_volume_arg, 50)
          vol_symbol = str(vol_arg) if not isinstance(vol_arg, TracedValue) else "vol"
          liquid_state.aspirate(resource_name, vol_symbol)
        elif isinstance(liquid_state, ExactLiquidState):
          vol = self._get_numeric_value(arg_map.get(contract.aspirate_volume_arg), 50.0)
          liquid_state.aspirate(resource_name, vol)

    if contract.dispenses_to:
      resource = arg_map.get(contract.dispenses_to)
      if resource:
        resource_name = self._get_resource_name(resource)
        if isinstance(liquid_state, BooleanLiquidState):
          liquid_state.dispense(resource_name)
        elif isinstance(liquid_state, SymbolicLiquidState):
          vol_arg = arg_map.get(contract.dispense_volume_arg, 50)
          vol_symbol = str(vol_arg) if not isinstance(vol_arg, TracedValue) else "vol"
          liquid_state.dispense(resource_name, vol_symbol)
        elif isinstance(liquid_state, ExactLiquidState):
          vol = self._get_numeric_value(arg_map.get(contract.dispense_volume_arg), 50.0)
          liquid_state.dispense(resource_name, vol)

    if contract.transfers_from_to:
      source_arg, dest_arg = contract.transfers_from_to
      source = arg_map.get(source_arg)
      dest = arg_map.get(dest_arg)
      if source and dest:
        source_name = self._get_resource_name(source)
        dest_name = self._get_resource_name(dest)
        if isinstance(liquid_state, BooleanLiquidState):
          liquid_state.transfer(source_name, dest_name)
        elif isinstance(liquid_state, ExactLiquidState):
          # For transfer, use a default volume if not specified
          vol = 50.0  # Default transfer volume
          liquid_state.transfer(source_name, dest_name, vol)

  def _build_arg_map(
    self,
    contract: MethodContract,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> dict[str, Any]:
    """Build a mapping of argument names to values.

    Uses common PLR argument naming conventions.
    """
    # Common argument name patterns for different methods
    arg_patterns: dict[str, list[str]] = {
      "pick_up_tips": ["tips"],
      "pick_up_tips96": ["tip_rack"],
      "drop_tips": ["tips"],
      "drop_tips96": ["tip_rack"],
      "aspirate": ["resource", "vol"],
      "dispense": ["resource", "vol"],
      "transfer": ["source", "target", "vol"],
      "transfer_96": ["source", "target"],
      "mix": ["resource", "vol", "repetitions"],
    }

    arg_names = arg_patterns.get(contract.method_name, ["resource", "vol", "source", "target"])

    result: dict[str, Any] = {}

    # Map positional args
    for i, arg in enumerate(args):
      if i < len(arg_names):
        result[arg_names[i]] = arg

    # Merge keyword args
    result.update(kwargs)

    return result

  def _get_resource_name(self, value: Any) -> str:
    """Extract resource name from a value."""
    if isinstance(value, TracedValue):
      return value.name
    if isinstance(value, str):
      return value
    return str(value)

  def _get_numeric_value(self, value: Any, default: float) -> float:
    """Extract numeric value from an argument."""
    if value is None:
      return default
    if isinstance(value, (int, float)):
      return float(value)
    if isinstance(value, str):
      try:
        return float(value)
      except ValueError:
        return default
    return default


# =============================================================================
# Stateful Traced Resource
# =============================================================================


@dataclass
class StatefulTracedResource(TracedResource):
  """Resource tracer that tracks state.

  Extends TracedResource to track liquid state for wells.
  """

  state: SimulationState | None = None
  """Reference to simulation state (shared with machine)"""

  def wells(self) -> StatefulTracedWellCollection:
    """Get all wells as a stateful collection."""
    return StatefulTracedWellCollection(
      name=f"{self.name}.wells()",
      recorder=self.recorder,
      declared_type="list[Well]",
      element_type="Well",
      source_resource=self.name,
      state=self.state,
    )

  def tips(self) -> StatefulTracedWellCollection:
    """Get all tip spots as a stateful collection."""
    return StatefulTracedWellCollection(
      name=f"{self.name}.tips()",
      recorder=self.recorder,
      declared_type="list[TipSpot]",
      element_type="TipSpot",
      source_resource=self.name,
      state=self.state,
    )


@dataclass
class StatefulTracedWellCollection(TracedWellCollection):
  """Well collection tracer that tracks state."""

  state: SimulationState | None = None
  """Reference to simulation state"""


@dataclass
class StatefulTracedWell(TracedWell):
  """Well tracer that tracks state."""

  state: SimulationState | None = None
  """Reference to simulation state"""
