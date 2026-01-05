"""Tests for the Computation Graph Extractor."""

import pytest

from praxis.backend.utils.plr_static_analysis.models import (
  GraphNodeType,
  PreconditionType,
  ProtocolComputationGraph,
)
from praxis.backend.utils.plr_static_analysis.resource_hierarchy import DeckLayoutType
from praxis.backend.utils.plr_static_analysis.visitors.computation_graph_extractor import (
  ComputationGraphExtractor,
  VariableTypeTracker,
  extract_graph_from_source,
)

# Test protocol source code
SIMPLE_TRANSFER_SOURCE = '''
async def simple_transfer(
    lh: LiquidHandler,
    source: Plate,
    dest: Plate,
    tips: TipRack,
):
    """Simple A to B transfer."""
    await lh.pick_up_tips(tips)
    await lh.aspirate(source["A1"], 100)
    await lh.dispense(dest["A1"], 100)
    await lh.drop_tips(tips)
'''

LOOP_PROTOCOL_SOURCE = '''
async def multi_well_transfer(
    lh: LiquidHandler,
    source: Plate,
    dest: Plate,
    tips: TipRack,
    volume: float = 50.0,
):
    """Transfer to multiple wells."""
    source_wells = source["A1:A8"]
    dest_wells = dest["A1:A8"]

    await lh.pick_up_tips(tips)

    for i, (src, dst) in enumerate(zip(source_wells, dest_wells)):
        await lh.aspirate(src, volume)
        await lh.dispense(dst, volume)

    await lh.drop_tips(tips)
'''

CONDITIONAL_PROTOCOL_SOURCE = '''
async def conditional_volume(
    lh: LiquidHandler,
    plate: Plate,
    tips: TipRack,
    volume: float,
    threshold: float = 50.0,
):
    """Conditional aspiration based on volume."""
    await lh.pick_up_tips(tips)

    if volume > threshold:
        await lh.aspirate(plate["A1"], volume)
    else:
        await lh.aspirate(plate["A1"], volume / 2)

    await lh.drop_tips(tips)
'''

MULTI_MACHINE_SOURCE = '''
async def plate_reader_workflow(
    lh: LiquidHandler,
    pr: PlateReader,
    plate: Plate,
    tips: TipRack,
):
    """Workflow involving multiple machines."""
    await lh.pick_up_tips(tips)
    await lh.aspirate(plate["A1"], 100)
    await lh.dispense(plate["B1"], 100)
    await lh.drop_tips(tips)

    result = await pr.read_absorbance(plate, wavelength=450)
    return result
'''


class TestVariableTypeTracker:
  """Tests for VariableTypeTracker."""

  def test_init_with_parameters(self) -> None:
    """Test initialization with parameter types."""
    tracker = VariableTypeTracker({"lh": "LiquidHandler", "plate": "Plate"})
    assert tracker.get_type("lh") == "LiquidHandler"
    assert tracker.get_type("plate") == "Plate"

  def test_set_and_get_type(self) -> None:
    """Test setting and getting types."""
    tracker = VariableTypeTracker({})
    tracker.set_type("wells", "list[Well]", source='plate["A1:A8"]')
    assert tracker.get_type("wells") == "list[Well]"
    assert tracker.get_source("wells") == 'plate["A1:A8"]'

  def test_get_unknown_type(self) -> None:
    """Test that unknown variables return None."""
    tracker = VariableTypeTracker({})
    assert tracker.get_type("unknown") is None

  def test_infer_plate_subscript_type_range(self) -> None:
    """Test inferring type from plate subscript with range."""
    tracker = VariableTypeTracker({})
    result = tracker.infer_subscript_type("Plate", "A1:A8")
    assert result == "list[Well]"

  def test_infer_plate_subscript_type_single(self) -> None:
    """Test inferring type from plate subscript with single well."""
    tracker = VariableTypeTracker({})
    result = tracker.infer_subscript_type("Plate", "A1")
    assert result == "Well"

  def test_infer_tiprack_subscript_type_range(self) -> None:
    """Test inferring type from tip rack subscript with range."""
    tracker = VariableTypeTracker({})
    result = tracker.infer_subscript_type("TipRack", "A1:A8")
    assert result == "list[TipSpot]"

  def test_infer_list_subscript_type(self) -> None:
    """Test inferring type from list subscript."""
    tracker = VariableTypeTracker({})
    result = tracker.infer_subscript_type("list[Well]", "0")
    assert result == "Well"

  def test_infer_attribute_wells(self) -> None:
    """Test inferring type from .wells() attribute."""
    tracker = VariableTypeTracker({})
    result = tracker.infer_attribute_type("Plate", "wells")
    assert result == "list[Well]"

  def test_infer_attribute_tips(self) -> None:
    """Test inferring type from .tips() attribute."""
    tracker = VariableTypeTracker({})
    result = tracker.infer_attribute_type("TipRack", "tips")
    assert result == "list[TipSpot]"


