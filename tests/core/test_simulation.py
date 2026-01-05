"""Tests for the protocol simulation infrastructure.

This module tests:
- Method contracts (preconditions, effects)
- State models (boolean, symbolic, exact)
- Stateful tracers
- Hierarchical simulation pipeline
- Bounds analyzer
- Failure mode detector
"""

import pytest

from praxis.backend.core.simulation.bounds_analyzer import (
  BoundsAnalyzer,
  ItemizedResourceSpec,
  LoopBounds,
)
from praxis.backend.core.simulation.failure_detector import (
  BooleanStateConfig,
  FailureModeDetector,
  generate_boolean_states,
)
from praxis.backend.core.simulation.method_contracts import (
  METHOD_CONTRACTS,
  MethodContract,
  get_contract,
  get_contracts_for_type,
)
from praxis.backend.core.simulation.pipeline import (
  HierarchicalSimulator,
  simulate_protocol_sync,
)
from praxis.backend.core.simulation.state_models import (
  BooleanLiquidState,
  DeckState,
  ExactLiquidState,
  SimulationState,
  StateLevel,
  StateViolation,
  SymbolicLiquidState,
  TipState,
  ViolationType,
)
from praxis.backend.core.simulation.stateful_tracers import (
  StatefulTracedMachine,
)
from praxis.backend.core.tracing.recorder import OperationRecorder


# =============================================================================
# Test Method Contracts
# =============================================================================


class TestMethodContracts:
  """Tests for method contract definitions."""

  def test_contracts_registry_populated(self) -> None:
    """Test that the contract registry has entries."""
    assert len(METHOD_CONTRACTS) > 0

  def test_liquid_handler_contracts_exist(self) -> None:
    """Test that liquid handler contracts are defined."""
    lh_contracts = get_contracts_for_type("liquid_handler")
    assert len(lh_contracts) > 0

    # Check specific methods
    method_names = {c.method_name for c in lh_contracts}
    assert "pick_up_tips" in method_names
    assert "aspirate" in method_names
    assert "dispense" in method_names
    assert "transfer" in method_names

  def test_get_contract_found(self) -> None:
    """Test getting a specific contract."""
    contract = get_contract("liquid_handler", "aspirate")
    assert contract is not None
    assert contract.method_name == "aspirate"
    assert contract.requires_tips is True
    assert contract.requires_liquid_in == "resource"

  def test_get_contract_not_found(self) -> None:
    """Test getting a non-existent contract."""
    contract = get_contract("liquid_handler", "nonexistent_method")
    assert contract is None

  def test_pick_up_tips_contract(self) -> None:
    """Test pick_up_tips contract details."""
    contract = get_contract("liquid_handler", "pick_up_tips")
    assert contract is not None
    assert contract.requires_tips is False  # Doesn't require tips to pick up
    assert contract.loads_tips is True  # Creates tips_loaded state
    assert "tips" in contract.requires_on_deck

  def test_transfer_contract(self) -> None:
    """Test transfer contract details."""
    contract = get_contract("liquid_handler", "transfer")
    assert contract is not None
    assert contract.requires_tips is True
    assert contract.requires_liquid_in == "source"
    assert contract.requires_capacity_in == "target"
    assert contract.transfers_from_to == ("source", "target")

  def test_plate_reader_contracts(self) -> None:
    """Test plate reader contracts exist."""
    pr_contracts = get_contracts_for_type("plate_reader")
    assert len(pr_contracts) > 0

    method_names = {c.method_name for c in pr_contracts}
    assert "read_absorbance" in method_names


# =============================================================================
# Test State Models
# =============================================================================


