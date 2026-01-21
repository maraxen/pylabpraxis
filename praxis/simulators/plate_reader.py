import logging

import numpy as np
from pylabrobot.resources import Plate

logger = logging.getLogger(__name__)


class PlateReaderSimulator:
  """A simulated plate reader that generates data based on protocol metadata."""

  def __init__(self, name: str):
    self.name = name
    self._rng = np.random.default_rng()

  async def read_luminescence(self, plate: Plate, **kwargs) -> list[list[float]]:
    """Simulates reading luminescence.

    Args:
        plate: The plate to read.
        **kwargs: May include __praxis_simulation_meta__ with 'shape' and 'range'.

    """
    sim_meta = kwargs.get("__praxis_simulation_meta__", {})

    # Default to 96-well plate shape if not specified
    shape = sim_meta.get("shape", (8, 12))
    data_range = sim_meta.get("range", (1000.0, 5000.0))

    data = self._rng.uniform(low=data_range[0], high=data_range[1], size=shape)
    return data.tolist()

  async def setup(self):
    """Simulates hardware setup."""
    logger.info("Simulator '%s' is ready.", self.name)

  async def stop(self):
    """Simulates hardware shutdown."""
    logger.info("Simulator '%s' is stopped.", self.name)
