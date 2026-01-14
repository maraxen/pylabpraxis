"""Base class for services that manage PLR type definitions."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from praxis.backend.models.domain.machine import (
  MachineDefinitionCreate as PLRTypeDefinitionCreate,
)
from praxis.backend.models.domain.machine import (
  MachineDefinitionUpdate as PLRTypeDefinitionUpdate,
)
from praxis.backend.models.domain.plr_sync import (
  PLRTypeDefinitionBase as PLRTypeDefinitionModel,
)

ModelType = TypeVar("ModelType", bound=PLRTypeDefinitionModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PLRTypeDefinitionCreate)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PLRTypeDefinitionUpdate)


class DiscoverableTypeServiceBase(
  ABC,
  Generic[ModelType, CreateSchemaType, UpdateSchemaType],
):
  """An abstract base class for services that handle discoverable pylabrobot type definitions."""

  @property
  @abstractmethod
  def _orm_model(self) -> type[ModelType]:
    """The SQLAlchemy ORM model for the type definition."""

  @abstractmethod
  async def discover_and_synchronize_type_definitions(self) -> list[ModelType]:
    """Discovers all type definitions from pylabrobot and synchronizes them with the database."""
