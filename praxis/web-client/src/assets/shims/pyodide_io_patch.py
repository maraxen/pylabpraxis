"""Pyodide I/O Patching Module

This module patches pylabrobot.io at runtime to use browser-compatible
WebSerial and WebUSB shims instead of pyserial and pyusb.

Usage in JupyterLite (auto-executed in bootstrap):
    import pyodide_io_patch
    pyodide_io_patch.patch_pylabrobot_io()

    # Now pylabrobot.io.Serial and USB use browser APIs
    from pylabrobot.io import Serial, USB
"""

import logging
import sys

logger = logging.getLogger(__name__)


def is_pyodide() -> bool:
  """Check if running in Pyodide environment."""
  return "pyodide" in sys.modules or hasattr(sys, "pyodide_py")


def patch_pylabrobot_io():
  """Patch pylabrobot.io to use browser-compatible shims.

  This replaces:
  - pylabrobot.io.Serial -> WebSerial
  - pylabrobot.io.USB -> WebUSB
  """
  if not is_pyodide():
    logger.info("Not in Pyodide environment, skipping I/O patch")
    return False

  try:
    # Import shims (these should be in micropip's path or loaded as assets)
    # Import pylabrobot.io module
    import pylabrobot.io as plr_io
    import pylabrobot.io.serial as plr_serial
    import pylabrobot.io.usb as plr_usb
    from web_serial_shim import WebSerial
    from web_usb_shim import WebUSB

    # Patch the Serial class
    plr_io.Serial = WebSerial
    plr_serial.Serial = WebSerial

    # Patch the USB class
    plr_io.USB = WebUSB
    plr_usb.USB = WebUSB

    # Update HAS_SERIAL and USE_USB flags
    plr_serial.HAS_SERIAL = True
    plr_usb.USE_USB = True

    logger.info("✓ Patched pylabrobot.io with WebSerial/WebUSB shims")
    return True

  except ImportError as e:
    logger.warning(f"Could not import shims, I/O patching skipped: {e}")
    return False
  except Exception as e:
    logger.error(f"Error patching pylabrobot.io: {e}")
    return False


def get_io_status() -> dict:
  """Get status of I/O shim patches."""
  try:
    from pylabrobot.io.serial import HAS_SERIAL, Serial
    from pylabrobot.io.usb import USB, USE_USB

    return {
      "in_pyodide": is_pyodide(),
      "serial_patched": "WebSerial" in str(Serial),
      "usb_patched": "WebUSB" in str(USB),
      "has_serial": HAS_SERIAL,
      "use_usb": USE_USB,
    }
  except Exception as e:
    return {"error": str(e)}


# Auto-patch when this module is imported in Pyodide
if is_pyodide():
  patch_pylabrobot_io()
