"""Hardware discovery and connection API endpoints.

This module provides endpoints for discovering hardware devices,
managing connections, and interactive hardware control (REPL).
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from praxis.backend.services.hardware_discovery import (
    ConnectionType,
    DeviceStatus,
    DiscoveredDevice,
    HardwareDiscoveryService,
)
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Singleton service instance
_discovery_service = HardwareDiscoveryService()


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
async def connect_device(request: ConnectRequest) -> ConnectResponse:
    """Connect to a hardware device.

    Note: Full connection management is not yet implemented.
    This is a placeholder for the REPL foundation.
    """
    logger.info("Connection request for device: %s", request.device_id)

    # TODO: Implement actual connection logic with WorkcellRuntime
    # For now, return a placeholder response

    if request.device_id.startswith("sim-"):
        return ConnectResponse(
            device_id=request.device_id,
            status="connected",
            message="Simulator connected successfully (demo mode)",
            connection_handle=f"handle-{request.device_id}",
        )

    return ConnectResponse(
        device_id=request.device_id,
        status="pending",
        message="Connection management not fully implemented. Use workcell configuration for now.",
        connection_handle=None,
    )


@router.post(
    "/disconnect",
    response_model=ConnectResponse,
    summary="Disconnect from a device",
    description="Close connection to a hardware device.",
)
async def disconnect_device(request: DisconnectRequest) -> ConnectResponse:
    """Disconnect from a hardware device."""
    logger.info("Disconnect request for device: %s", request.device_id)

    return ConnectResponse(
        device_id=request.device_id,
        status="disconnected",
        message="Device disconnected",
        connection_handle=None,
    )


@router.get(
    "/connections",
    response_model=list[dict[str, Any]],
    summary="List active connections",
    description="Get list of currently active hardware connections.",
)
async def list_connections() -> list[dict[str, Any]]:
    """List all active hardware connections.

    Note: This is a placeholder. Full connection tracking will be
    implemented with Redis-backed state management.
    """
    # TODO: Integrate with Redis-backed connection state
    return []


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