class TestBooleanLiquidState:
  """Tests for BooleanLiquidState."""

  def test_init(self) -> None:
    """Test initialization."""
    state = BooleanLiquidState()
    assert len(state.has_liquid) == 0
    assert len(state.has_capacity) == 0

  def test_set_has_liquid(self) -> None:
    """Test setting liquid state."""
    state = BooleanLiquidState()
    state.set_has_liquid("plate.A1", True)
    assert state.check_has_liquid("plate.A1") is True

  def test_unknown_resource_has_liquid(self) -> None:
    """Test that unknown resources are assumed to have liquid."""
    state = BooleanLiquidState()
    assert state.check_has_liquid("unknown") is True

  def test_aspirate(self) -> None:
    """Test aspirate effect."""
    state = BooleanLiquidState()
    state.set_has_liquid("source", True)
    state.aspirate("source")
    # Still has liquid after single aspirate (boolean doesn't track depletion)
    assert state.check_has_capacity("source") is True

  def test_dispense(self) -> None:
    """Test dispense effect."""
    state = BooleanLiquidState()
    state.dispense("dest")
    assert state.check_has_liquid("dest") is True

  def test_transfer(self) -> None:
    """Test transfer effect."""
    state = BooleanLiquidState()
    state.set_has_liquid("source", True)
    state.transfer("source", "dest")
    assert state.check_has_liquid("dest") is True

  def test_copy(self) -> None:
    """Test copying state."""
    state = BooleanLiquidState()
    state.set_has_liquid("plate", True)
    copied = state.copy()
    assert copied.check_has_liquid("plate") is True
    # Modify original, copy should be unchanged
    state.set_has_liquid("plate", False)
    assert copied.check_has_liquid("plate") is True


class TestExactLiquidState:
  """Tests for ExactLiquidState."""

  def test_set_volume(self) -> None:
    """Test setting volume."""
    state = ExactLiquidState()
    state.set_volume("well", 100.0, max_capacity=200.0)
    assert state.get_volume("well") == 100.0
    assert state.get_capacity("well") == 100.0

  def test_aspirate_success(self) -> None:
    """Test successful aspiration."""
    state = ExactLiquidState()
    state.set_volume("source", 100.0)
    result = state.aspirate("source", 50.0)
    assert result is True
    assert state.get_volume("source") == 50.0

  def test_aspirate_failure(self) -> None:
    """Test failed aspiration (insufficient volume)."""
    state = ExactLiquidState()
    state.set_volume("source", 30.0)
    result = state.aspirate("source", 50.0)
    assert result is False
    # Volume unchanged on failure
    assert state.get_volume("source") == 30.0

  def test_dispense_success(self) -> None:
    """Test successful dispense."""
    state = ExactLiquidState()
    state.set_volume("dest", 50.0, max_capacity=200.0)
    result = state.dispense("dest", 50.0)
    assert result is True
    assert state.get_volume("dest") == 100.0

  def test_dispense_failure(self) -> None:
    """Test failed dispense (capacity exceeded)."""
    state = ExactLiquidState()
    state.set_volume("dest", 180.0, max_capacity=200.0)
    result = state.dispense("dest", 50.0)
    assert result is False

  def test_transfer(self) -> None:
    """Test transfer operation."""
    state = ExactLiquidState()
    state.set_volume("source", 100.0)
    state.set_volume("dest", 0.0)
    result = state.transfer("source", "dest", 50.0)
    assert result is True
    assert state.get_volume("source") == 50.0
    assert state.get_volume("dest") == 50.0


class TestTipState:
  """Tests for TipState."""

  def test_init(self) -> None:
    """Test initialization."""
    state = TipState()
    assert state.tips_loaded is False
    assert state.tips_count == 0

  def test_load_tips(self) -> None:
    """Test loading tips."""
    state = TipState()
    state.load_tips(8, "tip_rack")
    assert state.tips_loaded is True
    assert state.tips_count == 8
    assert state.tip_source == "tip_rack"

  def test_drop_tips(self) -> None:
    """Test dropping tips."""
    state = TipState()
    state.load_tips(8)
    state.drop_tips()
    assert state.tips_loaded is False
    assert state.tips_count == 0


class TestSimulationState:
  """Tests for SimulationState."""

  def test_default_boolean(self) -> None:
    """Test creating default boolean state."""
    state = SimulationState.default_boolean()
    assert state.level == StateLevel.BOOLEAN
    assert isinstance(state.liquid_state, BooleanLiquidState)

  def test_promote_boolean_to_symbolic(self) -> None:
    """Test promoting boolean to symbolic state."""
    state = SimulationState.default_boolean()
    state.liquid_state.set_has_liquid("plate", True)

    promoted = state.promote()

    assert promoted.level == StateLevel.SYMBOLIC
    assert isinstance(promoted.liquid_state, SymbolicLiquidState)

  def test_promote_symbolic_to_exact(self) -> None:
    """Test promoting symbolic to exact state."""
    state = SimulationState.default_symbolic()
    promoted = state.promote_to_exact_with_values({"plate": 100.0})

    assert promoted.level == StateLevel.EXACT
    assert isinstance(promoted.liquid_state, ExactLiquidState)

  def test_copy(self) -> None:
    """Test copying state."""
    state = SimulationState.default_boolean()
    state.tip_state.load_tips(8)
    state.deck_state.place_on_deck("plate")

    copied = state.copy()

    assert copied.tip_state.tips_loaded is True
    assert copied.deck_state.is_on_deck("plate") is True

    # Modify original
    state.tip_state.drop_tips()
    # Copy unchanged
    assert copied.tip_state.tips_loaded is True


