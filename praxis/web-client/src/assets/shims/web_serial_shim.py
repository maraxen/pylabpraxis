"""WebSerial Shim for Pyodide/Browser Environment

This module provides a WebSerial-based implementation of pylabrobot's Serial interface,
enabling hardware communication from the browser using the WebSerial API.

Usage in JupyterLite:
    from web_serial_shim import WebSerial

    # Request a serial port (user must approve in browser dialog)
    serial = WebSerial(baudrate=9600)
    await serial.setup()

    # Use like regular Serial
    await serial.write(b"command")
    response = await serial.read(100)
"""

import asyncio
import logging
from typing import Any

# Import Pyodide's JavaScript bridge
try:
  from js import Object, Uint8Array, navigator
  from pyodide.ffi import create_proxy, to_js

  IN_PYODIDE = True
except ImportError:
  IN_PYODIDE = False
  navigator = None

logger = logging.getLogger(__name__)


class WebSerial:
  """WebSerial-based Serial implementation for browser environments.

  Implements the same interface as pylabrobot.io.Serial but uses
  the browser's WebSerial API via Pyodide's JS bridge.
  """

  def __init__(
    self,
    port: Any | None = None,  # SerialPort object from requestPort
    vid: int | None = None,
    pid: int | None = None,
    baudrate: int = 9600,
    bytesize: int = 8,
    parity: str = "N",
    stopbits: int = 1,
    write_timeout: float = 1,
    timeout: float = 1,
    rtscts: bool = False,
    dsrdtr: bool = False,
  ):
    """Initialize WebSerial.

    Args:
        port: Optional SerialPort object. If None, will request in setup().
        vid: USB Vendor ID for filtering (optional)
        pid: USB Product ID for filtering (optional)
        baudrate: Baud rate (default 9600)
        bytesize: Data bits (5-8, default 8)
        parity: Parity ('N', 'E', 'O', default 'N')
        stopbits: Stop bits (1 or 2, default 1)
        write_timeout: Write timeout in seconds
        timeout: Read timeout in seconds
        rtscts: Enable RTS/CTS flow control
        dsrdtr: Enable DSR/DTR flow control

    """
    if not IN_PYODIDE:
      raise RuntimeError("WebSerial is only available in Pyodide/browser environment")

    self._port = port
    self._vid = vid
    self._pid = pid
    self.baudrate = baudrate
    self.bytesize = bytesize
    self.parity = parity
    self.stopbits = stopbits
    self.write_timeout = write_timeout
    self.timeout = timeout
    self.rtscts = rtscts
    self.dsrdtr = dsrdtr

    self._reader: Any | None = None
    self._writer: Any | None = None
    self._port_name: str = "WebSerial"

  @property
  def port(self) -> str:
    """Return port identifier."""
    return self._port_name

  async def setup(self):
    """Initialize the WebSerial connection.

    This will trigger a browser dialog for the user to select a serial port
    if no port was provided in the constructor.
    """
    if not hasattr(navigator, "serial"):
      raise RuntimeError(
        "WebSerial is not supported in this browser. Please use Chrome, Edge, or Opera."
      )

    # Request port if not provided
    if self._port is None:
      filters = []
      if self._vid is not None and self._pid is not None:
        filters.append({"usbVendorId": self._vid, "usbProductId": self._pid})

      options = {"filters": filters} if filters else {}

      try:
        self._port = await navigator.serial.requestPort(to_js(options))
      except Exception as e:
        raise RuntimeError(f"Failed to request serial port: {e}")

    # Map parity
    parity_map = {"N": "none", "E": "even", "O": "odd"}
    parity = parity_map.get(self.parity, "none")

    # Map stop bits
    stopbits_map = {1: 1, 2: 2}
    stopbits = stopbits_map.get(self.stopbits, 1)

    # Open the port
    options = {
      "baudRate": self.baudrate,
      "dataBits": self.bytesize,
      "parity": parity,
      "stopBits": stopbits,
      "flowControl": "hardware" if self.rtscts else "none",
    }

    try:
      await self._port.open(to_js(options))
    except Exception as e:
      raise RuntimeError(f"Failed to open serial port: {e}")

    # Get readable and writable streams
    self._reader = self._port.readable.getReader()
    self._writer = self._port.writable.getWriter()

    # Try to get port info for logging
    try:
      info = self._port.getInfo()
      self._port_name = f"WebSerial[{info.usbVendorId}:{info.usbProductId}]"
    except:
      self._port_name = "WebSerial"

    logger.info(f"WebSerial port opened: {self._port_name}")

  async def stop(self):
    """Close the serial port."""
    try:
      if self._reader:
        await self._reader.cancel()
        self._reader.releaseLock()
        self._reader = None

      if self._writer:
        await self._writer.close()
        self._writer = None

      if self._port:
        await self._port.close()
        self._port = None

      logger.info("WebSerial port closed")
    except Exception as e:
      logger.warning(f"Error closing WebSerial port: {e}")

  async def write(self, data: bytes):
    """Write data to the serial port."""
    if self._writer is None:
      raise RuntimeError("Port not open. Call setup() first.")

    # Convert bytes to Uint8Array
    js_data = Uint8Array.new(list(data))

    try:
      await self._writer.write(js_data)
      logger.debug(f"[{self._port_name}] write: {data}")
    except Exception as e:
      raise RuntimeError(f"Write failed: {e}")

  async def read(self, num_bytes: int = 1) -> bytes:
    """Read data from the serial port."""
    if self._reader is None:
      raise RuntimeError("Port not open. Call setup() first.")

    result = bytearray()

    try:
      # Read with timeout
      read_task = asyncio.create_task(self._read_chunk())
      try:
        chunk = await asyncio.wait_for(read_task, timeout=self.timeout)
        if chunk:
          result.extend(chunk[:num_bytes])
      except asyncio.TimeoutError:
        logger.debug(f"[{self._port_name}] read timeout")
    except Exception as e:
      raise RuntimeError(f"Read failed: {e}")

    if result:
      logger.debug(f"[{self._port_name}] read: {bytes(result)}")

    return bytes(result)

  async def _read_chunk(self) -> bytes:
    """Read a chunk of data from the reader."""
    result = await self._reader.read()
    if result.done:
      return b""
    # Convert Uint8Array to bytes
    return bytes(result.value.to_py())

  async def readline(self) -> bytes:
    """Read a line (until newline) from the serial port."""
    if self._reader is None:
      raise RuntimeError("Port not open. Call setup() first.")

    result = bytearray()

    try:
      while True:
        read_task = asyncio.create_task(self._read_chunk())
        try:
          chunk = await asyncio.wait_for(read_task, timeout=self.timeout)
          if not chunk:
            break
          result.extend(chunk)
          if b"\n" in chunk:
            break
        except asyncio.TimeoutError:
          break
    except Exception as e:
      raise RuntimeError(f"Readline failed: {e}")

    if result:
      logger.debug(f"[{self._port_name}] readline: {bytes(result)}")

    return bytes(result)

  async def reset_input_buffer(self):
    """Clear the input buffer (no-op for WebSerial)."""
    logger.debug(f"[{self._port_name}] reset_input_buffer (no-op)")

  async def reset_output_buffer(self):
    """Clear the output buffer (no-op for WebSerial)."""
    logger.debug(f"[{self._port_name}] reset_output_buffer (no-op)")

  @property
  def dtr(self) -> bool:
    """Get DTR state (not fully supported in WebSerial)."""
    return False

  @dtr.setter
  def dtr(self, value: bool):
    """Set DTR state."""
    logger.warning("DTR control not fully supported in WebSerial")

  @property
  def rts(self) -> bool:
    """Get RTS state (not fully supported in WebSerial)."""
    return False

  @rts.setter
  def rts(self, value: bool):
    """Set RTS state."""
    logger.warning("RTS control not fully supported in WebSerial")

  def serialize(self) -> dict:
    """Serialize configuration."""
    return {
      "port": self._port_name,
      "baudrate": self.baudrate,
      "bytesize": self.bytesize,
      "parity": self.parity,
      "stopbits": self.stopbits,
      "write_timeout": self.write_timeout,
      "timeout": self.timeout,
      "rtscts": self.rtscts,
      "dsrdtr": self.dsrdtr,
      "type": "WebSerial",
    }

  @classmethod
  def deserialize(cls, data: dict) -> "WebSerial":
    """Deserialize from dict (port must be re-requested)."""
    return cls(
      baudrate=data.get("baudrate", 9600),
      bytesize=data.get("bytesize", 8),
      parity=data.get("parity", "N"),
      stopbits=data.get("stopbits", 1),
      write_timeout=data.get("write_timeout", 1),
      timeout=data.get("timeout", 1),
      rtscts=data.get("rtscts", False),
      dsrdtr=data.get("dsrdtr", False),
    )
