"""Pydantic models for PyLabRobot type definitions."""


from .pydantic_base import PraxisBaseModel


class PLRTypeDefinitionBase(PraxisBaseModel):

  """Base model for a PyLabRobot type definition."""

  fqn: str
  description: str | None = None
  plr_category: str | None = None


class PLRTypeDefinition(PLRTypeDefinitionBase):

  """Model for a PyLabRobot type definition."""


class PLRTypeDefinitionResponse(PLRTypeDefinition):

  """Model for API responses for a PyLabRobot type definition."""


class PLRTypeDefinitionCreate(PLRTypeDefinitionBase):

  """Model for creating a new PyLabRobot type definition."""


class PLRTypeDefinitionUpdate(PraxisBaseModel):

  """Model for updating a PyLabRobot type definition."""

  fqn: str | None = None
  description: str | None = None
  plr_category: str | None = None
