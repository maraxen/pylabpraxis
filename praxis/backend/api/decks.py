"""FastAPI router for all deck-related endpoints."""

from fastapi import APIRouter

from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.orm.deck import DeckDefinitionOrm, DeckOrm
from praxis.backend.models.pydantic.deck import (
    DeckCreate,
    DeckResponse,
    DeckTypeDefinitionCreate,
    DeckTypeDefinitionResponse,
    DeckTypeDefinitionUpdate,
    DeckUpdate,
)
from praxis.backend.services.deck import DeckService
from praxis.backend.services.deck_type_definition import DeckTypeDefinitionCRUDService

router = APIRouter()

router.include_router(
    create_crud_router(
        service=DeckService(DeckOrm),
        prefix="/",
        tags=["Decks"],
        create_schema=DeckCreate,
        update_schema=DeckUpdate,
        response_schema=DeckResponse,
    )
)

router.include_router(
    create_crud_router(
        service=DeckTypeDefinitionCRUDService(DeckDefinitionOrm),
        prefix="/types",
        tags=["Deck Type Definitions"],
        create_schema=DeckTypeDefinitionCreate,
        update_schema=DeckTypeDefinitionUpdate,
        response_schema=DeckTypeDefinitionResponse,
    )
)