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
import types
from typing import Any

logger = logging.getLogger(__name__)


def is_pyodide() -> bool:
  """Check if running in Pyodide environment."""
  return "pyodide" in sys.modules or hasattr(sys, "pyodide_py")


def patch_pylabrobot_io():
  """Patch pylabrobot.io to use browser-compatible shims.

  This replaces:
  - pylabrobot.io.Serial -> WebSerial
  - pylabrobot.io.USB -> WebUSB
  - pylabrobot.io.ftdi.FTDI -> WebFTDI

  AND injects global module shims for direct imports:
  - import serial -> SerialShimModule
  - import usb.core -> USBShimModule
  - import hid -> HIDShimModule
  """
  if not is_pyodide():
    logger.info("Not in Pyodide environment, skipping I/O patch")
    return False

  try:
    # 1. Import browser shims
    from web_serial_shim import WebSerial
    from web_usb_shim import WebUSB
    from web_hid_shim import WebHID

    # 2. Patch Pylabrobot IO Classes (Existing Logic)
    import pylabrobot.io as plr_io
    import pylabrobot.io.serial as plr_serial
    import pylabrobot.io.usb as plr_usb

    plr_io.Serial = WebSerial
    plr_serial.Serial = WebSerial

    plr_io.USB = WebUSB
    plr_usb.USB = WebUSB

    plr_serial.HAS_SERIAL = True
    plr_usb.USE_USB = True

    logger.info("✓ Patched pylabrobot.io with WebSerial/WebUSB")

    try:
      import pylabrobot.io.ftdi as plr_ftdi
      from web_ftdi_shim import WebFTDI

      plr_ftdi.FTDI = WebFTDI
      plr_ftdi.HAS_PYLIBFTDI = True
      logger.info("✓ Patched pylabrobot.io.ftdi with WebFTDI")
    except ImportError:
      logger.warning("Could not patch FTDI (module not found)")

    try:
      import pylabrobot.io.hid as plr_hid

      plr_hid.HID = WebHID
      plr_hid.USE_HID = True
      logger.info("✓ Patched pylabrobot.io.hid with WebHID")
    except ImportError:
      logger.warning("Could not patch HID (module not found)")

    # 3. Inject Global Module Shims (New Logic)
    _inject_serial_shim(WebSerial)
    _inject_usb_shim(WebUSB)
    _inject_hid_shim()

    logger.info("✓ Injected global module shims (serial, usb, hid)")

  except Exception as e:
    logger.error(f"Error patching I/O: {e}")
    # Don't re-raise, allow app to continue even if shim fails (partial functionality)
    return False

  return True


def _inject_serial_shim(WebSerialClass):
  """Inject a fake 'serial' module into sys.modules."""

  # Define the Shim Module
  class SerialShimModule(types.ModuleType):
    def __init__(self):
      super().__init__("serial")
      self.Serial = WebSerialClass
      self.SerialException = Exception  # Simple alias

      # Constants required by backends
      self.EIGHTBITS = 8
      self.SEVENBITS = 7
      self.FIVEBITS = 5
      self.SIXBITS = 6

      self.PARITY_NONE = "N"
      self.PARITY_EVEN = "E"
      self.PARITY_ODD = "O"
      self.PARITY_MARK = "M"
      self.PARITY_SPACE = "S"

      self.STOPBITS_ONE = 1
      self.STOPBITS_TWO = 2
      self.STOPBITS_ONE_POINT_FIVE = 1.5

    def __getattr__(self, name):
      # Fallback for other attributes
      if name in self.__dict__:
        return self.__dict__[name]
      raise AttributeError(f"module 'serial' has no attribute '{name}'")

  # Inject 'serial'
  if "serial" not in sys.modules:
    sys.modules["serial"] = SerialShimModule()

  # Inject 'serial.tools'
  serial_tools = types.ModuleType("serial.tools")
  sys.modules["serial.tools"] = serial_tools

  # Inject 'serial.tools.list_ports'
  class ListPortsModule(types.ModuleType):
    def __init__(self):
      super().__init__("serial.tools.list_ports")

    def comports(self, include_links=False):
      # Return empty list to force manual port selection or prevent auto-scan errors
      return []

  sys.modules["serial.tools.list_ports"] = ListPortsModule()

  # Link them up so import serial.tools.list_ports works
  serial_tools.list_ports = sys.modules["serial.tools.list_ports"]
  sys.modules["serial"].tools = serial_tools


def _inject_usb_shim(WebUSBClass):
  """Inject a fake 'usb' and 'usb.core' module."""

  # Only inject if not already present
  if "usb" not in sys.modules:
    sys.modules["usb"] = types.ModuleType("usb")

  class USBCoreShim(types.ModuleType):
    def __init__(self):
      super().__init__("usb.core")

    def find(self, *args, **kwargs):
      # Return a placeholder or None.
      # Real usage requires instantiating WebUSB directly in our shims,
      # but this prevents ImportErrors.
      return None

    class Device:
      """Phantom Device class."""

      pass

  sys.modules["usb.core"] = USBCoreShim()
  sys.modules["usb"].core = sys.modules["usb.core"]


def _inject_hid_shim():
  """Inject a fake 'hid' module."""

  class HIDShimModule(types.ModuleType):
    def __init__(self):
      super().__init__("hid")

    def device(self):
      """Return a dummy device or raise NotImplementedError currently."""
      # Future: Return WebHID shim
      return None

    def enumerate(self, vid=0, pid=0):
      return []

  if "hid" not in sys.modules:
    sys.modules["hid"] = HIDShimModule()


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
    "global_serial_shim": False,
    "global_usb_shim": False,
  }

  try:
    from pylabrobot.io.serial import HAS_SERIAL, Serial

    result["serial_patched"] = "WebSerial" in str(Serial)
    result["has_serial"] = HAS_SERIAL

    # Check global shim
    import serial

    result["global_serial_shim"] = "WebSerial" in str(serial.Serial)
  except Exception:
    pass

  try:
    from pylabrobot.io.usb import USB, USE_USB

    result["usb_patched"] = "WebUSB" in str(USB)
    result["use_usb"] = USE_USB

    # Check global shim
    import usb.core

    result["global_usb_shim"] = "usb.core" in sys.modules
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
