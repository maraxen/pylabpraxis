"""Pydantic models for PyLabRobot type definitions."""

from pydantic import BaseModel, Field
import uuid

class PLRTypeDefinitionBase(BaseModel):
    """Base model for a PyLabRobot type definition."""
    name: str
    fqn: str
    description: str | None = None
    plr_category: str | None = None

class PLRTypeDefinitionCreate(PLRTypeDefinitionBase):
    """Model for creating a new PyLabRobot type definition."""
    pass

class PLRTypeDefinitionUpdate(PLRTypeDefinitionBase):
    """Model for updating a PyLabRobot type definition."""
    pass

class PLRTypeDefinition(PLRTypeDefinitionBase):
    """Model for a PyLabRobot type definition."""
    accession_id: uuid.UUID

    class Config:
        from_attributes = True
