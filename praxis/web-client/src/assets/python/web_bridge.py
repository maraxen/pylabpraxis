"""
WebBridge - PyLabRobot IO shim for browser-based hardware control.

This module provides:
1. WebBridgeIO: A transport layer that routes raw bytes through WebWorker messages
   to Angular's WebSerialService, enabling PLR machines to communicate with
   physical hardware connected to the browser.
2. WebBridgeBackend: A high-level backend that sends PLR commands to the browser
   (legacy approach, kept for compatibility).
3. patch_io_for_browser: Helper to patch any PLR machine's IO layer for browser mode.
"""

import json
import asyncio
import sys
import uuid
from typing import Optional, Dict, Any

# Check if we're running in browser/Pyodide mode
IS_BROWSER_MODE = 'pyodide' in sys.modules

if IS_BROWSER_MODE:
    from js import postMessage
else:
    # Mock for local testing
    def postMessage(msg):
        print(f"[MockPostMessage] {msg}")


# =============================================================================
# WebBridgeIO - Generic IO Transport for Browser Mode
# =============================================================================

# Global registry for pending read requests (used by worker to route responses)
_pending_reads: Dict[str, asyncio.Future] = {}


class WebBridgeIO:
    """
    A PLR-compatible IO transport that routes raw bytes through the WebWorker
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
        """
        Initialize WebBridgeIO.
        
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
        await self._send_io_command('OPEN', {
            'baudRate': self.baudrate
        })
        self._is_open = True
        print(f"WebBridgeIO: Opened port {self.port_id} at {self.baudrate} baud")
        
    async def stop(self) -> None:
        """Close the connection."""
        if self._is_open:
            await self._send_io_command('CLOSE', {})
            self._is_open = False
            print(f"WebBridgeIO: Closed port {self.port_id}")
    
    async def write(self, data: bytes, timeout: Optional[float] = None) -> int:
        """
        Write raw bytes to the device via WebSerial.
        
        Args:
            data: Bytes to write
            timeout: Write timeout in seconds (unused, for interface compatibility)
            
        Returns:
            Number of bytes written
        """
        await self._send_io_command('WRITE', {
            'data': list(data)  # Convert bytes to list for JSON serialization
        })
        return len(data)
    
    async def read(self, num_bytes: int = 1, timeout: Optional[float] = None) -> bytes:
        """
        Read bytes from the device. Waits for data from WebSerial via JS bridge.
        
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
        
        await self._send_io_command('READ', {
            'size': num_bytes,
            'timeout': timeout,
            'request_id': request_id
        })
        
        try:
            result = await asyncio.wait_for(future, timeout=timeout + 1)
            return bytes(result)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Read timeout after {timeout}s on port {self.port_id}")
        finally:
            _pending_reads.pop(request_id, None)
    
    async def readline(self) -> bytes:
        """
        Read a line from the device (until newline character).
        
        Returns:
            Bytes including the newline character
        """
        request_id = str(uuid.uuid4())
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        _pending_reads[request_id] = future
        
        await self._send_io_command('READLINE', {
            'timeout': self.read_timeout,
            'request_id': request_id
        })
        
        try:
            result = await asyncio.wait_for(future, timeout=self.read_timeout + 1)
            return bytes(result)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Readline timeout on port {self.port_id}")
        finally:
            _pending_reads.pop(request_id, None)
    
    async def _send_io_command(self, command: str, data: dict) -> None:
        """Send an IO command to the JavaScript layer."""
        message = {
            'type': 'RAW_IO',
            'payload': {
                'command': command,
                'port_id': self.port_id,
                **data
            }
        }
        postMessage(json.dumps(message))
    
    def serialize(self) -> dict:
        """Serialize the IO configuration."""
        return {
            'type': 'WebBridgeIO',
            'port_id': self.port_id,
            'baudrate': self.baudrate,
            'read_timeout': self.read_timeout,
            'write_timeout': self.write_timeout,
        }


def handle_io_response(request_id: str, data: list) -> None:
    """
    Called by the worker when JS sends data back from WebSerial.
    
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
        print(f"WebBridgeIO: Received response for unknown request {request_id}")


# =============================================================================
# Machine Patcher - Patch any PLR machine for browser mode
# =============================================================================

