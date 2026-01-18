"""Resource factory function visitor for PLR static analysis.

This visitor detects factory functions that return PLR resource types
(Plate, TipRack, Trough, etc.) and extracts their metadata.

PLR defines most resources as factory functions like:
    def Cor_96_wellplate_360ul_Fb(name: str, with_lid: bool = False) -> Plate:
        return Plate(...)

This visitor captures these function-based resource definitions.
"""

from typing import Any

import libcst as cst

from praxis.backend.utils.plr_static_analysis.models import (
  DiscoveredCapabilities,
  DiscoveredClass,
  PLRClassType,
)

# Resource types that factory functions can return
RESOURCE_RETURN_TYPES: frozenset[str] = frozenset(
  {
    "Plate",
    "TipRack",
    "Trough",
    "Lid",
    "Carrier",
    "PlateCarrier",
    "TipCarrier",
    "TroughCarrier",
    "Container",
    "PetriDish",
    "TubeRack",
    "Tube",
    "Well",
    "Resource",
    "HamiltonSTARDeck",
    "STARLetDeck",
    "VantageDeck",
    "Deck",
    "HamiltonDeck",
  }
)

# Map return types to resource categories
RETURN_TYPE_TO_CATEGORY: dict[str, str] = {
  "Plate": "Plate",
  "TipRack": "TipRack",
  "Trough": "Trough",
  "Lid": "Lid",
  "Carrier": "Carrier",
  "PlateCarrier": "PlateCarrier",
  "TipCarrier": "TipCarrier",
  "TroughCarrier": "TroughCarrier",
  "Container": "Container",
  "PetriDish": "PetriDish",
  "TubeRack": "TubeRack",
  "Tube": "Tube",
  "Well": "Well",
  "Resource": "Resource",
  "HamiltonSTARDeck": "Deck",
  "STARLetDeck": "Deck",
  "VantageDeck": "Deck",
  "Deck": "Deck",
  "HamiltonDeck": "Deck",
}


