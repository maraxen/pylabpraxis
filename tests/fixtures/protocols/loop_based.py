"""Loop-based protocol - for loops over wells.

This protocol demonstrates looping over well collections, which
requires special handling in graph extraction (foreach nodes).
"""


async def multi_well_transfer(
  lh: "LiquidHandler",
  source: "Plate",
  dest: "Plate",
  tips: "TipRack",
  volume: float = 50.0,
) -> None:
  """Transfer to multiple wells in a loop.

  Args:
      lh: The liquid handler machine.
      source: Source plate.
      dest: Destination plate.
      tips: Tip rack.
      volume: Volume to transfer per well.

  """
  source_wells = source["A1:A8"]
  dest_wells = dest["A1:A8"]

  await lh.pick_up_tips(tips)

  for i, (src, dst) in enumerate(zip(source_wells, dest_wells)):
    await lh.aspirate(src, volume)
    await lh.dispense(dst, volume)

  await lh.drop_tips(tips)


# Source code for graph extraction testing
MULTI_WELL_TRANSFER_SOURCE = '''
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
