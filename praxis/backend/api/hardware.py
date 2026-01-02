"""Hardware discovery and connection API endpoints.

This module provides endpoints for discovering hardware devices,
managing connections, and interactive hardware control (REPL).
"""

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from praxis.backend.services.hardware_connection_manager import (
  ConnectionState,
  HardwareConnectionManager,
)
from praxis.backend.services.hardware_discovery import (
  ConnectionType,
  DeviceStatus,
  HardwareDiscoveryService,
)
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Singleton service instance
_discovery_service = HardwareDiscoveryService()


def get_connection_manager(request: Request) -> HardwareConnectionManager:
  """Dependency to get the hardware connection manager.

  Uses the KeyValueStore from application state.
  """
  kv_store = request.app.state.kv_store
  return HardwareConnectionManager(kv_store)


# ============================================================================
# Pydantic Models
# ============================================================================


class DiscoveredDeviceResponse(BaseModel):
  """Response model for a discovered device."""

  id: str
  name: str
  connection_type: ConnectionType
  status: DeviceStatus
  port: str | None = None
  ip_address: str | None = None
  manufacturer: str | None = None
  model: str | None = None
  serial_number: str | None = None
  plr_backend: str | None = None
  properties: dict[str, Any] | None = None


class DiscoveryResponse(BaseModel):
  """Response model for discovery results."""

  devices: list[DiscoveredDeviceResponse]
  total: int
  serial_count: int
  simulator_count: int
  network_count: int


class ConnectRequest(BaseModel):
  """Request to connect to a device."""

  device_id: str
  backend_class: str | None = None
  config: dict[str, Any] | None = None


class ConnectResponse(BaseModel):
  """Response after connecting to a device."""

  device_id: str
  status: str
  message: str
  connection_handle: str | None = None


class DisconnectRequest(BaseModel):
  """Request to disconnect from a device."""

  device_id: str


class RegisterMachineRequest(BaseModel):
  """Request to register a discovered device as a machine."""

  device_id: str
  name: str
  plr_backend: str
  connection_type: str
  port: str | None = None
  ip_address: str | None = None
  configuration: dict[str, Any] | None = None


class RegisterMachineResponse(BaseModel):
  """Response after registering a machine."""

  accession_id: str
  name: str
  status: str
  message: str


class ReplCommand(BaseModel):
  """REPL command to execute on a connected device."""

  device_id: str
  command: str


class ReplResponse(BaseModel):
  """Response from REPL command execution."""

  device_id: str
  command: str
  output: str
  success: bool
  error: str | None = None


class ConnectionStateResponse(BaseModel):
  """Response model for connection state."""

  device_id: str
  status: str
  connected_at: datetime | None = None
  last_heartbeat: datetime
  backend_class: str | None = None
  config: dict[str, Any] = {}
  error_message: str | None = None

  @classmethod
  def from_state(cls, state: ConnectionState) -> "ConnectionStateResponse":
    """Create from ConnectionState dataclass."""
    return cls(
      device_id=state.device_id,
      status=state.status,
      connected_at=state.connected_at,
      last_heartbeat=state.last_heartbeat,
      backend_class=state.backend_class,
      config=state.config,
      error_message=state.error_message,
    )


class HeartbeatRequest(BaseModel):
  """Request to send heartbeat for a connection."""

  device_id: str


class HeartbeatResponse(BaseModel):
  """Response after heartbeat."""

  device_id: str
  success: bool
  message: str
  last_heartbeat: datetime | None = None


# ============================================================================
# Endpoints
# ============================================================================


