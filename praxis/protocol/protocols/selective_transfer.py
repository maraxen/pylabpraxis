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
      "description": "Source well positions (e.g. A1, B2)",
      "ui_hint": "well_selector",
      "plate_ref": "source_plate",
    },
    "dest_wells": {
      "description": "Destination well positions (e.g. A1, B2)",
      "ui_hint": "well_selector",
      "plate_ref": "dest_plate",
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
  src_well_names = _parse_wells(source_wells)
  dst_well_names = _parse_wells(dest_wells)

  transfers = []

  # Calculate operations based on pattern
  if transfer_pattern == "1:1":
    if len(src_well_names) != len(dst_well_names):
      msg = (
        f"1:1 pattern requires equal well counts: "
        f"{len(src_well_names)} sources vs {len(dst_well_names)} destinations"
      )
      raise ValueError(msg)

    # Use single index for 1:1 mapping (Technical Debt: Simplify indexing)
    for i in range(len(src_well_names)):
      src = src_well_names[i]
      dst = dst_well_names[i]
      
      # Perform transfer
      await _perform_transfer(
        liquid_handler, 
        source_plate, 
        src, 
        dest_plate, 
        dst, 
        transfer_volume_ul, 
        tip_rack, 
        i
      )

      transfers.append({
        "source_plate": source_plate.name,
        "source_well": src,
        "dest_plate": dest_plate.name,
        "dest_well": dst,
        "volume_ul": transfer_volume_ul,
        "pattern": "1:1",
      })

  elif transfer_pattern == "replicate":
    expected_dst = len(src_well_names) * replicate_count
    if len(dst_well_names) < expected_dst:
      msg = (
        f"Replicate pattern with {len(src_well_names)} sources x "
        f"{replicate_count} replicates requires {expected_dst} destinations, "
        f"but only {len(dst_well_names)} provided"
      )
      raise ValueError(msg)

    dst_idx = 0
    for src in src_well_names:
      for rep in range(replicate_count):
        dst = dst_well_names[dst_idx]
        
        await _perform_transfer(
          liquid_handler, 
          source_plate, 
          src, 
          dest_plate, 
          dst, 
          transfer_volume_ul, 
          tip_rack, 
          dst_idx
        )

        transfers.append({
          "source_plate": source_plate.name,
          "source_well": src,
          "dest_plate": dest_plate.name,
          "dest_well": dst,
          "volume_ul": transfer_volume_ul,
          "pattern": "replicate",
          "replicate_number": rep + 1,
        })
        dst_idx += 1

  elif transfer_pattern == "pool":
    # Pool all sources into each destination
    op_idx = 0
    for dst in dst_well_names:
      for src in src_well_names:
        await _perform_transfer(
          liquid_handler, 
          source_plate, 
          src, 
          dest_plate, 
          dst, 
          transfer_volume_ul, 
          tip_rack, 
          op_idx
        )
        
        transfers.append({
          "source_plate": source_plate.name,
          "source_well": src,
          "dest_plate": dest_plate.name,
          "dest_well": dst,
          "volume_ul": transfer_volume_ul,
          "pattern": "pool",
        })
        op_idx += 1

  else:
    msg = f"Unknown transfer pattern: {transfer_pattern}"
    raise ValueError(msg)

  # Update state
  state["transfers"] = transfers
  state["transfer_count"] = len(transfers)
  state["total_volume_ul"] = transfer_volume_ul * len(transfers)
  state["status"] = "completed"

  return state


async def _perform_transfer(
  lh: LiquidHandler, 
  src_plate: Plate, 
  src_well: str, 
  dst_plate: Plate, 
  dst_well: str, 
  vol: float, 
  tip_rack: TipRack,
  tip_idx: int
) -> None:
  """Execute a single transfer operation with tip handling."""
  # Simple tip tracking: Wrap around tip rack if needed
  # Note: In a real protocol, we'd use a TipTracker or similar
  num_tips = 96 # Assumed standard 96 tip rack for simplicity
  tip_spot = tip_rack.get_item(tip_idx % num_tips)
  
  if tip_spot: # Should always be true for standard rack
      await lh.pick_up_tips(tip_spot)
      await lh.aspirate(src_plate[src_well], vols=[vol])
      await lh.dispense(dst_plate[dst_well], vols=[vol])
      await lh.return_tips() # Return to save simulation tips/avoid trash config issues


def _parse_wells(selection: str) -> list[str]:
  """Parse a well selection string into a list of well positions."""
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
