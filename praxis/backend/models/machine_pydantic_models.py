"""Pydantic models for managing machine assets within the Praxis application.

These models define the structure for requests and responses related to
machine instances, including their creation, retrieval, and updates,
enabling robust data validation and serialization for API interactions.
"""

import datetime
from typing import Any, Dict, List, Optional

from pydantic import UUID7, BaseModel, Field


class MachineTypeInfo(BaseModel):
  """Provides detailed information about a specific machine type.

  This includes its name, parent class, constructor parameters,
  supported backends, documentation string, and module path.
  """

  name: str
  parent_class: str
  constructor_params: Dict[str, Dict]
  backends: List[str]
  doc: str
  module: str


class MachineCreationRequest(BaseModel):
  """Represents a request to create a new machine instance.

  It includes the desired name, machine type, an optional backend,
  description, and specific parameters for machine instantiation.
  """

  name: str
  machineType: str
  backend: Optional[str] = None
  description: Optional[str] = None
  params: Dict[str, Any] = {}


class MachineBase(BaseModel):
  """Defines the base properties for a machine.

  This model captures common attributes for machine instances,
  such as name, category, description, status, and connection information.
  """

  name: str
  machine_category: str
  description: Optional[str] = None
  manufacturer: Optional[str] = None
  model: Optional[str] = None
  serial_number: Optional[str] = None
  installation_date: Optional[datetime.date] = None
  status: Optional[str] = None
  location_description: Optional[str] = None
  connection_info: Optional[Dict[str, Any]] = None
  is_simulation_override: Optional[bool] = None
  custom_fields: Optional[Dict[str, Any]] = None
  is_resource: bool = Field(
    default=False,
    description="Indicates if this machine is also registered as a resource instance.",
  )
  resource_counterpart_id: Optional[UUID7] = Field(
    default=None,
    description="ID of the associated ResourceInstanceOrm if this machine is a \
        resource.",
  )

  class Config:
    """Configuration for Pydantic model behavior."""

    from_attributes = True
    use_enum_values = True


class MachineCreate(MachineBase):
  """Represents a machine for creation requests.

  Extends `MachineBase` by including the PyLabRobot class name
  and an optional link to a `deck_type_definition_id` if the machine
  serves as a deck.
  """

  id: Optional[UUID7] = None
  python_fqn: str
  deck_type_definition_id: Optional[UUID7] = None


class MachineResponse(MachineBase):
  """Represents a machine for API responses.

  Extends `MachineBase` by adding system-generated identifiers,
  the actual PyLabRobot class name used for instantiation,
  and timestamps for creation and last update.
  """

  id: UUID7
  python_fqn: str
  deck_type_definition_id: Optional[int] = None
  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class MachineUpdate(BaseModel):
  """Specifies the fields that can be updated for an existing machine.

  All fields are optional, allowing partial updates. It includes
  common mutable attributes of a machine instance.
  """

  name: Optional[str] = None
  # python_fqn: Optional[str] = None # Typically not updatable
  machine_category: Optional[str] = None
  deck_type_definition_id: Optional[int] = None
  description: Optional[str] = None
  manufacturer: Optional[str] = None
  model: Optional[str] = None
  serial_number: Optional[str] = None
  installation_date: Optional[datetime.date] = None
  status: Optional[str] = None
  location_description: Optional[str] = None
  connection_info: Optional[Dict[str, Any]] = None
  is_simulation_override: Optional[bool] = None
  custom_fields: Optional[Dict[str, Any]] = None
  is_resource: Optional[bool] = Field(
    default=None,
    description="Indicates if this machine is also registered as a resource instance.",
  )
  resource_counterpart_id: Optional[int] = Field(
    default=None,
    description="ID of the associated ResourceInstanceOrm if this machine is a \
      resource.",
  )