@router.get(
  "/discover",
  response_model=DiscoveryResponse,
  summary="Discover available hardware",
  description="Scan for connected hardware devices including serial ports, USB, network, and simulators.",
)
async def discover_hardware() -> DiscoveryResponse:
  """Discover all available hardware devices."""
  try:
    devices = await _discovery_service.discover_all()

    # Convert dataclasses to response models
    device_responses = [
      DiscoveredDeviceResponse(
        id=d.id,
        name=d.name,
        connection_type=d.connection_type,
        status=d.status,
        port=d.port,
        ip_address=d.ip_address,
        manufacturer=d.manufacturer,
        model=d.model,
        serial_number=d.serial_number,
        plr_backend=d.plr_backend,
        properties=d.properties,
      )
      for d in devices
    ]

    # Count by type
    serial_count = sum(1 for d in devices if d.connection_type == ConnectionType.SERIAL)
    simulator_count = sum(1 for d in devices if d.connection_type == ConnectionType.SIMULATOR)
    network_count = sum(1 for d in devices if d.connection_type == ConnectionType.NETWORK)

    return DiscoveryResponse(
      devices=device_responses,
      total=len(devices),
      serial_count=serial_count,
      simulator_count=simulator_count,
      network_count=network_count,
    )

  except Exception as e:
    logger.exception("Error during hardware discovery: %s", e)
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Hardware discovery failed: {e}",
    ) from e


@router.get(
  "/discover/serial",
  response_model=list[DiscoveredDeviceResponse],
  summary="Discover serial devices",
  description="Scan for devices connected via serial/USB ports.",
)
async def discover_serial() -> list[DiscoveredDeviceResponse]:
  """Discover serial/USB connected devices."""
  devices = await _discovery_service.discover_serial_ports()
  return [
    DiscoveredDeviceResponse(
      id=d.id,
      name=d.name,
      connection_type=d.connection_type,
      status=d.status,
      port=d.port,
      manufacturer=d.manufacturer,
      model=d.model,
      serial_number=d.serial_number,
      plr_backend=d.plr_backend,
      properties=d.properties,
    )
    for d in devices
  ]


@router.get(
  "/discover/simulators",
  response_model=list[DiscoveredDeviceResponse],
  summary="List available simulators",
  description="Get list of available PyLabRobot simulator backends.",
)
async def discover_simulators() -> list[DiscoveredDeviceResponse]:
  """List available simulator backends."""
  devices = await _discovery_service.discover_simulators()
  return [
    DiscoveredDeviceResponse(
      id=d.id,
      name=d.name,
      connection_type=d.connection_type,
      status=d.status,
      manufacturer=d.manufacturer,
      model=d.model,
      plr_backend=d.plr_backend,
      properties=d.properties,
    )
    for d in devices
  ]


@router.post(
  "/connect",
  response_model=ConnectResponse,
  summary="Connect to a device",
  description="Establish connection to a discovered hardware device.",
)
async def connect_device(
  request: ConnectRequest,
  manager: Annotated[HardwareConnectionManager, Depends(get_connection_manager)],
) -> ConnectResponse:
  """Connect to a hardware device.

  This registers the connection in the persistent state store,
  allowing connection tracking across server restarts.
  """
  logger.info("Connection request for device: %s", request.device_id)

  try:
    # Register connection in state store
    state = await manager.connect(
      device_id=request.device_id,
      backend_class=request.backend_class,
      config=request.config or {},
    )

    # For simulators, mark as immediately connected
    if request.device_id.startswith("sim-"):
      return ConnectResponse(
        device_id=request.device_id,
        status="connected",
        message="Simulator connected successfully",
        connection_handle=f"handle-{request.device_id}",
      )

    # For real hardware, the actual connection is handled by WorkcellRuntime
    # This just tracks the connection state
    return ConnectResponse(
      device_id=request.device_id,
      status=state.status,
      message=f"Connection registered for {request.backend_class or 'device'}",
      connection_handle=f"handle-{request.device_id}",
    )

  except Exception as e:
    logger.exception("Error connecting to device: %s", request.device_id)
    # Try to set error state
    await manager.set_error(request.device_id, str(e))
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Connection failed: {e}",
    ) from e


@router.post(
  "/disconnect",
  response_model=ConnectResponse,
  summary="Disconnect from a device",
  description="Close connection to a hardware device.",
)
async def disconnect_device(
  request: DisconnectRequest,
  manager: Annotated[HardwareConnectionManager, Depends(get_connection_manager)],
) -> ConnectResponse:
  """Disconnect from a hardware device.

  Removes the connection from the persistent state store.
  """
  logger.info("Disconnect request for device: %s", request.device_id)

  existed = await manager.disconnect(request.device_id)

  if existed:
    return ConnectResponse(
      device_id=request.device_id,
      status="disconnected",
      message="Device disconnected successfully",
      connection_handle=None,
    )

  return ConnectResponse(
    device_id=request.device_id,
    status="disconnected",
    message="Device was not connected",
    connection_handle=None,
  )


