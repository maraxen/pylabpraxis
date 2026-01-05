"""Type annotation analysis utilities for index selector inference.

This module provides utilities for analyzing CST type annotations to detect
types that should be rendered as visual index selectors (Well, TipSpot, etc.)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import libcst as cst


# =============================================================================
# ANSI/SBS Standard Plate Dimensions
# =============================================================================

# Standard ANSI/SLAS plate formats
# https://www.slas.org/resources/library/standards/
ANSI_SBS_PLATE_DIMENSIONS: dict[int, tuple[int, int]] = {
  6: (3, 2),  # 6-well plate
  12: (4, 3),  # 12-well plate
  24: (6, 4),  # 24-well plate
  48: (8, 6),  # 48-well plate
  96: (12, 8),  # 96-well plate (default)
  384: (24, 16),  # 384-well plate
  1536: (48, 32),  # 1536-well plate
}

# Default dimensions (96-well plate)
DEFAULT_ITEMS_X = 12
DEFAULT_ITEMS_Y = 8


def get_standard_dimensions(num_wells: int | None = None) -> tuple[int, int]:
  """Get ANSI/SBS standard dimensions for a plate.

  Args:
      num_wells: Number of wells. If None, returns 96-well default.

  Returns:
      Tuple of (items_x, items_y).
  """
  if num_wells is None:
    return (DEFAULT_ITEMS_X, DEFAULT_ITEMS_Y)
  return ANSI_SBS_PLATE_DIMENSIONS.get(num_wells, (DEFAULT_ITEMS_X, DEFAULT_ITEMS_Y))


# =============================================================================
# Type Annotation Analysis
# =============================================================================

# Known itemized resource types that should use index selector
ITEMIZED_ELEMENT_TYPES: frozenset[str] = frozenset(
  {
    "Well",
    "TipSpot",
    "Tube",  # Less common but possible
  }
)

# Container type names that wrap itemized types
CONTAINER_TYPE_NAMES: frozenset[str] = frozenset(
  {
    "list",
    "List",
    "Sequence",
    "tuple",
    "Tuple",
    "Set",
    "set",
    "frozenset",
    "FrozenSet",
    "Iterable",
    "Iterator",
    "Collection",
  }
)

# Optional/Union type names
OPTIONAL_TYPE_NAMES: frozenset[str] = frozenset(
  {
    "Optional",
    "Union",
  }
)


@dataclass
class ItemizedTypeInfo:
  """Information about an itemized type detected from annotation."""

  field_type: str = "index_selector"
  """The field type for Formly."""

  is_itemized: bool = True
  """Whether this is an itemized type."""

  element_type: str = "Well"
  """The element type (Well, TipSpot, etc.)."""

  is_container: bool = False
  """Whether this is a container of itemized elements."""

  items_x: int = DEFAULT_ITEMS_X
  """Number of columns (default 96-well)."""

  items_y: int = DEFAULT_ITEMS_Y
  """Number of rows (default 96-well)."""

  def to_dict(self) -> dict[str, Any]:
    """Convert to dict for ProtocolParameterInfo."""
    return {
      "field_type": self.field_type,
      "is_itemized": self.is_itemized,
      "itemized_spec": {
        "items_x": self.items_x,
        "items_y": self.items_y,
      },
    }


class TypeAnnotationAnalyzer:
  """Analyzes CST type annotation nodes to detect itemized types.

  This class recursively parses type annotations to find Well, TipSpot,
  and other itemized resource types, including when wrapped in containers
  like list[Well], Sequence[TipSpot], tuple[Well, ...], Optional[Well], etc.

  Usage:
      analyzer = TypeAnnotationAnalyzer()
      info = analyzer.analyze(annotation_node)
      if info:
          # Type should use index selector
          field_type = info.field_type
          itemized_spec = {"items_x": info.items_x, "items_y": info.items_y}
  """

  def analyze(self, node: cst.BaseExpression) -> ItemizedTypeInfo | None:
    """Analyze a type annotation node for itemized types.

    Args:
        node: The LibCST annotation node.

    Returns:
        ItemizedTypeInfo if itemized type detected, None otherwise.
    """
    return self._analyze_node(node, is_inside_container=False)

  def _analyze_node(
    self, node: cst.BaseExpression, is_inside_container: bool
  ) -> ItemizedTypeInfo | None:
    """Recursively analyze a type annotation node.

    Args:
        node: The CST node to analyze.
        is_inside_container: Whether we're inside a container type.

    Returns:
        ItemizedTypeInfo if itemized type found, None otherwise.
    """
    # Handle Name nodes: Well, TipSpot
    if isinstance(node, cst.Name):
      if node.value in ITEMIZED_ELEMENT_TYPES:
        return ItemizedTypeInfo(
          element_type=node.value,
          is_container=is_inside_container,
        )
      return None

    # Handle Attribute nodes: pylabrobot.resources.Well
    if isinstance(node, cst.Attribute):
      if node.attr.value in ITEMIZED_ELEMENT_TYPES:
        return ItemizedTypeInfo(
          element_type=node.attr.value,
          is_container=is_inside_container,
        )
      return None

    # Handle Subscript nodes: list[Well], Sequence[TipSpot], tuple[Well, ...]
    if isinstance(node, cst.Subscript):
      return self._analyze_subscript(node, is_inside_container)

    # Handle BinaryOperation nodes: Well | None (Python 3.10+ union syntax)
    if isinstance(node, cst.BinaryOperation):
      if isinstance(node.operator, cst.BitOr):
        # Check left side
        left_result = self._analyze_node(node.left, is_inside_container)
        if left_result:
          return left_result
        # Check right side
        right_result = self._analyze_node(node.right, is_inside_container)
        if right_result:
          return right_result
      return None

    return None

  def _analyze_subscript(
    self, node: cst.Subscript, is_inside_container: bool
  ) -> ItemizedTypeInfo | None:
    """Analyze a subscript type annotation.

    Handles: list[Well], Sequence[TipSpot], Optional[Well],
             tuple[Well, ...], Union[Well, None], etc.
    """
    base = node.value

    # Get the base type name
    base_name = None
    if isinstance(base, cst.Name):
      base_name = base.value
    elif isinstance(base, cst.Attribute):
      # typing.Sequence, typing.Optional, etc.
      base_name = base.attr.value

    if base_name is None:
      return None

    # Is it a container type?
    if base_name in CONTAINER_TYPE_NAMES:
      # Analyze inner types
      for element in node.slice:
        if isinstance(element, cst.SubscriptElement):
          inner_node = self._get_subscript_element_value(element)
          if inner_node:
            result = self._analyze_node(inner_node, is_inside_container=True)
            if result:
              return result

    # Is it an Optional or Union type?
    if base_name in OPTIONAL_TYPE_NAMES:
      # Analyze inner types (skip None)
      for element in node.slice:
        if isinstance(element, cst.SubscriptElement):
          inner_node = self._get_subscript_element_value(element)
          if inner_node and not self._is_none_type(inner_node):
            result = self._analyze_node(inner_node, is_inside_container)
            if result:
              return result

    return None

  def _get_subscript_element_value(
    self, element: cst.SubscriptElement
  ) -> cst.BaseExpression | None:
    """Extract the value from a subscript element."""
    slice_val = element.slice

    if isinstance(slice_val, cst.Index):
      return slice_val.value
    elif isinstance(slice_val, cst.Slice):
      # tuple[Well, ...] - the element type is before the comma
      return None  # Handled by iterating elements
    elif isinstance(slice_val, cst.BaseExpression):
      return slice_val

    return None

  def _is_none_type(self, node: cst.BaseExpression) -> bool:
    """Check if a node represents None type."""
    if isinstance(node, cst.Name):
      return node.value in ("None", "NoneType")
    return False


def analyze_type_hint_string(type_hint: str) -> ItemizedTypeInfo | None:
  """Analyze a type hint string for itemized types.

  This is a convenience function for when you have a string representation
  rather than a CST node.

  Args:
      type_hint: The type hint as a string (e.g., "Sequence[Well]")

  Returns:
      ItemizedTypeInfo if itemized type detected, None otherwise.
  """
  try:
    # Parse as an expression
    module = cst.parse_module(f"x: {type_hint}")
    stmt = module.body[0]
    if isinstance(stmt, cst.SimpleStatementLine):
      inner = stmt.body[0]
      if isinstance(inner, cst.AnnAssign) and inner.annotation:
        analyzer = TypeAnnotationAnalyzer()
        return analyzer.analyze(inner.annotation.annotation)
  except Exception:
    pass

  # Fallback to simple string matching (legacy behavior)
  for elem_type in ITEMIZED_ELEMENT_TYPES:
    if elem_type in type_hint:
      is_container = any(c in type_hint for c in CONTAINER_TYPE_NAMES)
      return ItemizedTypeInfo(
        element_type=elem_type,
        is_container=is_container,
      )

  return None
