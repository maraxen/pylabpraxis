from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.orm import AsyncSession

from praxis.backend.models.orm.plr_sync import PLRTypeDefinitionOrm
from praxis.backend.models.pydantic.plr_sync import (
    PLRTypeDefinitionCreate,
    PLRTypeDefinitionUpdate,
)

ModelType = TypeVar("ModelType", bound=PLRTypeDefinitionOrm)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PLRTypeDefinitionCreate)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PLRTypeDefinitionUpdate)


class DiscoverableTypeServiceBase(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC
):
    """
    An abstract base class for services that handle discoverable pylabrobot type definitions.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    @property
    @abstractmethod
    def _orm_model(self) -> type[ModelType]:
        """The SQLAlchemy ORM model for the type definition."""
        pass

    @abstractmethod
    async def discover_and_synchronize_type_definitions(self) -> list[ModelType]:
        """
        Discovers all type definitions from pylabrobot and synchronizes them with the database.
        """
        pass