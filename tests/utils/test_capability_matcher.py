"""Tests for capability matching components (Phase 4).

Tests cover:
- CapabilityRequirement, ProtocolRequirements, CapabilityMatchResult models
- ProtocolRequirementExtractor visitor
- CapabilityMatcherService
"""


from praxis.backend.services.capability_matcher import CapabilityMatcherService
from praxis.backend.utils.plr_static_analysis.models import (
  CapabilityMatchResult,
  CapabilityRequirement,
  ProtocolRequirements,
)
from praxis.backend.utils.plr_static_analysis.visitors.protocol_requirement_extractor import (
  extract_requirements_from_source,
)

# =============================================================================
# Pydantic Model Tests
# =============================================================================


class TestCapabilityRequirement:
  """Tests for CapabilityRequirement model."""

  def test_basic_requirement(self) -> None:
    """Test creating a basic requirement."""
    req = CapabilityRequirement(
      capability_name="has_core96",
      expected_value=True,
    )
    assert req.capability_name == "has_core96"
    assert req.expected_value is True
    assert req.operator == "eq"

  def test_requirement_with_operator(self) -> None:
    """Test requirement with non-default operator."""
    req = CapabilityRequirement(
      capability_name="channels",
      expected_value=8,
      operator="gte",
    )
    assert req.operator == "gte"
    assert req.expected_value == 8

  def test_requirement_with_inference_source(self) -> None:
    """Test requirement with inferred_from field."""
    req = CapabilityRequirement(
      capability_name="has_iswap",
      expected_value=True,
      inferred_from="lh.move_plate()",
      machine_type="liquid_handler",
    )
    assert req.inferred_from == "lh.move_plate()"
    assert req.machine_type == "liquid_handler"


class TestProtocolRequirements:
  """Tests for ProtocolRequirements model."""

  def test_empty_requirements(self) -> None:
    """Test empty requirements."""
    reqs = ProtocolRequirements()
    assert reqs.machine_type is None
    assert reqs.requirements == []

  def test_requirements_with_items(self) -> None:
    """Test requirements with items."""
    reqs = ProtocolRequirements(
      machine_type="liquid_handler",
      requirements=[
        CapabilityRequirement(capability_name="has_core96", expected_value=True),
        CapabilityRequirement(capability_name="has_iswap", expected_value=True),
      ],
    )
    assert reqs.machine_type == "liquid_handler"
    assert len(reqs.requirements) == 2


class TestCapabilityMatchResult:
  """Tests for CapabilityMatchResult model."""

  def test_compatible_result(self) -> None:
    """Test a compatible result."""
    result = CapabilityMatchResult(
      is_compatible=True,
      matched_capabilities=["has_core96", "has_iswap"],
    )
    assert result.is_compatible is True
    assert len(result.missing_capabilities) == 0

  def test_incompatible_result(self) -> None:
    """Test an incompatible result with missing capabilities."""
    missing = CapabilityRequirement(capability_name="has_core96", expected_value=True)
    result = CapabilityMatchResult(
      is_compatible=False,
      missing_capabilities=[missing],
    )
    assert result.is_compatible is False
    assert len(result.missing_capabilities) == 1


# =============================================================================
# ProtocolRequirementExtractor Tests
# =============================================================================


