"""SQLAlchemy ORM models for managing the Praxis application.

This file defines the database schema for storing information about assets, data outputs,
schedules, workcells, and users in the Praxis application. It includes models for:
- **Asset**: Abstract base class for all physical assets in the lab.
- **DeckOrm**: Represents a physical deck in the lab, which can contain multiple machines.
- **DeckDefinitionOrm**: Represents a logical definition of a deck, including its dimensions and
  and associated machines.
- **DeckPositionDefinitionOrm**: Represents a specific position on a deck, including its dimensions
  and associated machine.
- **MachineDefinitionOrm**: Represents a logical definition of a machine, including its dimensions,
  categories, and PyLabRobot definitions.
- **MachineOrm**: Represents a specific physical instance of a machine, tracking its status and
  location.
- **FunctionDataOutputOrm**: Represents data outputs from protocol functions, including
  measurements, images, and files.
- **WellDataOutputOrm**: Represents data outputs specific to wells in a plate, including
  measurements, images, and files.
- **ProtocolSourceRepositoryOrm**: Represents a repository for protocol sources, including
  their names, descriptions, and relationships to associated machines.
- **FileSystemProtocolSourceOrm**: Represents a file system-based protocol source,
  including its path and associated metadata.
- **FunctionCallLogOrm**: Represents a log of function calls made during protocol runs,
  including their parameters and results.
- **FunctionProtocolDefinitionOrm**: Represents a logical definition of a protocol function,
  including its parameters, return types, and associated metadata.
- **ParameterDefinitionOrm**: Represents a definition of a protocol parameter,
  including its type, default value, and associated metadata.
- **AssetRequirementOrm**: Represents requirements for assets in a protocol,
  including their types, quantities, and associated metadata.
- **ProtocolRunOrm**: Represents a run of a protocol, including its status, start and end times,
  and associated metadata.
- **ResourceOrm**: Represents a resource in the lab, including its type, status, and location.
- **ResourceDefinitionOrm**: Catalogs resource definitions with metadata including dimensions,
  categories, and PyLabRobot definitions.
- **ScheduleOrm**: Represents a schedule for running protocols, including its start and end times,
  recurrence rules, and associated metadata.
- **ScheduleEntryOrm**: Represents an entry in a schedule, including its status, start and end
  times, and associated metadata.
- **AssetReservationOrm**: Represents a reservation for an asset, including its start and end times,
  and associated metadata.
- **ScheduleHistoryOrm**: Represents the history of a schedule, including its status, start and end
  times, and associated metadata.
- **SchedulerMetricsView**: A materialized view that aggregates scheduler metrics,
  including average execution times and counts of scheduled entries.
- **UserOrm**: Represents a user in the Praxis application, including their authentication
  credentials, contact details, and account status.
- **WorkcellOrm**: Represents a logical grouping of machines and resources, often a physical lab
  space or automation setup.

"""

from praxis.backend.models.orm.asset import AssetOrm
from praxis.backend.models.orm.deck import DeckDefinitionOrm, DeckOrm, DeckPositionDefinitionOrm
from praxis.backend.models.orm.machine import MachineDefinitionOrm, MachineOrm
from praxis.backend.models.orm.outputs import FunctionDataOutputOrm, WellDataOutputOrm
from praxis.backend.models.orm.protocol import (
  AssetRequirementOrm,
  FileSystemProtocolSourceOrm,
  FunctionCallLogOrm,
  FunctionProtocolDefinitionOrm,
  ParameterDefinitionOrm,
  ProtocolRunOrm,
  ProtocolSourceRepositoryOrm,
)
from praxis.backend.models.orm.resolution import (
  ResolutionActionEnum,
  ResolutionTypeEnum,
  StateResolutionLogOrm,
)
from praxis.backend.models.orm.resource import ResourceDefinitionOrm, ResourceOrm
from praxis.backend.models.orm.schedule import (
  AssetReservationOrm,
  ScheduleEntryOrm,
  ScheduleHistoryOrm,
  SchedulerMetricsView,
)
from praxis.backend.models.orm.user import UserOrm
from praxis.backend.models.orm.workcell import WorkcellOrm

__all__ = [
  "AssetOrm",
  "AssetRequirementOrm",
  "AssetReservationOrm",
  "DeckDefinitionOrm",
  "DeckOrm",
  "DeckPositionDefinitionOrm",
  "FileSystemProtocolSourceOrm",
  "FunctionCallLogOrm",
  "FunctionDataOutputOrm",
  "FunctionProtocolDefinitionOrm",
  "MachineDefinitionOrm",
  "MachineOrm",
  "ParameterDefinitionOrm",
  "ProtocolRunOrm",
  "ProtocolSourceRepositoryOrm",
  "ResolutionActionEnum",
  "ResolutionTypeEnum",
  "ResourceDefinitionOrm",
  "ResourceOrm",
  "ScheduleEntryOrm",
  "ScheduleHistoryOrm",
  "SchedulerMetricsView",
  "StateResolutionLogOrm",
  "UserOrm",
  "WellDataOutputOrm",
  "WorkcellOrm",
]