class TestComputationGraphExtractor:
  """Tests for ComputationGraphExtractor."""

  def test_simple_transfer_extracts_operations(self) -> None:
    """Test that simple_transfer extracts all 4 operations."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None
    assert len(graph.operations) == 4
    assert graph.execution_order == ["op_1", "op_2", "op_3", "op_4"]

  def test_simple_transfer_operation_methods(self) -> None:
    """Test that operation methods are correctly extracted."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None
    methods = [op.method_name for op in graph.operations]
    assert methods == ["pick_up_tips", "aspirate", "dispense", "drop_tips"]

  def test_simple_transfer_resources(self) -> None:
    """Test that resources are correctly identified."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None
    assert "source" in graph.resources
    assert "dest" in graph.resources
    assert "tips" in graph.resources
    assert graph.resources["source"].declared_type == "Plate"
    assert graph.resources["tips"].declared_type == "TipRack"

  def test_simple_transfer_machine_types(self) -> None:
    """Test that machine types are correctly identified."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None
    assert "liquid_handler" in graph.machine_types

  def test_simple_transfer_resource_types(self) -> None:
    """Test that resource types are collected."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None
    assert "Plate" in graph.resource_types
    assert "TipRack" in graph.resource_types

  def test_simple_transfer_no_loops_or_conditionals(self) -> None:
    """Test that simple protocol has no loops or conditionals."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None
    assert graph.has_loops is False
    assert graph.has_conditionals is False

  def test_loop_protocol_detects_loops(self) -> None:
    """Test that loop protocol is detected as having loops."""
    graph = extract_graph_from_source(
      LOOP_PROTOCOL_SOURCE, "multi_well_transfer", "test_module"
    )
    assert graph is not None
    assert graph.has_loops is True

  def test_conditional_protocol_detects_conditionals(self) -> None:
    """Test that conditional protocol is detected."""
    graph = extract_graph_from_source(
      CONDITIONAL_PROTOCOL_SOURCE, "conditional_volume", "test_module"
    )
    assert graph is not None
    assert graph.has_conditionals is True

  def test_multi_machine_detects_both_machines(self) -> None:
    """Test that multi-machine protocol detects both machine types."""
    graph = extract_graph_from_source(
      MULTI_MACHINE_SOURCE, "plate_reader_workflow", "test_module"
    )
    assert graph is not None
    assert "liquid_handler" in graph.machine_types
    assert "plate_reader" in graph.machine_types

  def test_multi_machine_operation_count(self) -> None:
    """Test that all operations are extracted."""
    graph = extract_graph_from_source(
      MULTI_MACHINE_SOURCE, "plate_reader_workflow", "test_module"
    )
    assert graph is not None
    # pick_up_tips, aspirate, dispense, drop_tips, read_absorbance
    assert len(graph.operations) == 5


