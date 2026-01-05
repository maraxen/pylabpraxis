"""Tests for the Resource Hierarchy Registry."""

import pytest

from praxis.backend.utils.plr_static_analysis.resource_hierarchy import (
  CARRIER_TYPES,
  DeckLayoutType,
  ResourceCategory,
  ResourceHierarchyRegistry,
  get_parental_chain,
  get_registry,
  infer_deck_type,
)


class TestResourceCategory:
  """Tests for ResourceCategory enum."""

  def test_sub_resource_categories_exist(self) -> None:
    """Test that sub-resource categories are defined."""
    assert ResourceCategory.WELL
    assert ResourceCategory.TIP_SPOT
    assert ResourceCategory.TUBE

  def test_container_categories_exist(self) -> None:
    """Test that container categories are defined."""
    assert ResourceCategory.PLATE
    assert ResourceCategory.TIP_RACK
    assert ResourceCategory.TROUGH
    assert ResourceCategory.TUBE_RACK

  def test_carrier_categories_exist(self) -> None:
    """Test that carrier categories are defined."""
    assert ResourceCategory.PLATE_CARRIER
    assert ResourceCategory.TIP_CARRIER
    assert ResourceCategory.TROUGH_CARRIER
    assert ResourceCategory.CARRIER


class TestResourceHierarchyRegistry:
  """Tests for ResourceHierarchyRegistry class."""

  @pytest.fixture
  def registry(self) -> ResourceHierarchyRegistry:
    """Provide a fresh registry instance."""
    return ResourceHierarchyRegistry()

  # --- Category Resolution ---

  def test_get_category_well(self, registry: ResourceHierarchyRegistry) -> None:
    """Test that Well maps to WELL category."""
    assert registry.get_category("Well") == ResourceCategory.WELL

  def test_get_category_plate(self, registry: ResourceHierarchyRegistry) -> None:
    """Test that Plate maps to PLATE category."""
    assert registry.get_category("Plate") == ResourceCategory.PLATE

  def test_get_category_tip_rack(self, registry: ResourceHierarchyRegistry) -> None:
    """Test that TipRack maps to TIP_RACK category."""
    assert registry.get_category("TipRack") == ResourceCategory.TIP_RACK

  def test_get_category_carrier(self, registry: ResourceHierarchyRegistry) -> None:
    """Test that PlateCarrier maps to PLATE_CARRIER category."""
    assert registry.get_category("PlateCarrier") == ResourceCategory.PLATE_CARRIER

  def test_get_category_unknown(self, registry: ResourceHierarchyRegistry) -> None:
    """Test that unknown types map to RESOURCE category."""
    assert registry.get_category("UnknownType") == ResourceCategory.RESOURCE

  # --- Parental Chain (Carrier-Based) ---

  def test_well_chain_carrier_based(self, registry: ResourceHierarchyRegistry) -> None:
    """Test Well parental chain on carrier-based deck."""
    chain = registry.get_parental_chain("Well", DeckLayoutType.CARRIER_BASED)
    assert chain.chain == ["Plate", "PlateCarrier", "Deck"]
    assert chain.resource_type == "Well"
    assert chain.deck_layout_type == DeckLayoutType.CARRIER_BASED

  def test_tipspot_chain_carrier_based(self, registry: ResourceHierarchyRegistry) -> None:
    """Test TipSpot parental chain on carrier-based deck."""
    chain = registry.get_parental_chain("TipSpot", DeckLayoutType.CARRIER_BASED)
    assert chain.chain == ["TipRack", "TipCarrier", "Deck"]

  def test_plate_chain_carrier_based(self, registry: ResourceHierarchyRegistry) -> None:
    """Test Plate parental chain on carrier-based deck."""
    chain = registry.get_parental_chain("Plate", DeckLayoutType.CARRIER_BASED)
    assert chain.chain == ["PlateCarrier", "Deck"]

  def test_tiprack_chain_carrier_based(self, registry: ResourceHierarchyRegistry) -> None:
    """Test TipRack parental chain on carrier-based deck."""
    chain = registry.get_parental_chain("TipRack", DeckLayoutType.CARRIER_BASED)
    assert chain.chain == ["TipCarrier", "Deck"]

  def test_carrier_chain_carrier_based(self, registry: ResourceHierarchyRegistry) -> None:
    """Test PlateCarrier parental chain."""
    chain = registry.get_parental_chain("PlateCarrier", DeckLayoutType.CARRIER_BASED)
    assert chain.chain == ["Deck"]

  # --- Parental Chain (Slot-Based) ---

  def test_well_chain_slot_based(self, registry: ResourceHierarchyRegistry) -> None:
    """Test Well parental chain on slot-based deck."""
    chain = registry.get_parental_chain("Well", DeckLayoutType.SLOT_BASED)
    assert chain.chain == ["Plate", "Slot", "Deck"]

  def test_plate_chain_slot_based(self, registry: ResourceHierarchyRegistry) -> None:
    """Test Plate parental chain on slot-based deck."""
    chain = registry.get_parental_chain("Plate", DeckLayoutType.SLOT_BASED)
    assert chain.chain == ["Slot", "Deck"]

  def test_tiprack_chain_slot_based(self, registry: ResourceHierarchyRegistry) -> None:
    """Test TipRack parental chain on slot-based deck."""
    chain = registry.get_parental_chain("TipRack", DeckLayoutType.SLOT_BASED)
    assert chain.chain == ["Slot", "Deck"]

  def test_trough_chain_slot_based(self, registry: ResourceHierarchyRegistry) -> None:
    """Test Trough parental chain on slot-based deck."""
    chain = registry.get_parental_chain("Trough", DeckLayoutType.SLOT_BASED)
    assert chain.chain == ["Slot", "Deck"]

  # --- Deck Type Inference ---

  def test_infer_deck_type_opentrons(self, registry: ResourceHierarchyRegistry) -> None:
    """Test inferring slot-based deck from Opentrons name."""
    assert registry.infer_deck_type("OTDeck") == DeckLayoutType.SLOT_BASED
    assert registry.infer_deck_type("Opentrons_Deck") == DeckLayoutType.SLOT_BASED
    assert registry.infer_deck_type("FlexDeck") == DeckLayoutType.SLOT_BASED

  def test_infer_deck_type_hamilton(self, registry: ResourceHierarchyRegistry) -> None:
    """Test inferring carrier-based deck from Hamilton name."""
    assert registry.infer_deck_type("HamiltonSTARDeck") == DeckLayoutType.CARRIER_BASED
    assert registry.infer_deck_type("STARDeck") == DeckLayoutType.CARRIER_BASED
    assert registry.infer_deck_type("HamiltonNimbus") == DeckLayoutType.CARRIER_BASED

  def test_infer_deck_type_tecan(self, registry: ResourceHierarchyRegistry) -> None:
    """Test inferring carrier-based deck from Tecan name."""
    assert registry.infer_deck_type("TecanEVO") == DeckLayoutType.CARRIER_BASED
    assert registry.infer_deck_type("Tecan_Deck") == DeckLayoutType.CARRIER_BASED

  def test_infer_deck_type_unknown_defaults_carrier(
    self, registry: ResourceHierarchyRegistry
  ) -> None:
    """Test that unknown deck names default to carrier-based."""
    assert registry.infer_deck_type("UnknownDeck") == DeckLayoutType.CARRIER_BASED
    assert registry.infer_deck_type("CustomDeck") == DeckLayoutType.CARRIER_BASED

  # --- Type Classification ---

  def test_is_sub_resource(self, registry: ResourceHierarchyRegistry) -> None:
    """Test is_sub_resource classification."""
    assert registry.is_sub_resource("Well") is True
    assert registry.is_sub_resource("TipSpot") is True
    assert registry.is_sub_resource("Tube") is True
    assert registry.is_sub_resource("Plate") is False
    assert registry.is_sub_resource("TipRack") is False

  def test_is_carrier(self, registry: ResourceHierarchyRegistry) -> None:
    """Test is_carrier classification."""
    assert registry.is_carrier("PlateCarrier") is True
    assert registry.is_carrier("TipCarrier") is True
    assert registry.is_carrier("Carrier") is True
    assert registry.is_carrier("Plate") is False
    assert registry.is_carrier("Well") is False

  def test_is_container(self, registry: ResourceHierarchyRegistry) -> None:
    """Test is_container classification."""
    assert registry.is_container("Plate") is True
    assert registry.is_container("TipRack") is True
    assert registry.is_container("Trough") is True
    assert registry.is_container("Well") is False
    assert registry.is_container("PlateCarrier") is False

  # --- Child Element Types ---

  def test_get_child_element_type_plate(self, registry: ResourceHierarchyRegistry) -> None:
    """Test getting child element type for Plate."""
    assert registry.get_child_element_type("Plate") == "Well"

  def test_get_child_element_type_tiprack(self, registry: ResourceHierarchyRegistry) -> None:
    """Test getting child element type for TipRack."""
    assert registry.get_child_element_type("TipRack") == "TipSpot"

  def test_get_child_element_type_tuberack(self, registry: ResourceHierarchyRegistry) -> None:
    """Test getting child element type for TubeRack."""
    assert registry.get_child_element_type("TubeRack") == "Tube"

  def test_get_child_element_type_non_container(
    self, registry: ResourceHierarchyRegistry
  ) -> None:
    """Test getting child element type for non-container returns None."""
    assert registry.get_child_element_type("Well") is None
    assert registry.get_child_element_type("PlateCarrier") is None

  # --- Immediate Parent ---

  def test_get_immediate_parent_well(self, registry: ResourceHierarchyRegistry) -> None:
    """Test getting immediate parent of Well."""
    assert registry.get_immediate_parent_type("Well") == "Plate"

  def test_get_immediate_parent_plate_carrier_based(
    self, registry: ResourceHierarchyRegistry
  ) -> None:
    """Test getting immediate parent of Plate on carrier-based deck."""
    assert (
      registry.get_immediate_parent_type("Plate", DeckLayoutType.CARRIER_BASED)
      == "PlateCarrier"
    )

  def test_get_immediate_parent_plate_slot_based(
    self, registry: ResourceHierarchyRegistry
  ) -> None:
    """Test getting immediate parent of Plate on slot-based deck."""
    assert registry.get_immediate_parent_type("Plate", DeckLayoutType.SLOT_BASED) == "Slot"

  # --- Custom Type Registration ---

  def test_register_custom_type(self, registry: ResourceHierarchyRegistry) -> None:
    """Test registering a custom resource type."""
    registry.register_type("CustomPlate", ResourceCategory.PLATE)
    assert registry.get_category("CustomPlate") == ResourceCategory.PLATE
    assert registry.is_container("CustomPlate") is True


