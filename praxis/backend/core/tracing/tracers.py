"""Tracer classes for protocol symbolic execution.

This module provides tracer objects that mimic PLR resources and machines
during symbolic execution. When a protocol is executed with tracers,
operations are recorded rather than performed, building a computation graph.

The design follows JAX-style tracing where tracer objects flow through
the protocol and record operations to an `OperationRecorder`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  from praxis.backend.core.tracing.recorder import OperationRecorder


# =============================================================================
# Base Tracer Class
# =============================================================================


@dataclass
class TracedValue(ABC):
  """Base class for all traced values.

  A TracedValue represents a symbolic value that flows through a protocol
  during tracing. Instead of holding actual data, it records operations
  performed on it to an OperationRecorder.
  """

  name: str
  """Symbolic name for this value (e.g., 'plate', 'source_wells[0]')"""

  recorder: OperationRecorder
  """The recorder that collects operations"""

  declared_type: str = "Any"
  """The declared type hint for this value"""

  @abstractmethod
  def _get_tracer_type(self) -> str:
    """Return the tracer type name for identification."""


# =============================================================================
# Resource Tracers
# =============================================================================


@dataclass
class TracedContainerElement(TracedValue):
  """Tracer for a single child element of a container resource.

  Represents an individual element from an itemized container such as:
  - Well from a Plate
  - TipSpot from a TipRack
  - Tube from a TubeRack

  This is a generic tracer that works with any container type.
  """

  element_type: str = "Well"
  """Type of element: 'Well', 'TipSpot', 'Tube', etc."""

  source_resource: str | None = None
  """Name of the parent container resource this was derived from"""

  items_x: int | None = None
  """Number of columns in the source container (for dimension inference)"""

  items_y: int | None = None
  """Number of rows in the source container (for dimension inference)"""

  index: int | None = None
  """Flat index position in the container, if known"""

  def _get_tracer_type(self) -> str:
    return "TracedContainerElement"

  def __repr__(self) -> str:
    return f"TracedContainerElement({self.name}, type={self.element_type})"


# Backwards compatibility alias
TracedWell = TracedContainerElement


@dataclass
class TracedContainerElementCollection(TracedValue):
  """Tracer for a collection of container elements.

  Represents a collection of child elements from an itemized container:
  - list[Well] from a Plate
  - Sequence[TipSpot] from a TipRack
  - tuple[Tube, ...] from a TubeRack

  Iteration yields symbolic TracedContainerElement objects representing "each element".
  This is a generic tracer that works with any container element type.
  """

  element_type: str = "Well"
  """Type of elements in the collection: 'Well', 'TipSpot', 'Tube', etc."""

  source_resource: str | None = None
  """Name of the parent container resource this was derived from"""

  items_x: int | None = None
  """Number of columns in the source container (for dimension inference)"""

  items_y: int | None = None
  """Number of rows in the source container (for dimension inference)"""

  _iteration_count: int = field(default=0, init=False)
  """Track how many times we've been iterated"""

  def _get_tracer_type(self) -> str:
    return "TracedContainerElementCollection"

  def __repr__(self) -> str:
    return f"TracedContainerElementCollection({self.name}, element_type={self.element_type})"

  def __iter__(self) -> Iterator[TracedContainerElement]:
    """Yield a symbolic element representing 'each item in collection'.

    For tracing purposes, we yield a single symbolic element that represents
    the loop variable. This is recorded as a foreach pattern.
    """
    self._iteration_count += 1
    loop_var_name = f"each_{self.name.replace('[', '_').replace(']', '_')}"

    # Record loop entry
    self.recorder.enter_loop(iterator_var=loop_var_name, source_collection=self.name)

    symbolic_element = TracedContainerElement(
      name=loop_var_name,
      recorder=self.recorder,
      declared_type=self.element_type,
      element_type=self.element_type,
      source_resource=self.source_resource or self.name,
      items_x=self.items_x,
      items_y=self.items_y,
    )

    yield symbolic_element

    # Record loop exit
    self.recorder.exit_loop()

  def __getitem__(
    self, index: int | slice
  ) -> TracedContainerElement | TracedContainerElementCollection:
    """Get an element or slice of the collection."""
    if isinstance(index, slice):
      # Return a sub-collection
      new_name = f"{self.name}[{index.start}:{index.stop}]"
      return TracedContainerElementCollection(
        name=new_name,
        recorder=self.recorder,
        declared_type=f"list[{self.element_type}]",
        element_type=self.element_type,
        source_resource=self.source_resource,
        items_x=self.items_x,
        items_y=self.items_y,
      )

    # Return single element
    new_name = f"{self.name}[{index}]"
    return TracedContainerElement(
      name=new_name,
      recorder=self.recorder,
      declared_type=self.element_type,
      element_type=self.element_type,
      source_resource=self.source_resource,
      items_x=self.items_x,
      items_y=self.items_y,
      index=index,
    )

  def __len__(self) -> int:
    """Return a symbolic length based on dimensions or default 96."""
    if self.items_x is not None and self.items_y is not None:
      return self.items_x * self.items_y
    return 96


# Backwards compatibility alias
TracedWellCollection = TracedContainerElementCollection