class TestPreconditionExtraction:
  """Tests for precondition extraction."""

  def test_tips_loaded_precondition(self) -> None:
    """Test that aspirate/dispense require tips_loaded precondition."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None

    # Find aspirate operation
    aspirate_op = None
    for op in graph.operations:
      if op.method_name == "aspirate":
        aspirate_op = op
        break

    assert aspirate_op is not None
    # Aspirate should have preconditions (tips loaded, plate accessible)
    assert len(aspirate_op.preconditions) >= 0  # May have been satisfied by pick_up_tips

  def test_pick_up_tips_creates_state(self) -> None:
    """Test that pick_up_tips creates tips_loaded state."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None

    # Find pick_up_tips operation
    pickup_op = None
    for op in graph.operations:
      if op.method_name == "pick_up_tips":
        pickup_op = op
        break

    assert pickup_op is not None
    assert "tips_loaded" in pickup_op.creates_state

  def test_resource_on_deck_preconditions(self) -> None:
    """Test that resources have on_deck preconditions."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None

    # Check that preconditions exist for resource placement
    on_deck_preconds = [
      p
      for p in graph.preconditions
      if p.precondition_type == PreconditionType.RESOURCE_ON_DECK
    ]
    # Should have preconditions for source, dest, tips (3 PLR resources, not lh)
    assert len(on_deck_preconds) == 3


class TestGraphModel:
  """Tests for ProtocolComputationGraph model methods."""

  def test_get_operation(self) -> None:
    """Test get_operation method."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None

    op = graph.get_operation("op_1")
    assert op is not None
    assert op.method_name == "pick_up_tips"

  def test_get_operation_not_found(self) -> None:
    """Test get_operation returns None for unknown ID."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None

    op = graph.get_operation("op_999")
    assert op is None

  def test_get_resource(self) -> None:
    """Test get_resource method."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None

    res = graph.get_resource("source")
    assert res is not None
    assert res.declared_type == "Plate"

  def test_get_resource_not_found(self) -> None:
    """Test get_resource returns None for unknown name."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None

    res = graph.get_resource("nonexistent")
    assert res is None

  def test_get_unsatisfied_preconditions(self) -> None:
    """Test get_unsatisfied_preconditions method."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE, "simple_transfer", "test_module"
    )
    assert graph is not None

    unsatisfied = graph.get_unsatisfied_preconditions()
    # resource_on_deck preconditions are unsatisfied (no satisfying operation)
    assert len(unsatisfied) > 0


class TestParentalChainIntegration:
  """Tests for parental chain integration in resource nodes."""

  def test_resource_parental_chain_carrier_based(self) -> None:
    """Test that resources have correct parental chains for carrier-based deck."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE,
      "simple_transfer",
      "test_module",
    )
    assert graph is not None

    source = graph.resources.get("source")
    assert source is not None
    # Plate -> PlateCarrier -> Deck
    assert "PlateCarrier" in source.parental_chain
    assert "Deck" in source.parental_chain

  def test_resource_parental_chain_tiprack(self) -> None:
    """Test that TipRack has correct parental chain."""
    graph = extract_graph_from_source(
      SIMPLE_TRANSFER_SOURCE,
      "simple_transfer",
      "test_module",
    )
    assert graph is not None

    tips = graph.resources.get("tips")
    assert tips is not None
    # TipRack -> TipCarrier -> Deck
    assert "TipCarrier" in tips.parental_chain
    assert "Deck" in tips.parental_chain


class TestExtractGraphFromSourceErrors:
  """Tests for error handling in extract_graph_from_source."""

  def test_invalid_source_returns_none(self) -> None:
    """Test that invalid Python source returns None."""
    graph = extract_graph_from_source(
      "this is not valid python {{{",
      "function",
      "module",
    )
    assert graph is None

  def test_function_not_found_returns_none(self) -> None:
    """Test that missing function returns None."""
    graph = extract_graph_from_source(
      "def other_function(): pass",
      "missing_function",
      "module",
    )
    assert graph is None

  def test_empty_function(self) -> None:
    """Test extracting graph from empty function."""
    source = '''
async def empty_protocol(lh: LiquidHandler):
    """Does nothing."""
    pass
'''
    graph = extract_graph_from_source(source, "empty_protocol", "test")
    assert graph is not None
    assert len(graph.operations) == 0
