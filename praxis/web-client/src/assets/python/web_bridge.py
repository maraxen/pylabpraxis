"""WebBridge - PyLabRobot IO shim for browser-based hardware control.

This module provides:
1. WebBridgeIO: A transport layer that routes raw bytes through WebWorker messages
   to Angular's WebSerialService, enabling PLR machines to communicate with
   physical hardware connected to the browser.
2. WebBridgeBackend: A high-level backend that sends PLR commands to the browser
   (legacy approach, kept for compatibility).
3. patch_io_for_browser: Helper to patch any PLR machine's IO layer for browser mode.
"""

import asyncio
import builtins
import json
import os
import sys
import uuid
from typing import Any

# Check if we're running in browser/Pyodide mode
IS_BROWSER_MODE = "pyodide" in sys.modules

if IS_BROWSER_MODE:
  from js import postMessage
else:
  # Mock for local testing
  def postMessage(msg):
    pass


# =============================================================================
# WebBridgeIO - Generic IO Transport for Browser Mode
# =============================================================================

# Global registry for pending read requests (used by worker to route responses)
_pending_reads: dict[str, asyncio.Future] = {}


class WebBridgeIO:
  """A PLR-compatible IO transport that routes raw bytes through the WebWorker
  message interface to Angular's WebSerialService.

  This class implements the same interface as pylabrobot.io.serial.Serial and
  pylabrobot.io.usb.USB, allowing it to be used as a drop-in replacement for
  the `self.io` attribute on any PLR machine backend.

  Example:
      backend = STAR()
      backend.io = WebBridgeIO(port_id='serial-port-1')
      await backend.setup()  # Now uses WebSerial!

  """

  def __init__(
    self,
    port_id: str,
    baudrate: int = 9600,
    read_timeout: float = 30.0,
    write_timeout: float = 30.0,
  ):
    """Initialize WebBridgeIO.

    Args:
        port_id: Identifier for the WebSerial port (from hardware discovery)
        baudrate: Baud rate for serial communication
        read_timeout: Default timeout for read operations (seconds)
        write_timeout: Default timeout for write operations (seconds)

    """
    self.port_id = port_id
    self.baudrate = baudrate
    self.read_timeout = read_timeout
    self.write_timeout = write_timeout
    self._is_open = False

  async def setup(self) -> None:
    """Initialize the connection. Opens the WebSerial port."""
    await self._send_io_command("OPEN", {"baudRate": self.baudrate})
    self._is_open = True

  async def stop(self) -> None:
    """Close the connection."""
    if self._is_open:
      await self._send_io_command("CLOSE", {})
      self._is_open = False

  async def write(self, data: bytes, timeout: float | None = None) -> int:
    """Write raw bytes to the device via WebSerial.

    Args:
        data: Bytes to write
        timeout: Write timeout in seconds (unused, for interface compatibility)

    Returns:
        Number of bytes written

    """
    await self._send_io_command(
      "WRITE",
      {
        "data": list(data)  # Convert bytes to list for JSON serialization
      },
    )
    return len(data)

  async def read(self, num_bytes: int = 1, timeout: float | None = None) -> bytes:
    """Read bytes from the device. Waits for data from WebSerial via JS bridge.

    Args:
        num_bytes: Number of bytes to read
        timeout: Read timeout in seconds

    Returns:
        Bytes read from device

    Raises:
        TimeoutError: If read times out

    """
    if timeout is None:
      timeout = self.read_timeout

    request_id = str(uuid.uuid4())
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    _pending_reads[request_id] = future

    await self._send_io_command(
      "READ", {"size": num_bytes, "timeout": timeout, "request_id": request_id}
    )

    try:
      result = await asyncio.wait_for(future, timeout=timeout + 1)
      return bytes(result)
    except asyncio.TimeoutError:
      msg = f"Read timeout after {timeout}s on port {self.port_id}"
      raise TimeoutError(msg)
    finally:
      _pending_reads.pop(request_id, None)

  async def readline(self) -> bytes:
    """Read a line from the device (until newline character).

    Returns:
        Bytes including the newline character

    """
    request_id = str(uuid.uuid4())
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    _pending_reads[request_id] = future

    await self._send_io_command(
      "READLINE", {"timeout": self.read_timeout, "request_id": request_id}
    )

    try:
      result = await asyncio.wait_for(future, timeout=self.read_timeout + 1)
      return bytes(result)
    except asyncio.TimeoutError:
      msg = f"Readline timeout on port {self.port_id}"
      raise TimeoutError(msg)
    finally:
      _pending_reads.pop(request_id, None)

  async def _send_io_command(self, command: str, data: dict) -> None:
    """Send an IO command to the JavaScript layer."""
    message = {"type": "RAW_IO", "payload": {"command": command, "port_id": self.port_id, **data}}
    postMessage(json.dumps(message))

  def serialize(self) -> dict:
    """Serialize the IO configuration."""
    return {
      "type": "WebBridgeIO",
      "port_id": self.port_id,
      "baudrate": self.baudrate,
      "read_timeout": self.read_timeout,
      "write_timeout": self.write_timeout,
    }