@dataclass
class TracedResource(TracedValue):
  """Tracer for PLR resources (Plate, TipRack, Trough, etc.).

  Represents a resource that sits on the deck. Subscript access returns
  TracedContainerElementCollection or TracedContainerElement depending on the access pattern.
  """

  resource_type: str = "Resource"
  """The PLR resource type (e.g., 'Plate', 'TipRack')"""

  parental_chain: list[str] = field(default_factory=list)
  """Parent types from this resource to deck"""

  items_x: int = 12
  """Number of columns in the resource grid (default: 96-well plate)"""

  items_y: int = 8
  """Number of rows in the resource grid (default: 96-well plate)"""

  def _get_tracer_type(self) -> str:
    return "TracedResource"

  def __repr__(self) -> str:
    return f"TracedResource({self.name}, type={self.resource_type}, {self.items_x}x{self.items_y})"

  def _infer_element_type(self) -> str:
    """Infer the child element type based on resource type."""
    if "Plate" in self.resource_type:
      return "Well"
    if "TipRack" in self.resource_type or "Tip" in self.resource_type:
      return "TipSpot"
    if "Tube" in self.resource_type:
      return "Tube"
    return "Well"  # Default

  def __getitem__(
    self, key: str | int | slice
  ) -> TracedContainerElement | TracedContainerElementCollection:
    """Access elements via subscript notation.

    Examples:
        plate["A1"] -> TracedContainerElement
        plate["A1:A8"] -> TracedContainerElementCollection
        tips[0] -> TracedContainerElement

    """
    elem_type = self._infer_element_type()

    if isinstance(key, str):
      # Well notation
      if ":" in key:
        # Range: plate["A1:A8"] -> list[Well]
        return TracedContainerElementCollection(
          name=f"{self.name}['{key}']",
          recorder=self.recorder,
          declared_type=f"list[{elem_type}]",
          element_type=elem_type,
          source_resource=self.name,
          items_x=self.items_x,
          items_y=self.items_y,
        )
      # Single: plate["A1"] -> Well
      return TracedContainerElement(
        name=f"{self.name}['{key}']",
        recorder=self.recorder,
        declared_type=elem_type,
        element_type=elem_type,
        source_resource=self.name,
        items_x=self.items_x,
        items_y=self.items_y,
      )

    if isinstance(key, int):
      return TracedContainerElement(
        name=f"{self.name}[{key}]",
        recorder=self.recorder,
        declared_type=elem_type,
        element_type=elem_type,
        source_resource=self.name,
        items_x=self.items_x,
        items_y=self.items_y,
        index=key,
      )

    # Slice
    return TracedContainerElementCollection(
      name=f"{self.name}[{key.start}:{key.stop}]",
      recorder=self.recorder,
      declared_type=f"list[{elem_type}]",
      element_type=elem_type,
      source_resource=self.name,
      items_x=self.items_x,
      items_y=self.items_y,
    )

  def wells(self) -> TracedContainerElementCollection:
    """Get all wells as a collection."""
    return TracedContainerElementCollection(
      name=f"{self.name}.wells()",
      recorder=self.recorder,
      declared_type="list[Well]",
      element_type="Well",
      source_resource=self.name,
      items_x=self.items_x,
      items_y=self.items_y,
    )

  def tips(self) -> TracedContainerElementCollection:
    """Get all tip spots as a collection."""
    return TracedContainerElementCollection(
      name=f"{self.name}.tips()",
      recorder=self.recorder,
      declared_type="list[TipSpot]",
      element_type="TipSpot",
      source_resource=self.name,
      items_x=self.items_x,
      items_y=self.items_y,
    )

  def tip_spots(self) -> TracedContainerElementCollection:
    """Alias for tips()."""
    return self.tips()


# =============================================================================
# Machine Tracers
# =============================================================================


@dataclass
class TracedMachine(TracedValue):
  """Tracer for PLR machines (LiquidHandler, PlateReader, etc.).

  Method calls on TracedMachine are intercepted and recorded to the
  OperationRecorder rather than being executed.
  """

  machine_type: str = "Machine"
  """The PLR machine type (e.g., 'liquid_handler', 'plate_reader')"""

  def _get_tracer_type(self) -> str:
    return "TracedMachine"

  def __repr__(self) -> str:
    return f"TracedMachine({self.name}, type={self.machine_type})"

  def __getattr__(self, name: str) -> Any:
    """Intercept method calls and return a recording proxy.

    Example:
        lh.aspirate(well, 100)  # Records operation instead of executing

    """
    # Skip internal attributes
    if name.startswith("_"):
      raise AttributeError(name)

    def method_proxy(*args: Any, **kwargs: Any) -> TracedMethodResult:
      """Record the method call and return a symbolic result."""
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
      op_id = self.recorder.record_operation(
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


@dataclass
class TracedMethodResult(TracedValue):
  """Result of a traced method call.

  Represents the symbolic return value of an operation.
  """

  operation_id: str = ""
  """ID of the operation that produced this result"""

  def _get_tracer_type(self) -> str:
    return "TracedMethodResult"

  def __repr__(self) -> str:
    return f"TracedMethodResult({self.name})"

  def __await__(self):
    """Make awaitable to support async protocol patterns."""

    async def _await_result():
      return self

    return _await_result().__await__()


# =============================================================================
# Comparison Tracers (for conditionals)
# =============================================================================


@dataclass
class TracedComparison(TracedValue):
  """Result of a comparison involving traced values.

  Used to track conditional branches in protocols. When used in a boolean
  context, records that a conditional was encountered.
  """

  left: str = ""
  """Left operand as string"""

  operator: str = ""
  """Comparison operator"""

  right: str = ""
  """Right operand as string"""

  def _get_tracer_type(self) -> str:
    return "TracedComparison"

  def __repr__(self) -> str:
    return f"TracedComparison({self.left} {self.operator} {self.right})"

  def __bool__(self) -> bool:
    """When used in conditional, record it and return True to execute branch."""
    condition_expr = f"{self.left} {self.operator} {self.right}"
    self.recorder.enter_conditional(condition_expr)
    return True
