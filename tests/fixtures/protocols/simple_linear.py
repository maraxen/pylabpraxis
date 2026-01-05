"""Simple linear protocol - no loops, no conditionals.

This protocol demonstrates a basic A→B transfer workflow with explicit
tip management. Used for testing basic graph extraction.
"""

# NOTE: These are mock type annotations for static analysis testing.
# Actual PLR types would be imported in production code.


async def simple_transfer(
  lh: "LiquidHandler",
  source: "Plate",
  dest: "Plate",
  tips: "TipRack",
) -> None:
  """Simple A→B transfer.

  Args:
      lh: The liquid handler machine.
      source: Source plate containing liquid.
      dest: Destination plate for transfer.
      tips: Tip rack with disposable tips.

  """
  await lh.pick_up_tips(tips)
  await lh.aspirate(source["A1"], 100)
  await lh.dispense(dest["A1"], 100)
  await lh.drop_tips(tips)


# Source code for graph extraction testing
SIMPLE_TRANSFER_SOURCE = '''
async def simple_transfer(
    lh: LiquidHandler,
    source: Plate,
    dest: Plate,
    tips: TipRack,
):
    """Simple A→B transfer."""
    await lh.pick_up_tips(tips)
    await lh.aspirate(source["A1"], 100)
    await lh.dispense(dest["A1"], 100)
    await lh.drop_tips(tips)
'''
