"""PyLabPraxis Example Protocols Package.

This package contains demo protocols that demonstrate the protocol decorator
and type-hinted protocol parameters. These protocols use generic PLR types
(Plate, TipRack) which are resolved to specific resource definitions at
protocol setup time.
"""

from praxis.protocol.protocols.plate_preparation import plate_preparation
from praxis.protocol.protocols.serial_dilution import serial_dilution
from praxis.protocol.protocols.simple_transfer import simple_transfer

__all__ = [
    "simple_transfer",
    "serial_dilution",
    "plate_preparation",
]
