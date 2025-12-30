"""Protocol requirement extraction visitor for inferring hardware capabilities.

This visitor analyzes protocol function bodies to infer required hardware
capabilities from method calls and type hints.
"""

import libcst as cst

from praxis.backend.utils.plr_static_analysis.models import (
  CapabilityRequirement,
  ProtocolRequirements,
)


# =============================================================================
# Method Call Patterns and Their Implied Requirements
# =============================================================================

# Liquid Handler method patterns
LH_METHOD_REQUIREMENTS: dict[str, list[tuple[str, object]]] = {
  # Core 96 head methods
  "pick_up_tips96": [("has_core96", True)],
  "drop_tips96": [("has_core96", True)],
  "aspirate96": [("has_core96", True)],
  "dispense96": [("has_core96", True)],
  # iSWAP (integrated swap) methods
  "move_plate": [("has_iswap", True)],
  "get_plate": [("has_iswap", True)],
  "put_plate": [("has_iswap", True)],
  "move_lid": [("has_iswap", True)],
  # Basic liquid handling (implies liquid handler)
  "aspirate": [],
  "dispense": [],
  "pick_up_tips": [],
  "drop_tips": [],
}

# Plate Reader method patterns
PR_METHOD_REQUIREMENTS: dict[str, list[tuple[str, object]]] = {
  "read_absorbance": [("absorbance", True)],
  "read_fluorescence": [("fluorescence", True)],
  "read_luminescence": [("luminescence", True)],
  "read_image": [("imaging", True)],
  "capture_image": [("imaging", True)],
}

# Heater Shaker method patterns
HS_METHOD_REQUIREMENTS: dict[str, list[tuple[str, object]]] = {
  "set_temperature": [],
  "start_shaking": [],
  "heat_shake": [],
  "cool": [("has_cooling", True)],
}

# Method prefixes that indicate machine type
MACHINE_TYPE_FROM_METHOD_PREFIX: dict[str, str] = {
  "aspirate": "liquid_handler",
  "dispense": "liquid_handler",
  "pick_up": "liquid_handler",
  "drop_tips": "liquid_handler",
  "read_absorbance": "plate_reader",
  "read_fluorescence": "plate_reader",
  "read_luminescence": "plate_reader",
  "shake": "heater_shaker",
  "heat": "heater_shaker",
  "centrifuge": "centrifuge",
  "spin": "centrifuge",
}

# Variable name patterns that indicate machine type
MACHINE_VAR_PATTERNS: dict[str, str] = {
  "lh": "liquid_handler",
  "liquid_handler": "liquid_handler",
  "pr": "plate_reader",
  "plate_reader": "plate_reader",
  "reader": "plate_reader",
  "hs": "heater_shaker",
  "heater_shaker": "heater_shaker",
  "shaker": "shaker",
  "centrifuge": "centrifuge",
  "cf": "centrifuge",
}


