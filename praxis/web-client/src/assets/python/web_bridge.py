import json
import asyncio
from pylabrobot.liquid_handling.backends import LiquidHandlerBackend
from js import postMessage

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
