import asyncio
import logging
from pylabrobot.liquid_handling.backends.hamilton import STAR
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources.hamilton import STARLetDeck

# Validate vanilla PLR execution
logging.basicConfig(level=logging.DEBUG)


async def main():
  print("--- Initializing STAR Backend ---")
  # No port specified, hoping for auto-detection or default behavior
  # Note: typically STAR needs a device node like /dev/ttyUSB0
  try:
    backend = STAR()
    print(f"Backend initialized: {backend}")

    # Must provide a deck
    deck = STARLetDeck()
    lh = LiquidHandler(backend=backend, deck=deck)
    print("LiquidHandler initialized")

    print("--- Calling setup() ---")
    await lh.setup()
    print("SETUP SUCCESSFUL")

    await lh.stop()
    print("Connection closed")

  except Exception as e:
    print(f"\n!!! SETUP FAILED !!!\nError: {e}")
    import traceback

    traceback.print_exc()


if __name__ == "__main__":
  asyncio.run(main())
