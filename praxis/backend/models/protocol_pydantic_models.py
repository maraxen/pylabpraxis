"""Pydantic models for protocol management and execution in the Praxis application.

These models facilitate the definition, preparation, and execution of protocols,
including requests to start a run, status updates, and detailed metadata
about protocol parameters and required assets.

Models included:
- ProtocolStartRequest
- ProtocolStatus
- ProtocolDirectories
- ProtocolPrepareRequest
- ProtocolInfo
- UIHint
- ParameterConstraintsModel
- ParameterMetadataModel
- AssetConstraintsModel
- AssetRequirementModel
- FunctionProtocolDefinitionModel
- ProtocolParameters
"""

import uuid
from typing import TYPE_CHECKING, Any

from pydantic import UUID7, BaseModel
from pydantic.fields import Field

if TYPE_CHECKING:
  from .protocol_definitions_orm import AssetDefinitionOrm


class ProtocolStartRequest(BaseModel):
  """Represents a request to start a protocol run.

  This includes details about the protocol to be run, its parameters,
  asset assignments, and configuration data.
  """

  protocol_class: str
  name: str
  description: str | None = None
  parameters: dict[str, Any] | None = None
  assets: dict[str, str] | None = None
  deck_instance: str | None = None
  workcell_accession_id: UUID7 | None = None
  protocol_definition_accession_id: UUID7 | None = None
  config_data: dict[str, Any]
  kwargs: dict[str, Any] | None = None


class ProtocolStatus(BaseModel):
  """Provides a simple status update for a protocol."""

  name: str
  status: str


class ProtocolDirectories(BaseModel):
  """Lists directories associated with protocols."""

  directories: list[str]


class ProtocolPrepareRequest(BaseModel):
  """Represents a request to prepare a protocol for execution.

  This includes the protocol's path or ID, along with any necessary
  parameters and asset assignments.
  """

  protocol_path: str
  parameters: dict[str, Any] | None = None
  asset_assignments: dict[str, str] | None = None


class ProtocolInfo(BaseModel):
  """Provides essential information about a protocol.

  This includes its name, source path, description, and whether it has
  parameters or assets, along with version and database ID.
  """

  name: str
  path: str
  description: str
  has_assets: bool | None = False
  has_parameters: bool | None = False
  version: str | None = None
  protocol_definition_accession_id: UUID7 | None = None


class UIHint(BaseModel):
  """Provides hints for parameter/asset rendering in a user interface."""

  widget_type: str | None = None


class ParameterConstraintsModel(BaseModel):
  """Defines validation constraints for a protocol parameter."""

  min_value: int | float | None = None
  max_value: int | float | None = None
  min_length: int | None = None
  max_length: int | None = None
  regex_pattern: str | None = None
  options: list[Any] | None = None

  class Config:
    """Pydantic configuration for ParameterConstraintsModel."""

    from_attributes = True
    validate_assignment = True


class ParameterMetadataModel(BaseModel):
  """Provides comprehensive metadata for a protocol parameter.

  This includes its name, type information, default value, description,
  constraints, and UI rendering hints.
  """

  name: str
  type_hint: str
  fqn: str
  is_deck_param: bool = False
  optional: bool
  default_value_repr: str | None = None
  description: str | None = None
  constraints: ParameterConstraintsModel = Field(
    default_factory=ParameterConstraintsModel,
  )
  ui_hint: UIHint = Field(default_factory=UIHint)


class LocationConstraintsModel(BaseModel):
  """Defines constraints for the location of an asset in a protocol.

  This includes required locations, optional locations, and any specific
  location-related constraints.
  """

  location_requirements: list[str] = Field(default_factory=list)
  on_resource_type: str = Field(default="")
  stack: bool = Field(default=False)
  directly_position: bool = Field(default=False)
  position_condition: list[str] = Field(default_factory=list)

  class Config:
    """Pydantic configuration for LocationConstraintsModel."""

    from_attributes = True
    validate_assignment = True


class AssetConstraintsModel(BaseModel):
  """Defines constraints for an asset required by a protocol."""

  required_methods: list[str] = Field(default_factory=list)
  required_attributes: list[str] = Field(default_factory=list)
  required_method_signatures: dict[str, str] = Field(default_factory=dict)
  required_method_args: dict[str, list[str]] = Field(default_factory=dict)


class AssetRequirementModel(BaseModel):
  """Describes a single asset required by a protocol.

  This includes its name, type information, optionality, default value,
  description, and specific constraints.
  """

  accession_id: UUID7
  name: str  # type: ignore
  fqn: str
  optional: bool = False
  default_value_repr: str | None = None
  description: str | None = None
  constraints: AssetConstraintsModel = Field(default_factory=AssetConstraintsModel)
  location_constraints: LocationConstraintsModel = Field(
    default_factory=LocationConstraintsModel,
  )