class TestProtocolRequirementExtractor:
  """Tests for ProtocolRequirementExtractor visitor."""

  def test_extract_core96_requirement(self) -> None:
    """Test extraction of Core96 requirement from pick_up_tips96 call."""
    source = """
def my_protocol(lh):
    lh.pick_up_tips96(tips)
    lh.aspirate96(plate, 100)
    lh.drop_tips96()
"""
    reqs = extract_requirements_from_source(source)
    assert reqs.machine_type == "liquid_handler"
    assert len(reqs.requirements) >= 1
    cap_names = [r.capability_name for r in reqs.requirements]
    assert "has_core96" in cap_names

  def test_extract_iswap_requirement(self) -> None:
    """Test extraction of iSWAP requirement from move_plate call."""
    source = """
def transport_protocol(lh):
    lh.move_plate(source, target)
    lh.get_plate(storage)
"""
    reqs = extract_requirements_from_source(source)
    assert reqs.machine_type == "liquid_handler"
    cap_names = [r.capability_name for r in reqs.requirements]
    assert "has_iswap" in cap_names

  def test_extract_plate_reader_requirement(self) -> None:
    """Test extraction of plate reader requirement."""
    source = """
def read_protocol(pr):
    pr.read_absorbance(plate, wavelength=450)
    pr.read_fluorescence(plate, ex=485, em=520)
"""
    reqs = extract_requirements_from_source(source)
    assert reqs.machine_type == "plate_reader"
    cap_names = [r.capability_name for r in reqs.requirements]
    assert "absorbance" in cap_names
    assert "fluorescence" in cap_names

  def test_extract_no_requirements(self) -> None:
    """Test extraction from code with no capability methods."""
    source = """
def simple_function():
    x = 1 + 2
    return x
"""
    reqs = extract_requirements_from_source(source)
    assert reqs.machine_type is None
    assert len(reqs.requirements) == 0

  def test_extract_basic_liquid_handler(self) -> None:
    """Test extraction with basic aspirate/dispense (no special caps)."""
    source = """
def basic_protocol(lh):
    lh.aspirate(plate, [[100]])
    lh.dispense(plate2, [[100]])
"""
    reqs = extract_requirements_from_source(source)
    # Should detect liquid_handler type but no special requirements
    assert reqs.machine_type == "liquid_handler"


# =============================================================================
# CapabilityMatcherService Tests
# =============================================================================


class TestCapabilityMatcherService:
  """Tests for CapabilityMatcherService."""

  def test_check_requirement_eq(self) -> None:
    """Test equality check."""
    matcher = CapabilityMatcherService()
    req = CapabilityRequirement(
      capability_name="has_core96",
      expected_value=True,
      operator="eq",
    )
    assert matcher._check_requirement(req, {"has_core96": True}) is True
    assert matcher._check_requirement(req, {"has_core96": False}) is False
    assert matcher._check_requirement(req, {}) is False

  def test_check_requirement_gte(self) -> None:
    """Test greater-than-or-equal check."""
    matcher = CapabilityMatcherService()
    req = CapabilityRequirement(
      capability_name="channels",
      expected_value=8,
      operator="gte",
    )
    assert matcher._check_requirement(req, {"channels": 8}) is True
    assert matcher._check_requirement(req, {"channels": 16}) is True
    assert matcher._check_requirement(req, {"channels": 4}) is False

  def test_check_requirement_in(self) -> None:
    """Test 'in' operator check."""
    matcher = CapabilityMatcherService()
    req = CapabilityRequirement(
      capability_name="modules",
      expected_value="iswap",
      operator="in",
    )
    assert matcher._check_requirement(req, {"modules": ["iswap", "core96"]}) is True
    assert matcher._check_requirement(req, {"modules": ["core96"]}) is False

  def test_parse_empty_requirements(self) -> None:
    """Test parsing empty/None requirements."""
    matcher = CapabilityMatcherService()
    reqs = matcher._parse_requirements(None)
    assert reqs.requirements == []

    reqs = matcher._parse_requirements({})
    assert reqs.requirements == []

  def test_parse_valid_requirements(self) -> None:
    """Test parsing valid requirements JSON."""
    matcher = CapabilityMatcherService()
    json_data = {
      "machine_type": "liquid_handler",
      "requirements": [
        {"capability_name": "has_core96", "expected_value": True},
      ],
    }
    reqs = matcher._parse_requirements(json_data)
    assert reqs.machine_type == "liquid_handler"
    assert len(reqs.requirements) == 1