def patch_io_for_browser(machine: Any, port_id: str, baudrate: int = 9600) -> Any:
    """
    Patch a PLR machine's transport layer to use WebBridgeIO.
    
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
        print("patch_io_for_browser: Not in browser mode, skipping patch")
        return machine
    
    backend = getattr(machine, 'backend', None)
    if backend is None:
        print(f"patch_io_for_browser: {type(machine).__name__} has no backend attribute")
        return machine
    
    web_io = WebBridgeIO(port_id=port_id, baudrate=baudrate)
    
    # Try known IO attribute names
    io_attrs = ['io', '_io', 'connection', '_connection', 'ser', '_ser']
    patched = False
    for attr in io_attrs:
        if hasattr(backend, attr):
            setattr(backend, attr, web_io)
            print(f"patch_io_for_browser: Patched {type(backend).__name__}.{attr} with WebBridgeIO(port_id='{port_id}')")
            patched = True
            break
    
    if not patched:
        print(f"patch_io_for_browser: Could not find IO attribute on {type(backend).__name__}")
    
    return machine


def create_browser_machine(machine_class, backend_class, port_id: str, baudrate: int = 9600, **kwargs):
    """
    Factory function to create a PLR machine pre-configured for browser mode.
    
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

from pylabrobot.liquid_handling.backends import LiquidHandlerBackend

class WebBridgeBackend(LiquidHandlerBackend):
    """
    A PyLabRobot backend that routes commands to the browser's main thread via WebWorker messages.
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
        """
        Sends a command to the JavaScript main thread.
        """
        message = {
            "type": "PLR_COMMAND",
            "payload": {
                "command": command,
                "data": data
            }
        }
        # In Pyodide worker, postMessage is available globally or via js module
        # We use a synchronous conversion to dict/json for safety across the boundary
        postMessage(json.dumps(message))

    # -------------------------------------------------------------------------
    # LiquidHandlerBackend Implementation
    # -------------------------------------------------------------------------
    
    async def assigned_resource_callback(self, resource):
        self.send_command("resource_assigned", {"resource_name": resource.name, "resource_type": resource.__class__.__name__})

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

import sys
import io
from js import postMessage

class StdoutRedirector(io.TextIOBase):
    def __init__(self, stream_type='STDOUT'):
        self.stream_type = stream_type

    def write(self, s):
        if s:
            # We transmit everything, even newlines alone, to keep accurate formatting
            postMessage(json.dumps({
                "type": self.stream_type,
                "payload": s
            }))
        return len(s)


def bootstrap_repl():
    """
    Sets up the environment for the web REPL:
    1. Redirects stdout/stderr to the browser.
    2. Imports common PyLabRobot classes.
    """
    sys.stdout = StdoutRedirector('STDOUT')
    sys.stderr = StdoutRedirector('STDERR')
    
    # Auto-imports
    # We inject into __main__ so they are available in the global REPL scope
    import __main__
    try:
        import pylabrobot.liquid_handling
        import pylabrobot.resources
        import pylabrobot.liquid_handling.backends
        
        # Core classes
        __main__.LiquidHandler = pylabrobot.liquid_handling.LiquidHandler
        
        # Resources
        __main__.Plate = pylabrobot.resources.Plate
        __main__.TipRack = pylabrobot.resources.TipRack
        __main__.Resource = pylabrobot.resources.Resource
        __main__.Container = pylabrobot.resources.Container
        __main__.Deck = pylabrobot.resources.Deck
        
        # Backends
        __main__.LiquidHandlerBackend = pylabrobot.liquid_handling.backends.LiquidHandlerBackend
        # Import specific backends if available
        # We can inspect the module to get all backend classes
        for name, cls in pylabrobot.liquid_handling.backends.__dict__.items():
            if isinstance(cls, type) and name.endswith('Backend'):
                setattr(__main__, name, cls)

        # Standard PLR Layouts/Machines if available
        # For now, let's try to grab STAR
        try:
             from pylabrobot.liquid_handling.backends.hamilton import STAR
             __main__.STAR = STAR
        except ImportError:
             pass

        print("PyLabRobot initialized. Available classes: LiquidHandler, Plate, TipRack, etc.")
    except ImportError:
        print("PyLabRobot not found. Running in basic Python mode.")

def get_completions(code):
    """
    Returns a list of completions for the given code.
    Uses rlcompleter bound to __main__.
    """
    import rlcompleter
    import __main__
    
    completer = rlcompleter.Completer(__main__.__dict__)
    matches = []
    state = 0
    while True:
        match = completer.complete(code, state)
        if match is None:
            break
        matches.append(match)
        state += 1
    return matches