def handle_io_response(request_id: str, data: list) -> None:
  """Called by the worker when JS sends data back from WebSerial.

  This function is invoked from python.worker.ts when a RAW_IO_RESPONSE
  message is received from the Angular main thread.

  Args:
      request_id: The request ID that was sent with the READ command
      data: List of byte values received from the device

  """
  future = _pending_reads.get(request_id)
  if future and not future.done():
    future.set_result(data)
  elif request_id not in _pending_reads:
    pass


# =============================================================================
# Machine Patcher - Patch any PLR machine for browser mode
# =============================================================================


def patch_io_for_browser(machine: Any, port_id: str, baudrate: int = 9600) -> Any:
  """Patch a PLR machine's transport layer to use WebBridgeIO.

  This function replaces the `self.io` attribute on a machine's backend
  with a WebBridgeIO instance, allowing the machine to communicate with
  hardware connected to the browser via WebSerial.

  Args:
      machine: Any PLR Machine instance (LiquidHandler, HeaterShaker, etc.)
      port_id: The WebSerial port identifier from hardware discovery
      baudrate: Baud rate for serial communication (default: 9600)

  Returns:
      The patched machine instance

  Example:
      lh = LiquidHandler(backend=STAR())
      patch_io_for_browser(lh, 'serial-port-1')
      await lh.setup()  # Now uses WebSerial!

  """
  if not IS_BROWSER_MODE:
    return machine

  backend = getattr(machine, "backend", None)
  if backend is None:
    return machine

  web_io = WebBridgeIO(port_id=port_id, baudrate=baudrate)

  # Try known IO attribute names
  io_attrs = ["io", "_io", "connection", "_connection", "ser", "_ser"]
  patched = False
  for attr in io_attrs:
    if hasattr(backend, attr):
      setattr(backend, attr, web_io)
      patched = True
      break

  if not patched:
    pass

  return machine


def create_browser_machine(
  machine_class, backend_class, port_id: str, baudrate: int = 9600, **kwargs
):
  """Factory function to create a PLR machine pre-configured for browser mode.

  Args:
      machine_class: The machine class (e.g., LiquidHandler)
      backend_class: The backend class (e.g., STAR)
      port_id: WebSerial port identifier
      baudrate: Baud rate for serial communication
      **kwargs: Additional arguments passed to backend constructor

  Returns:
      A machine instance with WebBridgeIO patched

  Example:
      lh = create_browser_machine(LiquidHandler, STAR, 'serial-port-1')
      await lh.setup()

  """
  backend = backend_class(**kwargs)
  machine = machine_class(backend=backend)
  return patch_io_for_browser(machine, port_id, baudrate)


# =============================================================================
# Legacy WebBridgeBackend (kept for compatibility)
# =============================================================================

# Try to import LiquidHandlerBackend - may not be available in browser mode
try:
  from pylabrobot.liquid_handling.backends import LiquidHandlerBackend

  _HAS_PLR = True
except ImportError:
  _HAS_PLR = False
  LiquidHandlerBackend = object  # Fallback base class


class WebBridgeBackend(LiquidHandlerBackend if _HAS_PLR else object):
  """A PyLabRobot backend that routes commands to the browser's main thread via WebWorker messages.
  This allows the Python code running in WASM to control hardware connected to the browser (WebSerial).
  """

  def __init__(self, num_channels: int = 8):
    super().__init__()
    self._num_channels = num_channels

  async def setup(self):
    self.send_command("setup", {})

  async def stop(self):
    self.send_command("stop", {})

  def send_command(self, command: str, data: dict):
    """Sends a command to the JavaScript main thread."""
    message = {"type": "PLR_COMMAND", "payload": {"command": command, "data": data}}
    # In Pyodide worker, postMessage is available globally or via js module
    # We use a synchronous conversion to dict/json for safety across the boundary
    postMessage(json.dumps(message))

  # -------------------------------------------------------------------------
  # LiquidHandlerBackend Implementation
  # -------------------------------------------------------------------------

  async def assigned_resource_callback(self, resource):
    self.send_command(
      "resource_assigned",
      {"resource_name": resource.name, "resource_type": resource.__class__.__name__},
    )

  async def pick_up_tips(self, ops):
    self.send_command("pick_up_tips", {"ops": [op.serialize() for op in ops]})

  async def drop_tips(self, ops):
    self.send_command("drop_tips", {"ops": [op.serialize() for op in ops]})

  async def aspirate(self, ops):
    self.send_command("aspirate", {"ops": [op.serialize() for op in ops]})

  async def dispense(self, ops):
    self.send_command("dispense", {"ops": [op.serialize() for op in ops]})

  async def pick_up_tips96(self, pickup):
    self.send_command("pick_up_tips96", {"resource_name": pickup.resource.name})

  async def drop_tips96(self, drop):
    self.send_command("drop_tips96", {"resource_name": drop.resource.name})

  async def aspirate96(self, aspiration):
    self.send_command("aspirate96", {"volume": aspiration.volume})

  async def dispense96(self, dispense):
    self.send_command("dispense96", {"volume": dispense.volume})

  @property
  def num_channels(self) -> int:
    return self._num_channels


