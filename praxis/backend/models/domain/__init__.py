"""Domain models for the Praxis backend - unified SQLModel definitions."""

from .asset import Asset, AssetBase, AssetCreate, AssetRead, AssetUpdate
from .deck import (
    Deck,
    DeckCreate,
    DeckDefinition,
    DeckDefinitionCreate,
    DeckDefinitionRead,
    DeckDefinitionUpdate,
    DeckPositionDefinition,
    DeckPositionDefinitionCreate,
    DeckPositionDefinitionRead,
    DeckPositionDefinitionUpdate,
    DeckRead,
    DeckUpdate,
)
from .machine import (
    Machine,
    MachineCreate,
    MachineDefinition,
    MachineDefinitionCreate,
    MachineDefinitionRead,
    MachineDefinitionUpdate,
    MachineRead,
    MachineUpdate,
)
from .outputs import (
    FunctionDataOutput,
    FunctionDataOutputCreate,
    FunctionDataOutputRead,
    FunctionDataOutputUpdate,
    WellDataOutput,
    WellDataOutputCreate,
    WellDataOutputRead,
    WellDataOutputUpdate,
)
from .protocol import ProtocolRun, ProtocolRunCreate, ProtocolRunRead, ProtocolRunUpdate
from .protocol_source import (
    FileSystemProtocolSource,
    FileSystemProtocolSourceCreate,
    FileSystemProtocolSourceRead,
    FileSystemProtocolSourceUpdate,
    ProtocolSourceRepository,
    ProtocolSourceRepositoryCreate,
    ProtocolSourceRepositoryRead,
    ProtocolSourceRepositoryUpdate,
)
from .resource import (
    Resource,
    ResourceCreate,
    ResourceDefinition,
    ResourceDefinitionCreate,
    ResourceDefinitionRead,
    ResourceDefinitionUpdate,
    ResourceRead,
    ResourceUpdate,
)
from .schedule import (
    AssetReservation,
    AssetReservationCreate,
    AssetReservationRead,
    AssetReservationUpdate,
    ScheduleEntry,
    ScheduleEntryCreate,
    ScheduleEntryRead,
    ScheduleEntryUpdate,
)
from .sqlmodel_base import PraxisBase, json_field
from .user import User, UserCreate, UserRead, UserUpdate
from .workcell import Workcell, WorkcellCreate, WorkcellRead, WorkcellUpdate

__all__ = [
    # Base
    "PraxisBase",
    "json_field",
    # Asset
    "Asset",
    "AssetBase",
    "AssetCreate",
    "AssetRead",
    "AssetUpdate",
    # Machine
    "Machine",
    "MachineCreate",
    "MachineRead",
    "MachineUpdate",
    "MachineDefinition",
    "MachineDefinitionCreate",
    "MachineDefinitionRead",
    "MachineDefinitionUpdate",
    # Resource
    "Resource",
    "ResourceCreate",
    "ResourceRead",
    "ResourceUpdate",
    "ResourceDefinition",
    "ResourceDefinitionCreate",
    "ResourceDefinitionRead",
    "ResourceDefinitionUpdate",
    # Deck
    "Deck",
    "DeckCreate",
    "DeckRead",
    "DeckUpdate",
    "DeckDefinition",
    "DeckDefinitionCreate",
    "DeckDefinitionRead",
    "DeckDefinitionUpdate",
    "DeckPositionDefinition",
    "DeckPositionDefinitionCreate",
    "DeckPositionDefinitionRead",
    "DeckPositionDefinitionUpdate",
    # Protocol
    "ProtocolRun",
    "ProtocolRunCreate",
    "ProtocolRunRead",
    "ProtocolRunUpdate",
    # Protocol Source
    "ProtocolSourceRepository",
    "ProtocolSourceRepositoryCreate",
    "ProtocolSourceRepositoryRead",
    "ProtocolSourceRepositoryUpdate",
    "FileSystemProtocolSource",
    "FileSystemProtocolSourceCreate",
    "FileSystemProtocolSourceRead",
    "FileSystemProtocolSourceUpdate",
    # Schedule
    "ScheduleEntry",
    "ScheduleEntryCreate",
    "ScheduleEntryRead",
    "ScheduleEntryUpdate",
    "AssetReservation",
    "AssetReservationCreate",
    "AssetReservationRead",
    "AssetReservationUpdate",
    # Outputs
    "FunctionDataOutput",
    "FunctionDataOutputCreate",
    "FunctionDataOutputRead",
    "FunctionDataOutputUpdate",
    "WellDataOutput",
    "WellDataOutputCreate",
    "WellDataOutputRead",
    "WellDataOutputUpdate",
    # Workcell
    "Workcell",
    "WorkcellCreate",
    "WorkcellRead",
    "WorkcellUpdate",
    # User
    "User",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
