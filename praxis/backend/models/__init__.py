"""ORM and Pydantic classes for standard interoperability and interfacing.

Imports and re-exports ORM classes and enums for asset management
and protocol definitions. It serves as a single point of access for these models,
allowing other parts of the application to import them easily.
It also includes the necessary imports for Alembic migrations, ensuring that
the database schema is in sync with the ORM models.
"""

from __future__ import annotations

from .asset_management_orm import (
    AssetInstanceOrm,
)
from .asset_pydantic_models import AssetBase, AssetResponse
from .deck_orm import (
    DeckConfigurationOrm,
    DeckConfigurationPoseItemOrm,
    DeckPoseDefinitionOrm,
    DeckTypeDefinitionOrm,
)
from .deck_pydantic_models import (
    DeckLayoutBase,
    DeckLayoutCreate,
    DeckLayoutResponse,
    DeckLayoutUpdate,
    DeckPoseDefinitionBase,
    DeckPoseDefinitionCreate,
    DeckPoseDefinitionResponse,
    DeckPoseDefinitionUpdate,
    DeckPoseItemBase,
    DeckPoseItemCreate,
    DeckPoseItemResponse,
    DeckTypeDefinitionBase,
    DeckTypeDefinitionCreate,
    DeckTypeDefinitionResponse,
    DeckTypeDefinitionUpdate,
)
from .machine_orm import MachineCategoryEnum, MachineOrm, MachineStatusEnum
from .machine_pydantic_models import (
    MachineBase,
    MachineCreate,
    MachineCreationRequest,
    MachineResponse,
    MachineTypeInfo,
    MachineUpdate,
)
from .protocol_definitions_orm import (
    AssetDefinitionOrm,
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
    UIHint,
)
from .resource_orm import (
    ResourceDefinitionCatalogOrm,
    ResourceInstanceOrm,
    ResourceInstanceStatusEnum,
)
from .resource_pydantic_models import (
    ResourceDefinitionBase,
    ResourceDefinitionCreate,
    ResourceDefinitionResponse,
    ResourceDefinitionUpdate,
    ResourceInstanceCreate,
    ResourceInstanceResponse,
    ResourceInstanceSharedFields,
    ResourceInstanceUpdate,
    ResourceInventoryDataIn,
    ResourceInventoryDataOut,
    ResourceInventoryItemCount,
    ResourceInventoryReagentItem,
)
from .user_management_orm import UserOrm
from .workcell_pydantic_models import (
    DeckInfo,
    DeckStateResponse,
    DeckUpdateMessage,
    PoseInfo,
    ResourceInfo,
)

__all__ = [
    "MachineOrm",
    "ResourceInstanceOrm",
    "ResourceDefinitionCatalogOrm",
    "MachineStatusEnum",
    "ResourceInstanceStatusEnum",  # ResourceCategoryEnum removed
    "ProtocolSourceStatusEnum",
    "ProtocolRunStatusEnum",
    "FunctionCallStatusEnum",
    "ProtocolSourceRepositoryOrm",
    "FileSystemProtocolSourceOrm",
    "FunctionProtocolDefinitionOrm",
    "ParameterDefinitionOrm",
    "AssetDefinitionOrm",
    "ProtocolRunOrm",
    "FunctionCallLogOrm",
    "AssetInstanceOrm",
    "UserOrm",
    "DeckInfo",
    "ResourceInfo",
    "PoseInfo",
    "DeckStateResponse",
    "DeckUpdateMessage",
    "ProtocolStartRequest",
    "ProtocolStatus",
    "ProtocolDirectories",
    "ProtocolPrepareRequest",
    "ProtocolInfo",
    "UIHint",
    "ParameterMetadataModel",
    "AssetRequirementModel",
    "ResourceInventoryDataIn",
    "ResourceInventoryDataOut",
    "ResourceInventoryReagentItem",
    "ResourceInventoryItemCount",
    "ProtocolParameters",
    "FunctionProtocolDefinitionModel",
    "ResourceDefinitionBase",
    "ResourceDefinitionCreate",
    "ResourceDefinitionUpdate",
    "ResourceDefinitionResponse",
    "ResourceInstanceCreate",
    "ResourceInstanceUpdate",
    "ResourceInstanceResponse",
    "ResourceInstanceSharedFields",
    "DeckLayoutBase",
    "DeckLayoutCreate",
    "DeckLayoutUpdate",
    "DeckLayoutResponse",
    "DeckPoseDefinitionBase",
    "DeckPoseDefinitionCreate",
    "DeckPoseDefinitionUpdate",
    "DeckPoseDefinitionResponse",
    "DeckPoseItemBase",
    "DeckPoseItemCreate",
    "DeckPoseItemResponse",
    "DeckTypeDefinitionBase",
    "DeckTypeDefinitionCreate",
    "DeckTypeDefinitionUpdate",
    "DeckTypeDefinitionResponse",
    "MachineBase",
    "MachineCreate",
    "MachineUpdate",
    "MachineResponse",
    "MachineCreationRequest",
    "MachineTypeInfo",
    "MachineCategoryEnum",
    "DeckConfigurationOrm",
    "DeckConfigurationPoseItemOrm",
    "DeckPoseDefinitionOrm",
    "DeckTypeDefinitionOrm",
    "AssetBase",
    "AssetResponse",
]