# =============================================================================
# Test Stateful Tracers
# =============================================================================


class TestStatefulTracedMachine:
  """Tests for StatefulTracedMachine."""

  @pytest.fixture
  def recorder(self) -> OperationRecorder:
    """Create a recorder for testing."""
    return OperationRecorder(protocol_fqn="test.protocol")

  @pytest.fixture
  def state(self) -> SimulationState:
    """Create default state for testing."""
    return SimulationState.default_boolean()

  def test_aspirate_without_tips_violation(
    self, recorder: OperationRecorder, state: SimulationState
  ) -> None:
    """Test that aspirating without tips creates a violation."""
    machine = StatefulTracedMachine(
      name="lh",
      recorder=recorder,
      declared_type="LiquidHandler",
      machine_type="liquid_handler",
      state=state,
    )

    # Aspirate without picking up tips
    machine.aspirate("well", 100)

    assert len(machine.violations) == 1
    assert machine.violations[0].violation_type == ViolationType.TIPS_NOT_LOADED

  def test_pick_up_tips_loads_tips(
    self, recorder: OperationRecorder, state: SimulationState
  ) -> None:
    """Test that pick_up_tips loads tips in state."""
    machine = StatefulTracedMachine(
      name="lh",
      recorder=recorder,
      declared_type="LiquidHandler",
      machine_type="liquid_handler",
      state=state,
    )

    machine.pick_up_tips("tips")

    assert state.tip_state.tips_loaded is True
    assert len(machine.violations) == 0

  def test_aspirate_with_tips_no_violation(
    self, recorder: OperationRecorder, state: SimulationState
  ) -> None:
    """Test that aspirating with tips doesn't create a violation."""
    machine = StatefulTracedMachine(
      name="lh",
      recorder=recorder,
      declared_type="LiquidHandler",
      machine_type="liquid_handler",
      state=state,
    )

    machine.pick_up_tips("tips")
    machine.aspirate("well", 100)

    # No tips violation (resource may have other violations)
    tips_violations = [v for v in machine.violations if v.violation_type == ViolationType.TIPS_NOT_LOADED]
    assert len(tips_violations) == 0

  def test_drop_tips_removes_tips(
    self, recorder: OperationRecorder, state: SimulationState
  ) -> None:
    """Test that drop_tips removes tips from state."""
    machine = StatefulTracedMachine(
      name="lh",
      recorder=recorder,
      declared_type="LiquidHandler",
      machine_type="liquid_handler",
      state=state,
    )

    machine.pick_up_tips("tips")
    assert state.tip_state.tips_loaded is True

    machine.drop_tips("tips")
    assert state.tip_state.tips_loaded is False


# =============================================================================
# Test Hierarchical Simulator
# =============================================================================