class TestParentalChainModel:
  """Tests for ParentalChain model properties."""

  def test_requires_carrier_true(self) -> None:
    """Test requires_carrier property when chain has carrier."""
    chain = get_parental_chain("Well", DeckLayoutType.CARRIER_BASED)
    assert "PlateCarrier" in chain.chain
    assert chain.requires_carrier is True

  def test_requires_carrier_false_slot_based(self) -> None:
    """Test requires_carrier property on slot-based deck."""
    chain = get_parental_chain("Plate", DeckLayoutType.SLOT_BASED)
    assert chain.requires_carrier is False

  def test_immediate_parent_property(self) -> None:
    """Test immediate_parent property."""
    chain = get_parental_chain("Well")
    assert chain.immediate_parent == "Plate"

  def test_immediate_parent_none_for_deck(self) -> None:
    """Test immediate_parent is None for Deck."""
    chain = get_parental_chain("Deck")
    assert chain.immediate_parent is None


class TestModuleLevelFunctions:
  """Tests for module-level convenience functions."""

  def test_get_registry_returns_singleton(self) -> None:
    """Test that get_registry returns the same instance."""
    reg1 = get_registry()
    reg2 = get_registry()
    assert reg1 is reg2

  def test_get_parental_chain_convenience(self) -> None:
    """Test get_parental_chain convenience function."""
    chain = get_parental_chain("Well")
    assert chain.chain == ["Plate", "PlateCarrier", "Deck"]

  def test_infer_deck_type_convenience(self) -> None:
    """Test infer_deck_type convenience function."""
    assert infer_deck_type("OTDeck") == DeckLayoutType.SLOT_BASED
    assert infer_deck_type("HamiltonSTAR") == DeckLayoutType.CARRIER_BASED