class ProtocolRequirementExtractor(cst.CSTVisitor):
  """Extracts hardware capability requirements from protocol function bodies.

  This visitor analyzes method calls within a protocol function to infer
  required hardware capabilities. For example:
    - `lh.pick_up_tips96()` implies `has_core96=True`
    - `lh.move_plate()` implies `has_iswap=True`
    - `pr.read_absorbance()` implies `absorbance=True`

  Usage:
    extractor = ProtocolRequirementExtractor()
    tree.walk(extractor)
    requirements = extractor.build_requirements()
  """

  def __init__(self) -> None:
    """Initialize the requirement extractor."""
    self._requirements: list[CapabilityRequirement] = []
    self._seen_requirements: set[tuple[str, object]] = set()
    self._machine_types: set[str] = set()
    self._method_calls: list[str] = []

  def visit_Call(self, node: cst.Call) -> bool:
    """Visit method calls to detect capability requirements.

    Args:
      node: The call expression node.

    Returns:
      True to continue visiting child nodes.
    """
    # Handle method calls like `lh.pick_up_tips96()`
    if isinstance(node.func, cst.Attribute):
      method_name = node.func.attr.value
      self._method_calls.append(method_name)

      # Extract the receiver name (e.g., "lh" from "lh.pick_up_tips96()")
      receiver_name = self._get_receiver_name(node.func.value)

      # Infer machine type from receiver name
      if receiver_name:
        lower_receiver = receiver_name.lower()
        for pattern, machine_type in MACHINE_VAR_PATTERNS.items():
          if pattern in lower_receiver:
            self._machine_types.add(machine_type)
            break

      # Check liquid handler methods
      if method_name in LH_METHOD_REQUIREMENTS:
        self._machine_types.add("liquid_handler")
        for cap_name, cap_value in LH_METHOD_REQUIREMENTS[method_name]:
          self._add_requirement(
            cap_name,
            cap_value,
            f"{receiver_name or '?'}.{method_name}()",
            "liquid_handler",
          )

      # Check plate reader methods
      elif method_name in PR_METHOD_REQUIREMENTS:
        self._machine_types.add("plate_reader")
        for cap_name, cap_value in PR_METHOD_REQUIREMENTS[method_name]:
          self._add_requirement(
            cap_name,
            cap_value,
            f"{receiver_name or '?'}.{method_name}()",
            "plate_reader",
          )

      # Check heater shaker methods
      elif method_name in HS_METHOD_REQUIREMENTS:
        self._machine_types.add("heater_shaker")
        for cap_name, cap_value in HS_METHOD_REQUIREMENTS[method_name]:
          self._add_requirement(
            cap_name,
            cap_value,
            f"{receiver_name or '?'}.{method_name}()",
            "heater_shaker",
          )

      # Fallback: infer machine type from method prefix
      else:
        for prefix, machine_type in MACHINE_TYPE_FROM_METHOD_PREFIX.items():
          if method_name.startswith(prefix):
            self._machine_types.add(machine_type)
            break

    return True

  def _get_receiver_name(self, node: cst.BaseExpression) -> str | None:
    """Extract the receiver name from an attribute access.

    Args:
      node: The expression being accessed (e.g., "lh" in "lh.method()").

    Returns:
      The name as a string, or None if not a simple name.
    """
    if isinstance(node, cst.Name):
      return node.value
    if isinstance(node, cst.Attribute):
      # Handle chained access like `self.lh.method()`
      return node.attr.value
    return None

  def _add_requirement(
    self,
    capability_name: str,
    expected_value: object,
    inferred_from: str,
    machine_type: str | None = None,
  ) -> None:
    """Add a capability requirement if not already seen.

    Args:
      capability_name: The capability name (e.g., "has_core96").
      expected_value: The expected value (e.g., True).
      inferred_from: Source code that triggered this inference.
      machine_type: Optional machine type this requirement applies to.
    """
    key = (capability_name, expected_value)
    if key not in self._seen_requirements:
      self._seen_requirements.add(key)
      self._requirements.append(
        CapabilityRequirement(
          capability_name=capability_name,
          expected_value=expected_value,
          inferred_from=inferred_from,
          machine_type=machine_type,
        ),
      )

  def build_requirements(self) -> ProtocolRequirements:
    """Build the final ProtocolRequirements object.

    Returns:
      ProtocolRequirements with all inferred requirements.
    """
    # Determine primary machine type (most common or first seen)
    primary_type = None
    if self._machine_types:
      # Prioritize liquid_handler as it's most common
      if "liquid_handler" in self._machine_types:
        primary_type = "liquid_handler"
      else:
        primary_type = next(iter(self._machine_types))

    return ProtocolRequirements(
      machine_type=primary_type,
      requirements=self._requirements,
    )

  @property
  def requirements(self) -> list[CapabilityRequirement]:
    """Get the list of discovered requirements."""
    return self._requirements

  @property
  def machine_types(self) -> set[str]:
    """Get all discovered machine types."""
    return self._machine_types


def extract_requirements_from_source(source: str) -> ProtocolRequirements:
  """Extract hardware requirements from Python source code.

  Args:
    source: Python source code to analyze.

  Returns:
    ProtocolRequirements inferred from the code.
  """
  from libcst.metadata import MetadataWrapper

  try:
    tree = cst.parse_module(source)
  except cst.ParserSyntaxError:
    return ProtocolRequirements()

  extractor = ProtocolRequirementExtractor()

  # Use MetadataWrapper to properly walk the visitor
  try:
    wrapper = MetadataWrapper(tree)
    wrapper.visit(extractor)
  except Exception:
    # Fall back to manual tree traversal if metadata fails
    _visit_tree_manually(tree, extractor)

  return extractor.build_requirements()


def _visit_tree_manually(tree: cst.Module, extractor: ProtocolRequirementExtractor) -> None:
  """Manually traverse the CST tree to visit all Call nodes.

  Args:
    tree: The parsed CST module.
    extractor: The extractor visitor to populate.
  """
  # Simple recursive traversal to find all Call nodes
  def visit_node(node: cst.CSTNode) -> None:
    if isinstance(node, cst.Call):
      extractor.visit_Call(node)
    # Recurse into child nodes
    for child in node.children:
      visit_node(child)

  for stmt in tree.body:
    visit_node(stmt)
