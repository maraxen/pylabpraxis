"""Pydantic models for PyLabRobot type definitions."""

import uuid

from pydantic import BaseModel


class PLRTypeDefinitionBase(BaseModel):
  """Base model for a PyLabRobot type definition."""

  name: str
  fqn: str
  description: str | None = None
  plr_category: str | None = None


class PLRTypeDefinitionCreate(PLRTypeDefinitionBase):
  """Model for creating a new PyLabRobot type definition."""


class PLRTypeDefinitionUpdate(PLRTypeDefinitionBase):
  """Model for updating a PyLabRobot type definition."""


class PLRTypeDefinition(PLRTypeDefinitionBase):
  """Model for a PyLabRobot type definition."""

  accession_id: uuid.UUID

  class Config:
    from_attributes = True
