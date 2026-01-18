"""Machine Frontend Definition model - represents abstract machine interfaces."""

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums import MachineCategoryEnum
from praxis.backend.utils.db import JsonVariant

if TYPE_CHECKING:
  from praxis.backend.models.domain.deck import DeckDefinition
  from praxis.backend.models.domain.machine_backend import MachineBackendDefinition


class MachineFrontendDefinitionBase(PraxisBase):
  """Base schema for MachineFrontendDefinition - shared fields for create/update/response."""

  fqn: str = Field(
    index=True, unique=True, description="Fully qualified name of the frontend class"
  )
  description: str | None = Field(default=None, description="Description of the machine interface")
  plr_category: str | None = Field(default=None, description="PyLabRobot category")
  machine_category: MachineCategoryEnum | None = Field(
    default=None,
    description="Category of the machine",
  )
  capabilities: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Hardware capabilities (channels, modules)"
  )
  capabilities_config: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="User-configurable capabilities schema"
  )
  has_deck: bool = Field(default=False, description="Whether this machine has a deck")
  manufacturer: str | None = Field(default=None)
  model: str | None = Field(default=None)


class MachineFrontendDefinition(MachineFrontendDefinitionBase, table=True):
  """MachineFrontendDefinition ORM model - catalog of abstract machine interfaces."""

  __tablename__ = "machine_frontend_definitions"
  __table_args__ = (UniqueConstraint("name"),)

  machine_category: MachineCategoryEnum = Field(
    default=MachineCategoryEnum.UNKNOWN,
    sa_column=Column(
      SAEnum(MachineCategoryEnum), default=MachineCategoryEnum.UNKNOWN, nullable=False
    ),
  )

  deck_definition_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Deck definition accession ID",
    foreign_key="deck_definition_catalog.accession_id",
  )

  # Relationships
  deck_definition: Optional["DeckDefinition"] = Relationship()
  compatible_backends: list["MachineBackendDefinition"] = Relationship(back_populates="frontend")


class MachineFrontendDefinitionCreate(MachineFrontendDefinitionBase):
  """Schema for creating a MachineFrontendDefinition."""


class MachineFrontendDefinitionRead(MachineFrontendDefinitionBase):
  """Schema for reading a MachineFrontendDefinition (API response)."""

  accession_id: uuid.UUID


class MachineFrontendDefinitionUpdate(SQLModel):
  """Schema for updating a MachineFrontendDefinition (partial update)."""

  name: str | None = None
  fqn: str | None = None
  description: str | None = None
  plr_category: str | None = None
  machine_category: MachineCategoryEnum | None = None
  capabilities: dict[str, Any] | None = None
  capabilities_config: dict[str, Any] | None = None
  has_deck: bool | None = None
  manufacturer: str | None = None
  model: str | None = None
