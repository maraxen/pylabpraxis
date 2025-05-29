"""This module imports and re-exports ORM classes and enums for asset management
and protocol definitions. It serves as a single point of access for these models,
allowing other parts of the application to import them easily.
It also includes the necessary imports for Alembic migrations, ensuring that
the database schema is in sync with the ORM models.
"""

from __future__ import annotations


from .asset_management_orm import (
    AssetInstanceOrm,
)

from .machine_orm import MachineOrm, MachineStatusEnum, MachineCategoryEnum

from .resource_orm import (
    ResourceInstanceOrm,
    ResourceDefinitionCatalogOrm,
    ResourceInstanceStatusEnum,
)

from .deck_orm import (
    DeckConfigurationOrm,
    DeckConfigurationSlotItemOrm,
    DeckSlotDefinitionOrm,
    DeckTypeDefinitionOrm,
)

from .protocol_definitions_orm import (
    ProtocolSourceStatusEnum,
    ProtocolRunStatusEnum,
    FunctionCallStatusEnum,
    ProtocolSourceRepositoryOrm,
    FileSystemProtocolSourceOrm,
    FunctionProtocolDefinitionOrm,
    ParameterDefinitionOrm,
    AssetDefinitionOrm,
    ProtocolRunOrm,
    FunctionCallLogOrm,
)

from .user_management_orm import UserOrm

from .protocol_pydantic_models import (
    ProtocolStartRequest,
    ProtocolStatus,
    ProtocolDirectories,
    ProtocolPrepareRequest,
    ProtocolInfo,
    UIHint,
    ParameterMetadataModel,
    AssetRequirementModel,
    ProtocolParameters,
    FunctionProtocolDefinitionModel,
)

from .resource_pydantic_models import (
    ResourceInventoryDataIn,
    ResourceInventoryDataOut,
    ResourceInventoryReagentItem,
    ResourceInventoryItemCount,
    ResourceDefinitionBase,
    ResourceDefinitionCreate,
    ResourceDefinitionUpdate,
    ResourceDefinitionResponse,
    ResourceInstanceCreate,
    ResourceInstanceUpdate,
    ResourceInstanceResponse,
    ResourceInstanceSharedFields,
)

from .deck_pydantic_models import (
    DeckLayoutBase,
    DeckLayoutCreate,
    DeckLayoutUpdate,
    DeckLayoutResponse,
    DeckSlotDefinitionBase,
    DeckSlotDefinitionCreate,
    DeckSlotDefinitionUpdate,
    DeckSlotDefinitionResponse,
    DeckSlotItemBase,
    DeckSlotItemCreate,
    DeckSlotItemResponse,
    DeckTypeDefinitionBase,
    DeckTypeDefinitionCreate,
    DeckTypeDefinitionUpdate,
    DeckTypeDefinitionResponse,
)
from .machine_pydantic_models import (
    MachineBase,
    MachineCreate,
    MachineUpdate,
    MachineResponse,
    MachineCreationRequest,
    MachineTypeInfo,
)
from .workcell_pydantic_models import (
    DeckInfo,
    ResourceInfo,
    SlotInfo,
    DeckStateResponse,
    DeckUpdateMessage,
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
    "SlotInfo",
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
    "DeckSlotDefinitionBase",
    "DeckSlotDefinitionCreate",
    "DeckSlotDefinitionUpdate",
    "DeckSlotDefinitionResponse",
    "DeckSlotItemBase",
    "DeckSlotItemCreate",
    "DeckSlotItemResponse",
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
    "DeckConfigurationSlotItemOrm",
    "DeckSlotDefinitionOrm",
    "DeckTypeDefinitionOrm",
]