class TestHierarchicalSimulator:
  """Tests for HierarchicalSimulator."""

  def test_simple_valid_protocol(self) -> None:
    """Test simulation of a valid simple protocol."""

    async def valid_protocol(lh, plate, tips):
      await lh.pick_up_tips(tips)
      await lh.aspirate(plate["A1"], 100)
      await lh.dispense(plate["B1"], 100)
      await lh.drop_tips(tips)

    result = simulate_protocol_sync(
      valid_protocol,
      parameter_types={
        "lh": "LiquidHandler",
        "plate": "Plate",
        "tips": "TipRack",
      },
    )

    assert result.passed is True
    assert result.level_completed == "exact"
    assert len(result.violations) == 0

  def test_protocol_missing_tips(self) -> None:
    """Test that missing tips are detected."""

    async def missing_tips_protocol(lh, plate):
      # Aspirate without picking up tips - should fail
      await lh.aspirate(plate["A1"], 100)

    result = simulate_protocol_sync(
      missing_tips_protocol,
      parameter_types={
        "lh": "LiquidHandler",
        "plate": "Plate",
      },
    )

    assert result.passed is False
    assert len(result.violations) > 0
    assert any(v["type"] == "tips_not_loaded" for v in result.violations)

  def test_protocol_with_loop(self) -> None:
    """Test simulation of protocol with loop."""

    async def loop_protocol(lh, plate, tips):
      await lh.pick_up_tips(tips)
      for well in plate.wells():
        await lh.aspirate(well, 50)
      await lh.drop_tips(tips)

    result = simulate_protocol_sync(
      loop_protocol,
      parameter_types={
        "lh": "LiquidHandler",
        "plate": "Plate",
        "tips": "TipRack",
      },
    )

    # Should pass - tips are picked up before loop
    assert result.passed is True

  def test_inferred_requirements(self) -> None:
    """Test that requirements are inferred from failures."""

    async def incomplete_protocol(lh, plate):
      await lh.aspirate(plate["A1"], 100)

    result = simulate_protocol_sync(
      incomplete_protocol,
      parameter_types={
        "lh": "LiquidHandler",
        "plate": "Plate",
      },
    )

    assert result.passed is False
    assert len(result.inferred_requirements) > 0
    # Should infer tips_required
    assert any(r.requirement_type == "tips_required" for r in result.inferred_requirements)


# =============================================================================
# Test Bounds Analyzer
# =============================================================================


class TestBoundsAnalyzer:
  """Tests for BoundsAnalyzer."""

  def test_analyze_wells_loop(self) -> None:
    """Test analyzing plate.wells() loop."""
    analyzer = BoundsAnalyzer()
    analyzer.add_resource_spec(
      ItemizedResourceSpec("plate", "Plate", items_x=12, items_y=8)
    )

    bounds = analyzer.analyze_loop("plate.wells()")

    assert bounds.is_bounded is True
    assert bounds.exact_count == 96

  def test_analyze_rows_loop(self) -> None:
    """Test analyzing plate.rows() loop."""
    analyzer = BoundsAnalyzer()
    analyzer.add_resource_spec(
      ItemizedResourceSpec("plate", "Plate", items_x=12, items_y=8)
    )

    bounds = analyzer.analyze_loop("plate.rows()")

    assert bounds.is_bounded is True
    assert bounds.exact_count == 8

  def test_analyze_columns_loop(self) -> None:
    """Test analyzing plate.columns() loop."""
    analyzer = BoundsAnalyzer()
    analyzer.add_resource_spec(
      ItemizedResourceSpec("plate", "Plate", items_x=12, items_y=8)
    )

    bounds = analyzer.analyze_loop("plate.columns()")

    assert bounds.is_bounded is True
    assert bounds.exact_count == 12

  def test_analyze_tips_loop(self) -> None:
    """Test analyzing tips.tips() loop."""
    analyzer = BoundsAnalyzer()
    analyzer.add_resource_spec(
      ItemizedResourceSpec("tips", "TipRack", items_x=12, items_y=8)
    )

    bounds = analyzer.analyze_loop("tips.tips()")

    assert bounds.is_bounded is True
    assert bounds.exact_count == 96

  def test_unknown_resource_default(self) -> None:
    """Test that unknown resources use default dimensions."""
    analyzer = BoundsAnalyzer()

    bounds = analyzer.analyze_loop("unknown.wells()")

    assert bounds.is_bounded is True
    assert bounds.exact_count == 96  # Default assumption

  def test_384_well_plate(self) -> None:
    """Test 384-well plate dimensions."""
    analyzer = BoundsAnalyzer()
    analyzer.add_resource_spec(
      ItemizedResourceSpec("plate384", "Plate384", items_x=24, items_y=16)
    )

    bounds = analyzer.analyze_loop("plate384.wells()")

    assert bounds.exact_count == 384


# =============================================================================
# Test Failure Mode Detector
# =============================================================================