import io
import sys

from js import postMessage


class StdoutRedirector(io.TextIOBase):
  def __init__(self, stream_type="STDOUT"):
    self.stream_type = stream_type

  def write(self, s):
    if s:
      # We transmit everything, even newlines alone, to keep accurate formatting
      postMessage(json.dumps({"type": self.stream_type, "payload": s}))
    return len(s)


def bootstrap_playground(namespace=None):
  """Sets up the environment for the web playground:
  1. Redirects stdout/stderr to the browser.
  2. Imports common PyLabRobot classes.

  Args:
      namespace: Optional dictionary to inject variables into (e.g. console.globals).
                 If None, temporarily injects into __main__ (legacy behavior).

  """
  sys.stdout = StdoutRedirector("STDOUT")
  sys.stderr = StdoutRedirector("STDERR")

  target = namespace if namespace is not None else {}

  try:
    import pylabrobot.liquid_handling
    import pylabrobot.liquid_handling.backends
    import pylabrobot.resources

    # Core classes
    target["LiquidHandler"] = pylabrobot.liquid_handling.LiquidHandler

    # Resources
    target["Plate"] = pylabrobot.resources.Plate
    target["TipRack"] = pylabrobot.resources.TipRack
    target["Resource"] = pylabrobot.resources.Resource
    target["Container"] = pylabrobot.resources.Container
    target["Deck"] = pylabrobot.resources.Deck

    # Backends
    target["LiquidHandlerBackend"] = pylabrobot.liquid_handling.backends.LiquidHandlerBackend
    # Import specific backends if available
    for name, cls in pylabrobot.liquid_handling.backends.__dict__.items():
      if isinstance(cls, type) and name.endswith("Backend"):
        target[name] = cls

    # Standard PLR Layouts/Machines if available
    try:
      from pylabrobot.liquid_handling.backends.hamilton import STAR

      target["STAR"] = STAR
    except ImportError:
      pass

    # If using __main__ fallback
    if namespace is None:
      import __main__

      for k, v in target.items():
        setattr(__main__, k, v)

  except ImportError:
    pass

  # Inject WebSerial & WebUSB from shims if available
  try:
    # Ensure importability from root/current dir
    if "." not in sys.path:
      sys.path.append(".")
    if "/" not in sys.path:
      sys.path.append("/")

    print(f"DEBUG: CWD={os.getcwd()}", file=sys.stderr)

    # 1. Inject WebSerial
    try:
      from web_serial_shim import WebSerial

      if namespace is not None:
        namespace["WebSerial"] = WebSerial
      builtins.WebSerial = WebSerial
      print("SUCCESS: WebSerial injected into builtins", file=sys.stderr)
    except ImportError:
      print("WARNING: web_serial_shim not found", file=sys.stderr)

    # 2. Inject WebUSB
    try:
      from web_usb_shim import WebUSB

      if namespace is not None:
        namespace["WebUSB"] = WebUSB
      builtins.WebUSB = WebUSB
      print("SUCCESS: WebUSB injected into builtins", file=sys.stderr)
    except ImportError:
      print("WARNING: web_usb_shim not found", file=sys.stderr)

  except Exception as e:
    import traceback

    print(f"ERROR: Failed during shim injection: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)


# =============================================================================
# Signature Help (still uses Jedi if available)
# =============================================================================

_jedi_available = False
_jedi_install_attempted = False


def _ensure_jedi():
  """Ensure Jedi is installed and available.
  Returns True if Jedi is ready, False otherwise.
  """
  global _jedi_available, _jedi_install_attempted

  if _jedi_available:
    return True

  if _jedi_install_attempted:
    return False

  _jedi_install_attempted = True

  try:
    import jedi

    _jedi_available = True
    return True
  except ImportError:
    # Try to install jedi via micropip
    if IS_BROWSER_MODE:
      try:
        import asyncio

        import micropip

        async def install_jedi():
          await micropip.install("jedi")

        # Run in event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(install_jedi())

        _jedi_available = True
        return True
      except Exception:
        # Jedi is optional for signature help
        return False
    else:
      return False


def get_signatures(source: str, line: int = 1, column: int | None = None) -> list:
  """Get function signatures for the code at cursor position.
  Used for showing parameter hints when typing function calls.

  Args:
      source: Full source code up to cursor
      line: Line number (1-indexed)
      column: Column position (0-indexed)

  Returns:
      List of signature dicts with name, params, docstring

  """
  if not _ensure_jedi():
    return []

  try:
    import jedi

    import __main__

    if column is None:
      lines = source.split("\n")
      column = len(lines[-1]) if lines else 0

    script = jedi.Interpreter(source, namespaces=[__main__.__dict__])

    signatures = script.get_signatures(line, column)

    return [
      {
        "name": sig.name,
        "params": [p.description for p in sig.params],
        "index": sig.index,  # Current parameter index
        "docstring": sig.docstring(fast=True),
      }
      for sig in signatures
    ]
  except Exception:
    return []