@router.get(
  "/connections",
  response_model=list[ConnectionStateResponse],
  summary="List active connections",
  description="Get list of currently active hardware connections.",
)
async def list_connections(
  manager: Annotated[HardwareConnectionManager, Depends(get_connection_manager)],
) -> list[ConnectionStateResponse]:
  """List all active hardware connections.

  Returns connections stored in the persistent state store (Redis or SQLite).
  Stale connections (without heartbeat) are automatically cleaned up.
  """
  connections = await manager.list_connections()
  return [ConnectionStateResponse.from_state(c) for c in connections]


@router.post(
  "/heartbeat",
  response_model=HeartbeatResponse,
  summary="Send connection heartbeat",
  description="Keep a connection alive by sending a heartbeat.",
)
async def send_heartbeat(
  request: HeartbeatRequest,
  manager: Annotated[HardwareConnectionManager, Depends(get_connection_manager)],
) -> HeartbeatResponse:
  """Send a heartbeat to keep a connection alive.

  Connections without heartbeats will expire after the TTL (default 2 minutes).
  This should be called periodically by clients to maintain connections.
  """
  state = await manager.heartbeat(request.device_id)

  if state is None:
    return HeartbeatResponse(
      device_id=request.device_id,
      success=False,
      message="Connection not found or expired",
      last_heartbeat=None,
    )

  return HeartbeatResponse(
    device_id=request.device_id,
    success=True,
    message="Heartbeat received",
    last_heartbeat=state.last_heartbeat,
  )


@router.get(
  "/connections/{device_id}",
  response_model=ConnectionStateResponse,
  summary="Get connection state",
  description="Get the current state of a specific connection.",
)
async def get_connection(
  device_id: str,
  manager: Annotated[HardwareConnectionManager, Depends(get_connection_manager)],
) -> ConnectionStateResponse:
  """Get the connection state for a specific device."""
  state = await manager.get_connection(device_id)

  if state is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Connection not found: {device_id}",
    )

  return ConnectionStateResponse.from_state(state)


@router.post(
  "/register",
  response_model=RegisterMachineResponse,
  summary="Register a device as a machine",
  description="Register a discovered hardware device as a machine in the system.",
)
async def register_machine(request: RegisterMachineRequest) -> RegisterMachineResponse:
  """Register a discovered device as a managed machine.

  This creates a machine record in the database, allowing it to be
  used in workcells and protocols.
  """
  import uuid

  logger.info(
    "Registering device %s as machine: %s (backend: %s)",
    request.device_id,
    request.name,
    request.plr_backend,
  )

  # TODO: Integrate with MachineService to create actual machine record
  # For now, return a placeholder response
  accession_id = str(uuid.uuid4())

  return RegisterMachineResponse(
    accession_id=accession_id,
    name=request.name,
    status="registered",
    message=f"Machine '{request.name}' registered successfully with backend {request.plr_backend}",
  )


@router.post(
  "/repl",
  response_model=ReplResponse,
  summary="Execute REPL command",
  description="Execute a command on a connected hardware device.",
)
async def execute_repl_command(request: ReplCommand) -> ReplResponse:
  """Execute a REPL command on a connected device.

  This provides interactive hardware control for debugging,
  testing, and manual operations.

  Note: Full REPL implementation requires WebSocket support for
  bidirectional communication. This endpoint is for simple
  request-response commands.
  """
  logger.info("REPL command for device %s: %s", request.device_id, request.command)

  # TODO: Implement actual command execution via WorkcellRuntime
  # For now, return a placeholder response

  if request.device_id.startswith("sim-"):
    return ReplResponse(
      device_id=request.device_id,
      command=request.command,
      output=f"[Simulator] Executed: {request.command}\nOK",
      success=True,
      error=None,
    )

  return ReplResponse(
    device_id=request.device_id,
    command=request.command,
    output="REPL execution not yet implemented for real hardware",
    success=False,
    error="REPL requires WebSocket connection for real hardware",
  )
