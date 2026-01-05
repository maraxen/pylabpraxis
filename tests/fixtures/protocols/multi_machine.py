"""Multi-machine protocol - multiple machine types.

This protocol demonstrates workflows involving multiple instruments
(liquid handler + plate reader), which requires tracking multiple
machine types in the graph.
"""


async def plate_reader_workflow(
  lh: "LiquidHandler",
  pr: "PlateReader",
  plate: "Plate",
  tips: "TipRack",
) -> "dict":
  """Workflow involving multiple machines.

  Args:
      lh: The liquid handler machine.
      pr: The plate reader.
      plate: Assay plate.
      tips: Tip rack.

  Returns:
      Absorbance measurement results.

  """
  # Liquid handling step
  await lh.pick_up_tips(tips)
  await lh.aspirate(plate["A1"], 100)
  await lh.dispense(plate["B1"], 100)
  await lh.drop_tips(tips)

  # Plate reading step
  result = await pr.read_absorbance(plate, wavelength=450)

  return result


# Source code for graph extraction testing
PLATE_READER_WORKFLOW_SOURCE = '''
async def plate_reader_workflow(
    lh: LiquidHandler,
    pr: PlateReader,
    plate: Plate,
    tips: TipRack,
):
    """Workflow involving multiple machines."""
    await lh.pick_up_tips(tips)
    await lh.aspirate(plate["A1"], 100)
    await lh.dispense(plate["B1"], 100)
    await lh.drop_tips(tips)

    result = await pr.read_absorbance(plate, wavelength=450)
    return result
'''
