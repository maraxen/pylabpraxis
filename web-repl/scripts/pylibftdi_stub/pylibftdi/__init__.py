"""Stub for pylibftdi — provides symbols without native FTDI hardware.

This package satisfies `import pylibftdi`, `import pylibftdi.driver`, and
`from pylibftdi import Device, FtdiError` in environments where the real
C-extension-based pylibftdi cannot be installed (Pyodide/WASM, CI without
libftdi, headless test runners) — the exact import pylabrobot/io/ftdi.py
performs at its own top:

    try:
      import pylibftdi.driver
      from pylibftdi import Device, FtdiError
      HAS_PYLIBFTDI = True
    except ImportError as e:
      HAS_PYLIBFTDI = False

Exported symbols match the subset actually used by pylabrobot (verified via
`git -C external/pylabrobot grep -n pylibftdi HEAD`):
  - FtdiError           (pylabrobot/io/ftdi.py, biotek_synergyh1_backend.py)
  - LibraryMissingError (pylabrobot/io/ftdi.py)
  - Device              (pylabrobot/io/ftdi.py)
  - driver              (pylabrobot/io/ftdi.py reads driver.USB_VID_LIST /
                          USB_PID_LIST — a submodule import, not an attribute;
                          see pylibftdi/driver.py. Nothing in pylabrobot
                          mutates these lists.)

These are stubs, not a working FTDI driver: `Device` raises at any real I/O
attempt. Real FTDI hardware access in the browser goes through the WebFTDI
shim, never through this package.
"""

from . import driver


class FtdiError(Exception):
  """Drop-in replacement for pylibftdi.FtdiError."""


class LibraryMissingError(Exception):
  """Drop-in replacement for pylibftdi.LibraryMissingError."""


class Device:
  """Phantom Device — will never be instantiated in stub context.

  Accepts the same kwargs as the real Device so that `Device(lazy_open=True, ...)`
  does not crash at construction, but any attempt to *use* the device raises.
  """

  def __init__(self, **kwargs):
    self._kwargs = kwargs
    self.closed = True

  def open(self):
    raise RuntimeError(
      "pylibftdi Device.open() called, but only the stub package is installed. "
      "Install the real pylibftdi to use FTDI hardware."
    )

  def close(self):
    pass

  def read(self, num_bytes=1):
    raise RuntimeError("pylibftdi stub: cannot read without real hardware")

  def write(self, data):
    raise RuntimeError("pylibftdi stub: cannot write without real hardware")

  def readline(self):
    raise RuntimeError("pylibftdi stub: cannot readline without real hardware")


__version__ = "0.0.0+stub"
