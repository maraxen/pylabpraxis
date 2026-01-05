"""Conditional protocol - if/else based on parameter.

This protocol demonstrates conditional execution paths, which
requires handling both branches in graph extraction.
"""


async def conditional_volume(
  lh: "LiquidHandler",
  plate: "Plate",
  tips: "TipRack",
  volume: float,
  threshold: float = 50.0,
) -> None:
  """Conditional aspiration based on volume.

  Args:
      lh: The liquid handler machine.
      plate: Source/destination plate.
      tips: Tip rack.
      volume: Requested volume.
      threshold: Volume threshold for conditional.

  """
  await lh.pick_up_tips(tips)

  if volume > threshold:
    await lh.aspirate(plate["A1"], volume)
  else:
    await lh.aspirate(plate["A1"], volume / 2)

  await lh.drop_tips(tips)


# Source code for graph extraction testing
CONDITIONAL_VOLUME_SOURCE = '''
async def conditional_volume(
    lh: LiquidHandler,
    plate: Plate,
    tips: TipRack,
    volume: float,
    threshold: float = 50.0,
):
    """Conditional aspiration based on volume."""
    await lh.pick_up_tips(tips)

    if volume > threshold:
        await lh.aspirate(plate["A1"], volume)
    else:
        await lh.aspirate(plate["A1"], volume / 2)

    await lh.drop_tips(tips)
'''
