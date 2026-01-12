"""Unified SQLModel definition for PLRTypeDefinition."""

from sqlmodel import Field

from praxis.backend.models.domain.sqlmodel_base import PraxisBase


class PLRTypeDefinitionBase(PraxisBase):
  """Base schema for PLRTypeDefinition - shared fields."""

  fqn: str = Field(
    index=True, unique=True, description="Fully qualified name of the PyLabRobot class."
  )
  # Name is inherited from PraxisBase but with different semantics in ORM?
  # ORM had: unique=False, index=True, nullable=False. PraxisBase has index=True.
  # We should be fine.

  description: str | None = Field(default=None, description="Detailed description of the type.")
  plr_category: str | None = Field(
    default=None, description="Category of the type in PyLabRobot (e.g., 'Deck', 'LiquidHandler')."
  )

  def __repr__(self) -> str:
    """Return a string representation of the PLRTypeDefinition object."""
    return f"<{self.__class__.__name__}(accession_id={self.accession_id}, name={self.name})>"


class PLRTypeDefinition(PLRTypeDefinitionBase):
  """PLRTypeDefinition domain schema (Abstract/Mixin).

  This is not a table itself but a shape used by synchronizers.
  """

  pass
