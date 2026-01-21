import logging
from typing import TYPE_CHECKING

from pylabrobot.resources import Well

if TYPE_CHECKING:
  from praxis.backend.core.run_context import PraxisRunContext

logger = logging.getLogger(__name__)


class LiquidHandlerSimulator:
  """A simulated liquid handler that tracks liquid volumes."""

  def __init__(self, name: str, run_context: "PraxisRunContext"):
    self.name = name
    self.run_context = run_context

  async def aspirate(self, well: Well, volume: float):
    """Simulates aspirating liquid from a well.

    Args:
        well: The well to aspirate from.
        volume: Volume in microliters.

    """
    well_state = self.run_context.get_simulation_state(well.name)
    current_volume = well_state.get("volume", 0.0)

    if current_volume < volume:
      msg = (
        f"Not enough liquid in {well.name} to aspirate {volume}uL (current: {current_volume}uL)."
      )
      raise RuntimeError(msg)

    well_state["volume"] = current_volume - volume
    self.run_context.update_simulation_state(well.name, well_state)
    logger.info(
      "Aspirated %suL from %s. New volume: %suL.", volume, well.name, well_state["volume"]
    )

  async def dispense(self, well: Well, volume: float):
    """Simulates dispensing liquid into a well.

    Args:
        well: The well to dispense into.
        volume: Volume in microliters.

    """
    well_state = self.run_context.get_simulation_state(well.name)
    current_volume = well_state.get("volume", 0.0)

    well_state["volume"] = current_volume + volume
    self.run_context.update_simulation_state(well.name, well_state)
    logger.info("Dispensed %suL to %s. New volume: %suL.", volume, well.name, well_state["volume"])

  async def setup(self):
    """Simulates hardware setup."""
    logger.info("Simulator '%s' is ready.", self.name)

  async def stop(self):
    """Simulates hardware shutdown."""
    logger.info("Simulator '%s' is stopped.", self.name)
