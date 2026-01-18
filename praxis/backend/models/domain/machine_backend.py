"""Machine Backend Definition model - represents hardware drivers."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums import BackendTypeEnum
from praxis.backend.utils.db import JsonVariant

if TYPE_CHECKING:
  from praxis.backend.models.domain.machine_frontend import MachineFrontendDefinition


class MachineBackendDefinitionBase(PraxisBase):
  """Base schema for MachineBackendDefinition - shared fields."""

  fqn: str = Field(index=True, unique=True, description="Fully qualified name")
  description: str | None = Field(default=None, description="Description of the backend")
  backend_type: BackendTypeEnum = Field(
    default=BackendTypeEnum.REAL_HARDWARE,
    description="Type of backend (hardware, simulator, etc.)",
  )
  connection_config: dict[str, Any] | None = Field(
    default=None,
    sa_type=JsonVariant,
    description="JSON schema for connection parameters",
  )
  manufacturer: str | None = Field(default=None)
  model: str | None = Field(default=None)
  is_deprecated: bool = Field(default=False)


class MachineBackendDefinition(MachineBackendDefinitionBase, table=True):
  """MachineBackendDefinition ORM model - represents hardware drivers."""

  __tablename__ = "machine_backend_definitions"
  __table_args__ = (UniqueConstraint("name"),)

  backend_type: BackendTypeEnum = Field(
    default=BackendTypeEnum.REAL_HARDWARE,
    sa_column=Column(
      SAEnum(BackendTypeEnum), default=BackendTypeEnum.REAL_HARDWARE, nullable=False
    ),
  )

  frontend_definition_accession_id: uuid.UUID = Field(
    foreign_key="machine_frontend_definitions.accession_id",
    description="Reference to the machine frontend definition",
  )

  frontend: "MachineFrontendDefinition" = Relationship(back_populates="compatible_backends")


class MachineBackendDefinitionCreate(MachineBackendDefinitionBase):
  """Schema for creating a MachineBackendDefinition."""

  frontend_definition_accession_id: uuid.UUID


class MachineBackendDefinitionRead(MachineBackendDefinitionBase):
  """Schema for reading a MachineBackendDefinition (API response)."""

  accession_id: uuid.UUID
  frontend_definition_accession_id: uuid.UUID


class MachineBackendDefinitionUpdate(SQLModel):
  """Schema for updating a MachineBackendDefinition (partial update)."""

  name: str | None = None
  fqn: str | None = None
  description: str | None = None
  backend_type: BackendTypeEnum | None = None
  connection_config: dict[str, Any] | None = None
  manufacturer: str | None = None
  model: str | None = None
  is_deprecated: bool | None = None
  frontend_definition_accession_id: uuid.UUID | None = None
