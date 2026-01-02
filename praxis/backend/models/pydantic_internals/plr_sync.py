"""Pydantic models for PyLabRobot type definitions."""

from pydantic import BaseModel, ConfigDict

from .pydantic_base import PraxisBaseModel


class PLRTypeDefinitionBase(BaseModel):
  """Base model for a PyLabRobot type definition."""

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  fqn: str
  name: str
  description: str | None = None
  plr_category: str | None = None


class PLRTypeDefinition(PLRTypeDefinitionBase):
  """Model for a PyLabRobot type definition."""


class PLRTypeDefinitionResponse(PLRTypeDefinition, PraxisBaseModel):
  """Model for API responses for a PyLabRobot type definition."""


class PLRTypeDefinitionCreate(PLRTypeDefinitionBase):
  """Model for creating a new PyLabRobot type definition."""


class PLRTypeDefinitionUpdate(BaseModel):
  """Model for updating a PyLabRobot type definition."""

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  fqn: str | None = None
  name: str | None = None
  description: str | None = None
  plr_category: str | None = None
