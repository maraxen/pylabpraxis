"""Selective Transfer Protocol.

A protocol that demonstrates complex well selection UI scenarios.
This shows how to use well selector parameters to enable grid-based
well selection in the protocol configuration UI.
"""

from typing import Any

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources import Plate, TipRack

from praxis.backend.core.decorators import protocol_function


@protocol_function(
  name="selective_transfer",
  version="1.0.0",
  description="Transfer liquid between selected wells with rich well selection UI",
  category="liquid_handling",
  tags=["demo", "transfer", "well-selection", "advanced"],
  is_top_level=True,
  param_metadata={
    "liquid_handler": {
      "description": "The liquid handling robot to use",
      "plr_type": "LiquidHandler",
    },
    "source_plate": {
      "description": "Source plate containing samples",
      "plr_type": "Plate",
    },
    "dest_plate": {
      "description": "Destination plate for transfers",
      "plr_type": "Plate",
    },
    "tip_rack": {
      "description": "Tip rack for liquid handling",
      "plr_type": "TipRack",
    },
    "source_wells": {
      "description": "Source wells to aspirate from (use grid selector)",
      "ui_hint": "well_selector",
      "plate_ref": "source_plate",  # Links to source plate for UI
    },
    "dest_wells": {
      "description": "Destination wells to dispense to (use grid selector)",
      "ui_hint": "well_selector",
      "plate_ref": "dest_plate",  # Links to destination plate for UI
    },
    "transfer_volume_ul": {
      "description": "Volume to transfer per well in microliters",
      "min": 1.0,
      "max": 1000.0,
    },
    "transfer_pattern": {
      "description": "How to map source to destination wells",
      "ui_hint": "select",
      "options": ["1:1", "replicate", "pool"],
    },
    "replicate_count": {
      "description": "Number of replicates per source (for 'replicate' pattern)",
      "min": 1,
      "max": 8,
    },
  },
)
async def selective_transfer(
  state: dict[str, Any],
  liquid_handler: LiquidHandler,
  source_plate: Plate,
  dest_plate: Plate,
  tip_rack: TipRack,
  source_wells: str = "A1:A4",
  dest_wells: str = "B1:B4",
  transfer_volume_ul: float = 50.0,
  transfer_pattern: str = "1:1",
  replicate_count: int = 3,
) -> dict[str, Any]:
  """Transfer liquid between selected wells with various patterns.

  This protocol demonstrates rich well selection scenarios:

  **1:1 Pattern**: Each source well maps to exactly one destination well.
  Source and destination must have the same number of wells.

  **Replicate Pattern**: Each source well is distributed to N destination wells.
  Useful for creating technical replicates.

  **Pool Pattern**: All source wells are pooled into each destination well.
  Useful for combining samples or creating pools.

  Args:
      state: Protocol state dictionary
      liquid_handler: Liquid handler for transfers
      source_plate: Source plate with samples
      dest_plate: Destination plate
      tip_rack: Tips for transfer
      source_wells: Well selection for sources
      dest_wells: Well selection for destinations
      transfer_volume_ul: Volume per transfer
      transfer_pattern: Mapping pattern (1:1, replicate, pool)
      replicate_count: Replicates per source for 'replicate' pattern

  Returns:
      Updated state with transfer records

  """
  # Parse well selections
  src_wells = _parse_wells(source_wells)
  dst_wells = _parse_wells(dest_wells)

  # Validate based on pattern
  transfers = []

  if transfer_pattern == "1:1":
    if len(src_wells) != len(dst_wells):
      msg = (
        f"1:1 pattern requires equal well counts: "
        f"{len(src_wells)} sources vs {len(dst_wells)} destinations"
      )
      raise ValueError(msg)

    for src, dst in zip(src_wells, dst_wells, strict=True):
      transfers.append(
        {
          "source_plate": source_plate.name,
          "source_well": src,
          "dest_plate": dest_plate.name,
          "dest_well": dst,
          "volume_ul": transfer_volume_ul,
          "pattern": "1:1",
        }
      )

  elif transfer_pattern == "replicate":
    expected_dst = len(src_wells) * replicate_count
    if len(dst_wells) < expected_dst:
      msg = (
        f"Replicate pattern with {len(src_wells)} sources x "
        f"{replicate_count} replicates requires {expected_dst} destinations, "
        f"but only {len(dst_wells)} provided"
      )
      raise ValueError(msg)

    dst_idx = 0
    for src in src_wells:
      for rep in range(replicate_count):
        transfers.append(
          {
            "source_plate": source_plate.name,
            "source_well": src,
            "dest_plate": dest_plate.name,
            "dest_well": dst_wells[dst_idx],
            "volume_ul": transfer_volume_ul,
            "pattern": "replicate",
            "replicate_number": rep + 1,
          }
        )
        dst_idx += 1

  elif transfer_pattern == "pool":
    # Pool all sources into each destination
    for dst in dst_wells:
      for src in src_wells:
        transfers.append(
          {
            "source_plate": source_plate.name,
            "source_well": src,
            "dest_plate": dest_plate.name,
            "dest_well": dst,
            "volume_ul": transfer_volume_ul,
            "pattern": "pool",
          }
        )

  else:
    msg = f"Unknown transfer pattern: {transfer_pattern}"
    raise ValueError(msg)

  # Record results
  state["transfers"] = transfers
  state["transfer_count"] = len(transfers)
  state["total_volume_ul"] = transfer_volume_ul * len(transfers)
  state["source_wells"] = src_wells
  state["dest_wells"] = dst_wells
  state["pattern"] = transfer_pattern
  state["status"] = "completed"

  return state


def _parse_wells(selection: str) -> list[str]:
  """Parse a well selection string into a list of well positions.

  Supports formats:
  - Range: 'A1:A4' or 'A1:H1' (row/column ranges)
  - Rectangle: 'A1:B4' (rectangular selection)
  - List: 'A1,B2,C3' (specific wells)
  """
  wells = []

  if ":" in selection and "," not in selection:
    # Range or rectangle selection
    start, end = selection.split(":")
    start_row, start_col = start[0].upper(), int(start[1:])
    end_row, end_col = end[0].upper(), int(end[1:])

    for row_ord in range(ord(start_row), ord(end_row) + 1):
      for col in range(start_col, end_col + 1):
        wells.append(f"{chr(row_ord)}{col}")
  elif "," in selection:
    # List of specific wells
    wells = [w.strip().upper() for w in selection.split(",")]
  else:
    # Single well
    wells = [selection.strip().upper()]

  return wells
