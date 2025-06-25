"""ORM and Pydantic classes for standard interoperability and interfacing.

Imports and re-exports ORM classes and enums for asset management
and protocol definitions. It serves as a single point of access for these models,
allowing other parts of the application to import them easily.
It also includes the necessary imports for Alembic migrations, ensuring that
the database schema is in sync with the ORM models.
"""

from __future__ import annotations

from .asset_orm import Asset
from .asset_pydantic_models import AssetBase, AssetResponse
from .deck_orm import DeckOrm, DeckPositionDefinitionOrm, DeckTypeDefinitionOrm
from .deck_pydantic_models import (
  DeckBase,
  DeckCreate,
  DeckPositionDefinitionBase,
  DeckPositionDefinitionCreate,
  DeckPositionDefinitionResponse,
  DeckPositionDefinitionUpdate,
  DeckResponse,
  DeckTypeDefinitionBase,
  DeckTypeDefinitionCreate,
  DeckTypeDefinitionResponse,
  DeckTypeDefinitionUpdate,
  DeckUpdate,
  PositioningConfig,
)
from .function_data_output_orm import (
  DataOutputTypeEnum,
  FunctionDataOutputOrm,
  SpatialContextEnum,
  WellDataOutputOrm,
)
from .function_data_output_pydantic_models import (
  DataExportRequest,
  DataSearchFilters,
  FunctionDataOutputBase,
  FunctionDataOutputCreate,
  FunctionDataOutputResponse,
  FunctionDataOutputUpdate,
  PlateDataVisualization,
  ProtocolRunDataSummary,
  WellDataOutputBase,
  WellDataOutputCreate,
  WellDataOutputResponse,
  WellDataOutputUpdate,
)
from .machine_orm import MachineCategoryEnum, MachineOrm, MachineStatusEnum
from .machine_pydantic_models import (
  MachineBase,
  MachineCreate,
  MachineResponse,
  MachineUpdate,
)
from .protocol_definitions_orm import (
  FileSystemProtocolSourceOrm,
  FunctionCallLogOrm,
  FunctionCallStatusEnum,
  FunctionProtocolDefinitionOrm,
  ParameterDefinitionOrm,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ProtocolSourceRepositoryOrm,
  ProtocolSourceStatusEnum,
)
from .protocol_pydantic_models import (
  AssetRequirementModel,
  FunctionProtocolDefinitionModel,
  ParameterMetadataModel,
  ProtocolDirectories,
  ProtocolInfo,
  ProtocolParameters,
  ProtocolPrepareRequest,
  ProtocolStartRequest,
  ProtocolStatus,
  RuntimeAssetRequirement,
  UIHint,
)
from .resource_orm import ResourceOrm, ResourceStatusEnum
from .resource_pydantic_models import (
  ResourceDefinitionBase,
  ResourceDefinitionCreate,
  ResourceDefinitionResponse,
  ResourceDefinitionUpdate,
  ResourceInventoryDataIn,
  ResourceInventoryDataOut,
  ResourceInventoryItemCount,
  ResourceInventoryReagentItem,
)
from .scheduler_orm import (
  AssetReservationOrm,
  AssetReservationStatusEnum,
  ScheduleEntryOrm,
  ScheduleHistoryOrm,
  ScheduleStatusEnum,
)
from .scheduler_pydantic import (
  AssetAvailabilityResponse,
  CancelScheduleRequest,
  ResourceRequirementRequest,
  ResourceReservationResponse,
  ResourceReservationStatus,
  ScheduleAnalysisResponse,
  ScheduleEntryResponse,
  ScheduleEntryStatus,
  ScheduleHistoryResponse,
  ScheduleListRequest,
  ScheduleListResponse,
  SchedulePriorityUpdateRequest,
  ScheduleProtocolRequest,
  SchedulerMetricsResponse,
  SchedulerSystemStatusResponse,
)
from .user_management_orm import UserOrm
from .workcell_orm import WorkcellOrm, WorkcellStatusEnum
from .workcell_pydantic_models import (
  WorkcellBase,
  WorkcellCreate,
  WorkcellResponse,
  WorkcellUpdate,
)

