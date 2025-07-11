"""Pydantic models for PyLabRobot type definitions."""

from pydantic import BaseModel

from .pydantic_base import PraxisBaseModel


class PLRTypeDefinitionBase(BaseModel):
  """Base model for a PyLabRobot type definition."""

  name: str
  fqn: str
  description: str | None = None
  plr_category: str | None = None


class PLRTypeDefinition(PLRTypeDefinitionBase, PraxisBaseModel):
  """Model for a PyLabRobot type definition."""


class PLRTypeDefinitionResponse(PLRTypeDefinition):
  """Model for API responses for a PyLabRobot type definition."""


class PLRTypeDefinitionCreate(PLRTypeDefinition):
  """Model for creating a new PyLabRobot type definition."""


class PLRTypeDefinitionUpdate(PLRTypeDefinitionBase):
  """Model for updating a PyLabRobot type definition."""
