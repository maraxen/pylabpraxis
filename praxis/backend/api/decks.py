"""FastAPI router for all deck-related endpoints."""

from functools import partial
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.dependencies import get_db
from praxis.backend.models import (
  DeckCreate,
  DeckResponse,
  DeckTypeDefinitionCreate,
  DeckTypeDefinitionResponse,
  DeckTypeDefinitionUpdate,
  DeckUpdate,
  SearchFilters,
)
from praxis.backend.services.deck import deck_service
from praxis.backend.services.deck_type_definition import deck_type_definition_service
from praxis.backend.utils.accession_resolver import get_accession_id_from_accession
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)
router = APIRouter()

log_deck_api_errors = partial(
  log_async_runtime_errors, logger_instance=logger, raises_exception=PraxisAPIError,
)

# --- Deck Type Definition Endpoints ---
deck_type_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=deck_type_definition_service.get,
  get_by_name_func=deck_type_definition_service.get_by_name,
  entity_type_name="Deck Type Definition",
)


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create deck type definition: ",
)
@router.post(
  "/types",
  response_model=DeckTypeDefinitionResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Deck Type Definitions"],
)
async def create_deck_type_definition_endpoint(
  request: DeckTypeDefinitionCreate, db: AsyncSession = Depends(get_db),
):
  """Create a new deck type definition."""
  try:
    return await deck_type_definition_service.create(db=db, obj_in=request)
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list deck type definitions: ",
)
@router.get(
  "/types",
  response_model=list[DeckTypeDefinitionResponse],
  tags=["Deck Type Definitions"],
)
async def read_deck_type_definitions_endpoint(
  db: AsyncSession = Depends(get_db), limit: int = 100, offset: int = 0,
):
  """List all available deck type definitions."""
  return await deck_type_definition_service.get_multi(
      db, filters=SearchFilters(limit=limit, offset=offset),
  )


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get deck type definition: ",
)
@router.get(
  "/types/{accession}",
  response_model=DeckTypeDefinitionResponse,
  tags=["Deck Type Definitions"],
)
async def read_deck_type_definition_endpoint(
  accession: str | UUID, db: AsyncSession = Depends(get_db),
):
  """Retrieve a deck type definition by its ID (UUID) or fully-qualified name."""
  deck_type_definition_accession_id = await deck_type_accession_resolver(
    accession=accession, db=db,
  )
  db_def = await deck_type_definition_service.get(
      db, id=deck_type_definition_accession_id,
  )
  if db_def is None:
    raise HTTPException(status_code=404, detail="Deck type definition not found")
  return db_def


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update deck type definition: ",
)
@router.put(
  "/types/{accession}",
  response_model=DeckTypeDefinitionResponse,
  tags=["Deck Type Definitions"],
)
async def update_deck_type_definition_endpoint(
  accession: str,
  request: DeckTypeDefinitionUpdate,
  db: AsyncSession = Depends(get_db),
):
  """Update an existing deck type definition."""
  deck_type_definition_accession_id = await deck_type_accession_resolver(
    accession=accession, db=db,
  )
  db_obj = await deck_type_definition_service.get(
      db, id=deck_type_definition_accession_id,
  )
  if not db_obj:
      raise HTTPException(
          status_code=404,
          detail=f"Deck type definition '{accession}' not found.",
      )
  try:
    updated_def = await deck_type_definition_service.update(
      db=db,
      db_obj=db_obj,
      obj_in=request,
    )
    return updated_def
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete deck type definition: ",
)
@router.delete(
  "/types/{accession}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Deck Type Definitions"],
)
async def delete_deck_type_definition_endpoint(
  accession: str | UUID, db: AsyncSession = Depends(get_db),
):
  """Delete a deck type definition."""
  deck_type_definition_accession_id = await deck_type_accession_resolver(
    accession=accession, db=db,
  )
  if not await deck_type_definition_service.remove(
      db, id=deck_type_definition_accession_id,
  ):
    raise HTTPException(
      status_code=404,
      detail=f"Deck type definition '{accession}' not found.",
    )


# --- Deck Endpoints ---
deck_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=deck_service.get,
  get_by_name_func=deck_service.get_by_name,
  entity_type_name="Deck",
)


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create deck: ",
)
@router.post(
  "/",
  response_model=DeckResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Decks"],
)
async def create_deck_endpoint(request: DeckCreate, db: AsyncSession = Depends(get_db)):
  """Create a new deck."""
  try:
    return await deck_service.create(db=db, obj_in=request)
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list decks: ",
)
@router.get("/", response_model=list[DeckResponse], tags=["Decks"])
async def read_decks_endpoint(
  db: AsyncSession = Depends(get_db),
  filters: SearchFilters = Depends(),
):
  """List all decks."""
  return await deck_service.get_multi(db, filters=filters)


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get deck: ",
)
@router.get(
  "/{accession}",
  response_model=DeckResponse,
  tags=["Decks"],
)
async def read_deck_endpoint(accession: str | UUID, db: AsyncSession = Depends(get_db)):
  """Retrieve a deck by its ID (UUID) or name."""
  deck_accession_id = await deck_accession_resolver(accession=accession, db=db)
  deck = await deck_service.get(db, id=deck_accession_id)

  if not deck:
    raise HTTPException(status_code=404, detail="Deck not found")
  return deck


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update deck: ",
)
@router.put(
  "/{accession}",
  response_model=DeckResponse,
  tags=["Decks"],
)
async def update_deck_endpoint(
  accession: str | UUID, request: DeckUpdate, db: AsyncSession = Depends(get_db),
):
  """Update an existing deck."""
  try:
    deck_accession_id = await deck_accession_resolver(accession=accession, db=db)
    db_obj = await deck_service.get(db, id=deck_accession_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Deck not found")
    updated_deck = await deck_service.update(
      db=db, db_obj=db_obj, obj_in=request,
    )
    return updated_deck
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete deck: ",
)
@router.delete(
  "/{accession}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Decks"],
)
async def delete_deck_endpoint(
  accession: str | UUID, db: AsyncSession = Depends(get_db),
):
  """Delete a deck."""
  deck_accession_id = await deck_accession_resolver(accession=accession, db=db)
  if not await deck_service.remove(db, id=deck_accession_id):
    raise HTTPException(status_code=404, detail="Deck not found")