__all__ = [
  # Asset and base models
  "AssetOrm",
  "AssetBase",
  "AssetResponse",
  # Decks
  "DeckOrm",
  "DeckBase",
  "DeckCreate",
  "DeckPositionDefinitionBase",
  "DeckPositionDefinitionCreate",
  "DeckPositionDefinitionResponse",
  "DeckPositionDefinitionUpdate",
  "DeckResponse",
  "DeckTypeDefinitionBase",
  "DeckTypeDefinitionCreate",
  "DeckTypeDefinitionResponse",
  "DeckTypeDefinitionUpdate",
  "DeckUpdate",
  "PositioningConfig",
  # Machines
  "MachineOrm",
  "MachineCategoryEnum",
  "MachineStatusEnum",
  "MachineBase",
  "MachineCreate",
  "MachineResponse",
  "MachineUpdate",
  # Resources
  "ResourceOrm",
  "ResourceStatusEnum",
  "ResourceDefinitionBase",
  "ResourceDefinitionCreate",
  "ResourceDefinitionResponse",
  "ResourceDefinitionUpdate",
  "ResourceInventoryDataIn",
  "ResourceInventoryDataOut",
  "ResourceInventoryItemCount",
  "ResourceInventoryReagentItem",
  # Protocols
  "FileSystemProtocolSourceOrm",
  "FunctionCallLogOrm",
  "FunctionCallStatusEnum",
  "FunctionProtocolDefinitionOrm",
  "ParameterDefinitionOrm",
  "ProtocolRunOrm",
  "ProtocolRunStatusEnum",
  "ProtocolSourceRepositoryOrm",
  "ProtocolSourceStatusEnum",
  "AssetRequirementModel",
  "FunctionProtocolDefinitionModel",
  "ParameterMetadataModel",
  "ProtocolDirectories",
  "ProtocolInfo",
  "ProtocolParameters",
  "ProtocolPrepareRequest",
  "ProtocolStartRequest",
  "ProtocolStatus",
  "RuntimeAssetRequirement",
  "UIHint",
  # Function data outputs
  "DataOutputTypeEnum",
  "FunctionDataOutputOrm",
  "SpatialContextEnum",
  "WellDataOutputOrm",
  "DataExportRequest",
  "DataSearchFilters",
  "FunctionDataOutputBase",
  "FunctionDataOutputCreate",
  "FunctionDataOutputResponse",
  "FunctionDataOutputUpdate",
  "PlateDataVisualization",
  "ProtocolRunDataSummary",
  "WellDataOutputBase",
  "WellDataOutputCreate",
  "WellDataOutputResponse",
  "WellDataOutputUpdate",
  # Scheduler
  "AssetReservationOrm",
  "AssetReservationStatusEnum",
  "ScheduleEntryOrm",
  "ScheduleHistoryOrm",
  "ScheduleStatusEnum",
  "AssetAvailabilityResponse",
  "CancelScheduleRequest",
  "ResourceRequirementRequest",
  "ResourceReservationResponse",
  "ResourceReservationStatus",
  "ScheduleAnalysisResponse",
  "ScheduleEntryResponse",
  "ScheduleEntryStatus",
  "ScheduleHistoryResponse",
  "ScheduleListRequest",
  "ScheduleListResponse",
  "SchedulePriorityUpdateRequest",
  "ScheduleProtocolRequest",
  "SchedulerMetricsResponse",
  "SchedulerSystemStatusResponse",
  # Users & workcells
  "UserOrm",
  "WorkcellOrm",
  "WorkcellStatusEnum",
  "WorkcellBase",
  "WorkcellCreate",
  "WorkcellResponse",
  "WorkcellUpdate",
]
