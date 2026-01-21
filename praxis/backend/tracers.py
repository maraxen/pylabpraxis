# pylint: disable=too-few-public-methods
"""Tracers for protocol execution."""

from praxis.backend.utils.errors import InvalidWellSetsError


class LinkedIndicesTracer:
  """Tracer for validating linked indices."""

  def validate(self, source_wells: list, destination_wells: list) -> bool:
    """Validate that the source and destination wells are linked by index."""
    if len(source_wells) != len(destination_wells):
      msg = "Source and destination well sets have different lengths."
      raise InvalidWellSetsError(msg)

    for i, (source_well, destination_well) in enumerate(zip(source_wells, destination_wells, strict=False)):
      if source_well.index != destination_well.index:
        msg = (
          f"Source well at index {i} has index {source_well.index}, "
          f"but destination well has index {destination_well.index}."
        )
        raise InvalidWellSetsError(msg)

    return True