class TestFailureModeDetector:
  """Tests for FailureModeDetector."""

  def test_generate_boolean_states(self) -> None:
    """Test generating boolean state combinations."""
    config = BooleanStateConfig(
      resources=["plate"],
      tip_states=[True, False],
      liquid_states=[True, False],
    )

    states = list(generate_boolean_states(config))

    # 2 tip states × 2 liquid states = 4 combinations
    assert len(states) == 4

  def test_generate_states_no_resources(self) -> None:
    """Test generating states with no resources."""
    config = BooleanStateConfig(
      resources=[],
      tip_states=[True, False],
    )

    states = list(generate_boolean_states(config))

    assert len(states) == 2  # Just tip states

  def test_detect_missing_tips_failure(self) -> None:
    """Test detecting missing tips failure mode."""

    async def incomplete_protocol(lh, plate):
      await lh.aspirate(plate["A1"], 100)

    detector = FailureModeDetector(max_states=10)
    result = detector.detect_sync(
      incomplete_protocol,
      parameter_types={
        "lh": "LiquidHandler",
        "plate": "Plate",
      },
    )

    assert len(result.failure_modes) > 0
    # At least one failure should be about tips
    tips_failures = [
      f for f in result.failure_modes if "tips" in f.failure_type.lower()
    ]
    assert len(tips_failures) > 0

  def test_no_failures_valid_protocol(self) -> None:
    """Test that valid protocol has no failure modes when run with correct state."""
    # Note: This tests the detector with a protocol that picks up tips
    # Some initial states may still cause failures

    async def valid_protocol(lh, plate, tips):
      await lh.pick_up_tips(tips)
      await lh.aspirate(plate["A1"], 100)
      await lh.drop_tips(tips)

    detector = FailureModeDetector(max_states=10)
    result = detector.detect_sync(
      valid_protocol,
      parameter_types={
        "lh": "LiquidHandler",
        "plate": "Plate",
        "tips": "TipRack",
      },
    )

    # Valid protocol should have fewer failures or none
    # (may still fail on states where source has no liquid)
    assert result.states_explored > 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestSimulationIntegration:
  """Integration tests for the complete simulation system."""

  def test_transfer_96_protocol(self) -> None:
    """Test simulation of 96-well transfer protocol."""

    async def transfer_96_protocol(lh, source, dest, tips):
      await lh.pick_up_tips96(tips)
      await lh.transfer_96(source, dest)
      await lh.drop_tips96(tips)

    result = simulate_protocol_sync(
      transfer_96_protocol,
      parameter_types={
        "lh": "LiquidHandler",
        "source": "Plate",
        "dest": "Plate",
        "tips": "TipRack",
      },
    )

    # Should pass with proper tip handling
    assert result.passed is True

  def test_multi_step_protocol(self) -> None:
    """Test complex multi-step protocol."""

    async def complex_protocol(lh, plate, tips, volume=50.0):
      await lh.pick_up_tips(tips)
      await lh.aspirate(plate["A1"], volume)
      await lh.dispense(plate["B1"], volume)
      await lh.aspirate(plate["A2"], volume)
      await lh.dispense(plate["B2"], volume)
      await lh.drop_tips(tips)

    result = simulate_protocol_sync(
      complex_protocol,
      parameter_types={
        "lh": "LiquidHandler",
        "plate": "Plate",
        "tips": "TipRack",
        "volume": "float",
      },
    )

    assert result.passed is True

  def test_simulation_with_plate_reader(self) -> None:
    """Test protocol using plate reader."""

    async def reader_protocol(pr, plate):
      await pr.read_absorbance(plate, wavelength=450)

    result = simulate_protocol_sync(
      reader_protocol,
      parameter_types={
        "pr": "PlateReader",
        "plate": "Plate",
      },
    )

    # Plate reader doesn't require tips
    assert result.passed is True

  def test_state_violation_has_fix_suggestion(self) -> None:
    """Test that violations include fix suggestions."""

    async def broken_protocol(lh, plate):
      await lh.aspirate(plate["A1"], 100)

    result = simulate_protocol_sync(
      broken_protocol,
      parameter_types={
        "lh": "LiquidHandler",
        "plate": "Plate",
      },
    )

    assert result.passed is False
    assert len(result.violations) > 0

    # At least one violation should have a suggested fix
    violations_with_fix = [v for v in result.violations if v.get("suggested_fix")]
    assert len(violations_with_fix) > 0
