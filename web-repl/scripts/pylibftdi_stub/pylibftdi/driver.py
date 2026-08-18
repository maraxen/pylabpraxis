"""Stub for pylibftdi.driver — the USB VID/PID identification table.

pylabrobot/io/ftdi.py (external/pylabrobot HEAD) does:

    import pylibftdi.driver
    ...
    if device.idVendor not in pylibftdi.driver.USB_VID_LIST: ...
    if device.idProduct not in pylibftdi.driver.USB_PID_LIST: ...

That is a genuine SUBMODULE import (`import pylibftdi.driver`), not just
attribute access on the `pylibftdi` package — so this file must exist as
`pylibftdi/driver.py` for the import itself to succeed. PLR only *reads*
these two lists to classify enumerated USB devices as FTDI-family hardware;
nothing in pylabrobot mutates them (verified via
`git -C external/pylabrobot grep -n pylibftdi HEAD` — the only lists usage is
these two read-only membership checks in pylabrobot/io/ftdi.py).

This module exists purely to satisfy that import in environments where the
real C-extension-backed pylibftdi cannot be installed (Pyodide/WASM, CI
without libftdi, headless test runners). Real FTDI hardware access in the
browser goes through the WebFTDI shim, not through this stub.
"""

USB_VID_LIST: list[int] = [0x0403]
USB_PID_LIST: list[int] = [0x6001, 0x6010, 0x6011, 0x6014, 0x6015]
