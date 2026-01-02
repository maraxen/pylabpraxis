"""Base ORM model for PyLabRobot type definitions."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from praxis.backend.utils.db import Base


class PLRTypeDefinitionOrm(Base):
  """Base ORM model for a PyLabRobot type definition.

  This is an abstract class that provides common columns for ORM models
  representing PyLabRobot type definitions (e.g., Decks, Resources, Machines).
  """

  __abstract__ = True

  fqn: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    unique=True,
    comment="Fully qualified name of the PyLabRobot class.",
    kw_only=True,
  )
  name: Mapped[str] = mapped_column(
    String,
    unique=False,  # Multiple PLR resources can have the same short name (e.g., Plate)
    index=True,
    nullable=False,
    comment="Human-readable name for the type definition. Not unique since fqn is the unique identifier.",
    kw_only=True,
  )
  description: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="Detailed description of the type.",
    default=None,
  )
  plr_category: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="Category of the type in PyLabRobot (e.g., 'Deck', 'LiquidHandler').",
    default=None,
  )

  def __repr__(self) -> str:
    """Return a string representation of the PLRTypeDefinitionOrm object."""
    return f"<{self.__class__.__name__}(accession_id={self.accession_id}, name={self.name})>"
