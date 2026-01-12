"""FastAPI router for all deck-related endpoints."""

from fastapi import APIRouter

from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.domain.deck import (
  DeckCreate,
  DeckDefinitionCreate,
  DeckDefinitionRead,
  DeckDefinitionUpdate,
  DeckRead,
  DeckUpdate,
)
from praxis.backend.models.domain.deck import Deck, DeckDefinition
from praxis.backend.services.deck import DeckService
from praxis.backend.services.deck_type_definition import DeckTypeDefinitionService

router = APIRouter()

router.include_router(
  create_crud_router(
    service=DeckService(Deck),
    prefix="/",
    tags=["Decks"],
    create_schema=DeckCreate,
    update_schema=DeckUpdate,
    read_schema=DeckRead,
  ),
)

router.include_router(
  create_crud_router(
    service=DeckTypeDefinitionService(DeckDefinition),
    prefix="/types",
    tags=["Deck Type Definitions"],
    create_schema=DeckDefinitionCreate,
    update_schema=DeckDefinitionUpdate,
    read_schema=DeckDefinitionRead,
  ),
)
