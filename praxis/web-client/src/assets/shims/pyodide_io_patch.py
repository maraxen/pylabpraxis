"""Pyodide I/O Patching Module.

This module patches pylabrobot.io at runtime to use browser-compatible
WebSerial, WebUSB, and WebFTDI shims instead of pyserial, pyusb, and pylibftdi.

Usage in JupyterLite (auto-executed in bootstrap):
    import pyodide_io_patch
    pyodide_io_patch.patch_pylabrobot_io()

    # Now pylabrobot.io.Serial, USB, and FTDI use browser APIs
    from pylabrobot.io import Serial, USB
    from pylabrobot.io.ftdi import FTDI
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
  - pylabrobot.io.ftdi.FTDI -> WebFTDI (critical for CLARIOstarBackend!)
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
    from web_hid_shim import WebHID
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

  except ImportError as e:
    logger.warning(f"Could not import Serial/USB shims: {e}")
  except Exception as e:
    logger.error(f"Error patching Serial/USB: {e}")

  # Patch HID (e.g. for Inheco)
  try:
    import pylabrobot.io.hid as plr_hid
    from web_hid_shim import WebHID

    plr_hid.HID = WebHID
    plr_hid.USE_HID = True

    logger.info("✓ Patched pylabrobot.io.hid with WebHID shim")
  except ImportError as e:
    logger.warning(f"Could not import HID shim or module: {e}")
  except Exception as e:
    logger.error(f"Error patching HID: {e}")

  # CRITICAL: Patch FTDI for backends like CLARIOstarBackend
  try:
    import pylabrobot.io.ftdi as plr_ftdi
    from web_ftdi_shim import WebFTDI

    # Patch the FTDI class
    plr_ftdi.FTDI = WebFTDI

    # Also set HAS_PYLIBFTDI to True so CLARIOstarBackend doesn't error
    plr_ftdi.HAS_PYLIBFTDI = True

    logger.info("✓ Patched pylabrobot.io.ftdi with WebFTDI shim")

  except ImportError as e:
    logger.warning(f"Could not import FTDI shim: {e}")
  except Exception as e:
    logger.error(f"Error patching FTDI: {e}")

  return True


def get_io_status() -> dict:
  """Get status of I/O shim patches."""
  result = {
    "in_pyodide": is_pyodide(),
    "serial_patched": False,
    "usb_patched": False,
    "ftdi_patched": False,
    "hid_patched": False,
    "has_serial": False,
    "use_usb": False,
    "use_hid": False,
  }

  try:
    from pylabrobot.io.serial import HAS_SERIAL, Serial

    result["serial_patched"] = "WebSerial" in str(Serial)
    result["has_serial"] = HAS_SERIAL
  except Exception:
    pass

  try:
    from pylabrobot.io.usb import USB, USE_USB

    result["usb_patched"] = "WebUSB" in str(USB)
    result["use_usb"] = USE_USB
  except Exception:
    pass

  try:
    from pylabrobot.io.ftdi import FTDI

    result["ftdi_patched"] = "WebFTDI" in str(FTDI)
  except Exception:
    pass

  try:
    from pylabrobot.io.hid import HID, USE_HID

    result["hid_patched"] = "WebHID" in str(HID)
    result["use_hid"] = USE_HID
  except Exception:
    pass

  return result


# Auto-patch when this module is imported in Pyodide
if is_pyodide():
  patch_pylabrobot_io()