class RuntimeAssetRequirement:
  """Represents a specific asset requirement for a *protocol run*.

  This wraps the static AssetRequirementModel definition with runtime details
  like its specific 'type' for the run (e.g., 'asset', 'deck') and a reservation ID.
  """

  def __init__(
    self,
    asset_definition: AssetRequirementModel,  # The static asset definition
    asset_type: str,  # e.g., "asset", "deck"
    estimated_duration_ms: int | None = None,
    priority: int = 1,
  ):
    """Initialize a RuntimeAssetRequirement."""
    self.asset_definition = asset_definition
    self.asset_type = asset_type
    self.asset_fqn = asset_definition.fqn
    self.estimated_duration_ms = estimated_duration_ms
    self.priority = priority
    self.reservation_id: uuid.UUID | None = None

  @property
  def asset_name(self) -> str:
    """Get the asset name from the underlying definition."""
    return self.asset_definition.name

  @property
  def constraints(self) -> AssetConstraintsModel | None:
    """Get the asset constraints from the underlying definition."""
    return self.asset_definition.constraints

  @property
  def location_constraints(self) -> LocationConstraintsModel | None:
    """Get the location constraints from the underlying definition."""
    return self.asset_definition.location_constraints

  def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for serialization."""
    return {
      "asset_name": self.asset_name,
      "asset_type": self.asset_type,
      "asset_fqn": self.asset_fqn,
      "estimated_duration_ms": self.estimated_duration_ms,
      "priority": self.priority,
      "reservation_id": str(self.reservation_id) if self.reservation_id else None,
      "constraints": self.constraints.model_dump() if self.constraints else None,
      "location_constraints": (
        self.location_constraints.model_dump() if self.location_constraints else None
      ),
    }

  @classmethod
  def from_asset_definition_orm(
    cls,
    asset_def_orm: "AssetDefinitionOrm",
    asset_type: str = "asset",
    estimated_duration_ms: int | None = None,
    priority: int = 1,
  ) -> "RuntimeAssetRequirement":
    """Create a RuntimeAssetRequirement from AssetDefinitionOrm.

    This provides a bridge between the ORM model and the runtime requirement.
    """
    # Convert ORM to AssetRequirementModel
    asset_requirement = AssetRequirementModel(
      accession_id=asset_def_orm.accession_id,
      name=asset_def_orm.name,  # type: ignore
      fqn=asset_def_orm.fqn,
      optional=asset_def_orm.optional,
      default_value_repr=asset_def_orm.default_value_repr,
      description=asset_def_orm.description,
      constraints=AssetConstraintsModel(**(asset_def_orm.constraints_json or {})),
      location_constraints=LocationConstraintsModel(),
    )

    return cls(
      asset_definition=asset_requirement,
      asset_type=asset_type,
      estimated_duration_ms=estimated_duration_ms,
      priority=priority,
    )


class FunctionProtocolDefinitionModel(BaseModel):
  """Represents a detailed definition of a function-based protocol.

  This model encapsulates core definition details, source information,
  execution behavior, categorization, and inferred parameters and assets.
  """

  accession_id: uuid.UUID
  name: str
  version: str = "0.1.0"
  description: str | None = None

  source_file_path: str
  module_name: str
  function_name: str

  source_repository_name: str | None = None
  commit_hash: str | None = None
  file_system_source_name: str | None = None

  is_top_level: bool = False
  solo_execution: bool = False
  preconfigure_deck: bool = False
  deck_param_name: str | None = None
  deck_construction_function_fqn: str | None = (
    None  # New field for deck construction callable
  )
  state_param_name: str | None = "state"

  category: str | None = None
  tags: list[str] = Field(default_factory=list)
  deprecated: bool = False

  parameters: list[ParameterMetadataModel] = Field(default_factory=list)
  assets: list[AssetRequirementModel] = Field(default_factory=list)

  class Config:
    """Pydantic configuration for FunctionProtocolDefinitionModel."""

    from_attributes = True
    validate_assignment = True


class ProtocolParameters(BaseModel):
  """Represents the parameters for a protocol run.

  This includes both user-defined parameters, derived from the protocol's
  function signature, and system-generated parameters that might be
  used internally for logging or tracking.
  """

  user_parameters: dict[str, ParameterMetadataModel] = Field(default_factory=dict)
  system_parameters: dict[str, ParameterMetadataModel] = Field(default_factory=dict)

  class Config:
    """Pydantic configuration for ProtocolParameters."""

    from_attributes = True
    validate_assignment = True
