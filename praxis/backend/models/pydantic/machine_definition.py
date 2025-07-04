"""Pydantic models for managing machine definitions in the Praxis application.

These models define the structure for requests and responses related to
machine definitions, including their creation, retrieval, and updates,
enabling robust data validation and serialization for API interactions.
"""

from typing import Any

from pydantic import UUID7, BaseModel, Field

from praxis.backend.models.enums import MachineCategoryEnum
from praxis.backend.models.pydantic.pydantic_base import PraxisBaseModel


class MachineDefinitionBase(BaseModel):
  """Defines the base properties for a machine definition."""

  name: str = Field(description="The unique name of the machine definition.")
  fqn: str = Field(description="The fully qualified name of the machine class.")
  machine_category: MachineCategoryEnum = Field(description="The category of the machine.")
  description: str | None = Field(None, description="A description of the machine definition.")
  is_consumable: bool = Field(False, description="Whether the machine is a consumable.")
  nominal_volume_ul: float | None = Field(None, description="The nominal volume in microliters.")
  material: str | None = Field(None, description="The material of the machine.")
  manufacturer: str | None = Field(None, description="The manufacturer of the machine.")
  plr_definition_details_json: dict[str, Any] | None = Field(
    None, description="PyLabRobot specific definition details."
  )
  size_x_mm: float | None = Field(None, description="The size in the x-dimension in millimeters.")
  size_y_mm: float | None = Field(None, description="The size in the y-dimension in millimeters.")
  size_z_mm: float | None = Field(None, description="The size in the z-dimension in millimeters.")
  plr_category: str | None = Field(None, description="The PyLabRobot category.")
  model: str | None = Field(None, description="The model of the machine.")
  rotation_json: dict[str, Any] | None = Field(None, description="The rotation of the machine.")
  is_machine: bool = Field(True, description="Whether this is a machine.")
  resource_definition_accession_id: UUID7 | None = Field(
    None, description="The accession ID of the resource definition."
  )
  has_deck: bool = Field(False, description="Whether the machine has a deck.")
  deck_definition_accession_id: UUID7 | None = Field(
    None, description="The accession ID of the deck definition."
  )
  setup_method_json: dict[str, Any] | None = Field(
    None, description="The setup method for the machine."
  )


class MachineDefinitionCreate(MachineDefinitionBase):
  """Represents a machine definition for creation requests."""


class MachineDefinitionUpdate(BaseModel):
  """Specifies the fields that can be updated for an existing machine definition."""

  name: str | None = Field(None, description="The new unique name of the machine definition.")
  fqn: str | None = Field(None, description="The new fully qualified name of the machine class.")
  machine_category: MachineCategoryEnum | None = Field(
    None, description="The new category of the machine."
  )
  description: str | None = Field(None, description="The new description of the machine definition.")
  is_consumable: bool | None = Field(None, description="Whether the machine is a consumable.")
  nominal_volume_ul: float | None = Field(None, description="The new nominal volume in microliters.")
  material: str | None = Field(None, description="The new material of the machine.")
  manufacturer: str | None = Field(None, description="The new manufacturer of the machine.")
  plr_definition_details_json: dict[str, Any] | None = Field(
    None, description="New PyLabRobot specific definition details."
  )
  size_x_mm: float | None = Field(
    None, description="The new size in the x-dimension in millimeters."
  )
  size_y_mm: float | None = Field(
    None, description="The new size in the y-dimension in millimeters."
  )
  size_z_mm: float | None = Field(
    None, description="The new size in the z-dimension in millimeters."
  )
  plr_category: str | None = Field(None, description="The new PyLabRobot category.")
  model: str | None = Field(None, description="The new model of the machine.")
  rotation_json: dict[str, Any] | None = Field(None, description="The new rotation of the machine.")
  is_machine: bool | None = Field(None, description="Whether this is a machine.")
  resource_definition_accession_id: UUID7 | None = Field(
    None, description="The new accession ID of the resource definition."
  )
  has_deck: bool | None = Field(None, description="Whether the machine has a deck.")
  deck_definition_accession_id: UUID7 | None = Field(
    None, description="The new accession ID of the deck definition."
  )
  setup_method_json: dict[str, Any] | None = Field(
    None, description="The new setup method for the machine."
  )


class MachineDefinitionResponse(MachineDefinitionBase, PraxisBaseModel):
  """Represents a machine definition for API responses."""

  class Config(PraxisBaseModel.Config):
    """Pydantic configuration for MachineDefinitionResponse."""