class TestDeckLayoutType:
  """Tests for DeckLayoutType enum."""

  def test_slot_based_value(self) -> None:
    """Test SLOT_BASED enum value."""
    assert DeckLayoutType.SLOT_BASED.value == "slot_based"

  def test_carrier_based_value(self) -> None:
    """Test CARRIER_BASED enum value."""
    assert DeckLayoutType.CARRIER_BASED.value == "carrier_based"


class TestCarrierTypes:
  """Tests for CARRIER_TYPES constant."""

  def test_contains_all_carrier_categories(self) -> None:
    """Test that CARRIER_TYPES contains all carrier categories."""
    assert ResourceCategory.PLATE_CARRIER in CARRIER_TYPES
    assert ResourceCategory.TIP_CARRIER in CARRIER_TYPES
    assert ResourceCategory.TROUGH_CARRIER in CARRIER_TYPES
    assert ResourceCategory.CARRIER in CARRIER_TYPES

  def test_does_not_contain_non_carriers(self) -> None:
    """Test that CARRIER_TYPES doesn't contain non-carrier categories."""
    assert ResourceCategory.PLATE not in CARRIER_TYPES
    assert ResourceCategory.WELL not in CARRIER_TYPES
    assert ResourceCategory.DECK not in CARRIER_TYPES
