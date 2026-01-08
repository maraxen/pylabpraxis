import logging
import serial.tools.list_ports
from pylabrobot.liquid_handling.backends.hamilton import STAR
from pylabrobot.liquid_handling import LiquidHandler

# Set up logging to see PLR debug output
logging.basicConfig(level=logging.DEBUG)

print("--- Listing Serial Ports ---")
ports = serial.tools.list_ports.comports()
for port in ports:
  print(f"Device: {port.device}")
  print(f"  Name: {port.name}")
  print(f"  Desc: {port.description}")
  print(f"  HWID: {port.hwid}")
  print(f"  VID: {port.vid}, PID: {port.pid}")
  print("-" * 20)

print("\n--- Attempting PLR Connection ---")
# Try to find a plausible port
potential_ports = [p.device for p in ports if "Bluetooth" not in p.device]

if not potential_ports:
  print("No non-Bluetooth ports found.")
else:
  print(f"Potential ports to try: {potential_ports}")
  # We can try to connect to the first plausible port or let STAR auto-detect if implemented
  # For now, let's just try to setup a STAR on the first candidate if user wants,
  # but primarily just listing ports is the first step.

  # Uncomment to try actual connection if you identify the port
  # backend = STAR(device=potential_ports[0])
  # lh = LiquidHandler(backend=backend)
  # await lh.setup()
  # await lh.stop()