class ResourceFactoryVisitor(cst.CSTVisitor):
  """Discovers factory functions that return PLR resource types."""

  def __init__(self, module_path: str, file_path: str) -> None:
    """Initialize the visitor.

    Args:
      module_path: The Python module path (e.g., 'pylabrobot.resources.corning.plates')
      file_path: The absolute file path to the source file

    """
    self.module_path = module_path
    self.file_path = file_path
    self.discovered_resources: list[DiscoveredClass] = []

  def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:  # noqa: N802
    """Visit a function definition to check if it's a resource factory.

    Args:
      node: The function definition node.

    Returns:
      True to continue visiting nested functions.

    """
    func_name = node.name.value

    # Skip private/dunder functions
    if func_name.startswith("_"):
      return True

    # Check return annotation
    return_type = self._extract_return_type(node)
    if return_type is None or return_type not in RESOURCE_RETURN_TYPES:
      return True

    # Skip deprecated functions (check for raise statements in body)
    if self._is_deprecated_function(node):
      return True

    # Extract metadata from the factory function
    fqn = f"{self.module_path}.{func_name}"
    docstring = self._get_docstring(node.body)
    category = RETURN_TYPE_TO_CATEGORY.get(return_type, "Resource")

    # Extract additional metadata from the return statement
    extra_metadata = self._extract_return_metadata(node)

    # Determine class type
    class_type = PLRClassType.RESOURCE
    if category == "Deck":
      class_type = PLRClassType.DECK

    # Create discovered class
    discovered = DiscoveredClass(
      fqn=fqn,
      name=func_name,
      module_path=self.module_path,
      file_path=self.file_path,
      class_type=class_type,
      base_classes=[return_type],
      is_abstract=False,
      docstring=docstring,
      capabilities=DiscoveredCapabilities(),
      category=category,
      # Extract vendor from module path
      vendor=self._infer_vendor_from_module(),
      manufacturer=extra_metadata.get("manufacturer"),
    )
    self.discovered_resources.append(discovered)

    return True

  def _extract_return_type(self, node: cst.FunctionDef) -> str | None:
    """Extract the return type annotation from a function.

    Args:
      node: The function definition node.

    Returns:
      The return type name, or None if not annotated or not a simple type.

    """
    if node.returns is None:
      return None

    annotation = node.returns.annotation

    # Handle simple Name annotation (e.g., -> Plate)
    if isinstance(annotation, cst.Name):
      return annotation.value

    # Handle Attribute annotation (e.g., -> resources.Plate)
    if isinstance(annotation, cst.Attribute):
      return annotation.attr.value

    return None

  def _is_deprecated_function(self, node: cst.FunctionDef) -> bool:
    """Check if a function is deprecated (raises error).

    Args:
      node: The function definition node.

    Returns:
      True if the function appears to be deprecated.

    """
    # Check if body is an indented block
    if not isinstance(node.body, cst.IndentedBlock):
      return False

    # Look for raise statements as the only meaningful body
    for stmt in node.body.body:
      if isinstance(stmt, cst.SimpleStatementLine):
        for simple_stmt in stmt.body:
          if isinstance(simple_stmt, cst.Raise):
            return True

    return False

  def _get_docstring(self, body: cst.BaseSuite) -> str | None:
    """Extract docstring from function body.

    Args:
      body: The function body.

    Returns:
      The docstring content, or None if no docstring.

    """
    if not isinstance(body, cst.IndentedBlock):
      return None

    if not body.body:
      return None

    first = body.body[0]
    if isinstance(first, cst.SimpleStatementLine):
      for stmt in first.body:
        if isinstance(stmt, cst.Expr) and isinstance(stmt.value, cst.SimpleString):
          # Extract string content (remove quotes)
          raw = stmt.value.value
          # Remove triple quotes
          if raw.startswith(('"""', "'''")):
            return raw[3:-3].strip()
          # Remove single/double quotes
          if raw.startswith(('"', "'")):
            return raw[1:-1].strip()

    return None

  def _extract_return_metadata(self, node: cst.FunctionDef) -> dict[str, Any]:
    """Extract metadata from the return statement's constructor call.

    Args:
      node: The function definition node.

    Returns:
      Dictionary of extracted metadata.

    """
    metadata: dict[str, Any] = {}

    if not isinstance(node.body, cst.IndentedBlock):
      return metadata

    # Find the return statement and extract arguments
    for stmt in node.body.body:
      if isinstance(stmt, cst.SimpleStatementLine):
        for simple_stmt in stmt.body:
          if isinstance(simple_stmt, cst.Return) and simple_stmt.value:
            metadata.update(self._extract_call_args(simple_stmt.value))
            break

    return metadata

  def _extract_call_args(self, expr: cst.BaseExpression) -> dict[str, Any]:
    """Extract keyword arguments from a Call expression.

    Args:
      expr: The expression (expected to be a Call).

    Returns:
      Dictionary of argument names to values.

    """
    result: dict[str, Any] = {}

    if not isinstance(expr, cst.Call):
      return result

    for arg in expr.args:
      if arg.keyword is not None:
        key = arg.keyword.value
        value = self._extract_literal_value(arg.value)
        if value is not None:
          result[key] = value

    return result

  def _extract_literal_value(self, node: cst.BaseExpression | None) -> Any:
    """Extract a literal value from a CST expression.

    Args:
      node: The expression node.

    Returns:
      The Python value, or None if not a simple literal.

    """
    if node is None:
      return None
    if isinstance(node, cst.Integer):
      return int(node.value, 0)
    if isinstance(node, cst.Float):
      return float(node.value)
    if isinstance(node, cst.SimpleString):
      raw = node.value
      if raw.startswith(('"""', "'''")):
        return raw[3:-3]
      if raw.startswith(('"', "'")):
        return raw[1:-1]
    if isinstance(node, cst.Name):
      if node.value == "True":
        return True
      if node.value == "False":
        return False
      if node.value == "None":
        return None
    return None

  def _infer_vendor_from_module(self) -> str | None:
    """Infer vendor from module path.

    Returns:
      The vendor name, or None if not detectable.

    """
    parts = self.module_path.lower().split(".")

    # Known vendor patterns
    vendor_map = {
      "corning": "Corning",
      "hamilton": "Hamilton",
      "greiner": "Greiner",
      "eppendorf": "Eppendorf",
      "thermo_fisher": "Thermo Fisher",
      "thermofisher": "Thermo Fisher",
      "opentrons": "Opentrons",
      "tecan": "Tecan",
      "revvity": "Revvity",
      "vwr": "VWR",
      "cellvis": "CellVis",
      "perkin_elmer": "PerkinElmer",
      "azenta": "Azenta",
      "agilent": "Agilent",
      "alpaqua": "Alpaqua",
      "biorad": "Bio-Rad",
      "boekel": "Boekel",
      "limbro": "Limbro",
      "ml_star": "Hamilton",
      "sarstedt": "Sarstedt",
      "starlab": "Starlab",
      "porvair": "Porvair",
    }

    for part in parts:
      if part in vendor_map:
        return vendor_map[part]

    return None
