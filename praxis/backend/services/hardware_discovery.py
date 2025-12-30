"""Hardware discovery service for detecting available lab equipment.

This service provides methods to discover hardware connected to the system,
including serial devices, network devices, and available simulators.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ConnectionType(str, Enum):
    """Type of hardware connection."""

    SERIAL = "serial"
    USB = "usb"
    NETWORK = "network"
    SIMULATOR = "simulator"


class DeviceStatus(str, Enum):
    """Status of a discovered device."""

    AVAILABLE = "available"
    BUSY = "busy"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class DiscoveredDevice:
    """Represents a discovered hardware device."""

    id: str
    name: str
    connection_type: ConnectionType
    status: DeviceStatus
    port: str | None = None
    ip_address: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    plr_backend: str | None = None  # Suggested PyLabRobot backend class
    properties: dict[str, Any] | None = None


class HardwareDiscoveryService:
    """Service for discovering available hardware devices."""

    # Known USB VID/PID pairs for lab equipment
    KNOWN_DEVICES = {
        # Hamilton devices
        (0x08BB, 0x0106): {"manufacturer": "Hamilton", "model": "STAR", "plr_backend": "pylabrobot.liquid_handling.backends.hamilton.STAR"},
        (0x08BB, 0x0107): {"manufacturer": "Hamilton", "model": "Starlet", "plr_backend": "pylabrobot.liquid_handling.backends.hamilton.Starlet"},
        # Opentrons devices
        (0x04D8, 0xE11A): {"manufacturer": "Opentrons", "model": "OT-2", "plr_backend": "pylabrobot.liquid_handling.backends.opentrons.OT2"},
        # Add more known devices here
    }

    # Known network device signatures
    NETWORK_SIGNATURES = {
        "opentrons": {"manufacturer": "Opentrons", "plr_backend": "pylabrobot.liquid_handling.backends.opentrons.OT2"},
        "hamilton": {"manufacturer": "Hamilton", "plr_backend": "pylabrobot.liquid_handling.backends.hamilton.STAR"},
    }

    def __init__(self) -> None:
        """Initialize the hardware discovery service."""
        self._cached_devices: list[DiscoveredDevice] = []

    async def discover_serial_ports(self) -> list[DiscoveredDevice]:
        """Discover devices connected via serial/USB ports.

        Returns:
            List of discovered serial devices.
        """
        devices: list[DiscoveredDevice] = []

        try:
            # Try to import serial.tools.list_ports
            from serial.tools import list_ports

            ports = list_ports.comports()
            for port in ports:
                device_info = self._identify_device(port.vid, port.pid)

                device = DiscoveredDevice(
                    id=f"serial-{port.device}",
                    name=port.description or port.device,
                    connection_type=ConnectionType.SERIAL,
                    status=DeviceStatus.AVAILABLE,
                    port=port.device,
                    manufacturer=device_info.get("manufacturer") or port.manufacturer,
                    model=device_info.get("model"),
                    serial_number=port.serial_number,
                    plr_backend=device_info.get("plr_backend"),
                    properties={
                        "vid": port.vid,
                        "pid": port.pid,
                        "hwid": port.hwid,
                    },
                )
                devices.append(device)
                logger.debug("Discovered serial device: %s on %s", device.name, port.device)

        except ImportError:
            logger.warning("pyserial not installed. Serial port discovery unavailable.")
        except Exception as e:
            logger.exception("Error discovering serial ports: %s", e)

        return devices

    async def discover_simulators(self) -> list[DiscoveredDevice]:
        """Discover available PLR simulator backends.

        Returns:
            List of available simulators.
        """
        simulators = [
            DiscoveredDevice(
                id="sim-liquid-handler",
                name="Simulated Liquid Handler",
                connection_type=ConnectionType.SIMULATOR,
                status=DeviceStatus.AVAILABLE,
                manufacturer="PyLabRobot",
                model="SimulatorBackend",
                plr_backend="pylabrobot.liquid_handling.backends.simulation.SimulatorBackend",
                properties={"simulated": True, "visualizer": True},
            ),
            DiscoveredDevice(
                id="sim-plate-reader",
                name="Simulated Plate Reader",
                connection_type=ConnectionType.SIMULATOR,
                status=DeviceStatus.AVAILABLE,
                manufacturer="PyLabRobot",
                model="SimulatedPlateReader",
                plr_backend="pylabrobot.plate_reading.backends.simulation.SimulatedPlateReader",
                properties={"simulated": True},
            ),
            DiscoveredDevice(
                id="sim-heater-shaker",
                name="Simulated Heater Shaker",
                connection_type=ConnectionType.SIMULATOR,
                status=DeviceStatus.AVAILABLE,
                manufacturer="PyLabRobot",
                model="SimulatedHeaterShaker",
                plr_backend="pylabrobot.heating_shaking.backends.simulation.SimulatedHeaterShaker",
                properties={"simulated": True},
            ),
        ]
        return simulators

    async def discover_network_devices(
        self,
        scan_range: str | None = None,
        timeout: float = 2.0,
    ) -> list[DiscoveredDevice]:
        """Discover devices on the network via mDNS/Zeroconf.

        Args:
            scan_range: Optional IP range to scan (e.g., "192.168.1.0/24").
            timeout: Timeout for discovery in seconds.

        Returns:
            List of discovered network devices.
        """
        devices: list[DiscoveredDevice] = []

        # Note: Full mDNS discovery requires zeroconf package
        # For now, return placeholder for manual IP entry
        logger.info("Network device discovery not fully implemented. Use manual IP entry.")

        return devices

    async def discover_all(self) -> list[DiscoveredDevice]:
        """Discover all available hardware devices.

        Returns:
            Combined list of all discovered devices.
        """
        all_devices: list[DiscoveredDevice] = []

        # Discover serial devices
        serial_devices = await self.discover_serial_ports()
        all_devices.extend(serial_devices)

        # Discover simulators
        simulators = await self.discover_simulators()
        all_devices.extend(simulators)

        # Discover network devices
        network_devices = await self.discover_network_devices()
        all_devices.extend(network_devices)

        # Cache for quick access
        self._cached_devices = all_devices

        logger.info(
            "Discovered %d devices: %d serial, %d simulators, %d network",
            len(all_devices),
            len(serial_devices),
            len(simulators),
            len(network_devices),
        )

        return all_devices

    def _identify_device(self, vid: int | None, pid: int | None) -> dict[str, str]:
        """Identify a device by its USB VID/PID.

        Args:
            vid: USB Vendor ID.
            pid: USB Product ID.

        Returns:
            Device information dict if recognized, empty dict otherwise.
        """
        if vid is None or pid is None:
            return {}
        return self.KNOWN_DEVICES.get((vid, pid), {})

    def get_cached_devices(self) -> list[DiscoveredDevice]:
        """Get the most recently discovered devices.

        Returns:
            Cached list of discovered devices.
        """
        return self._cached_devices
