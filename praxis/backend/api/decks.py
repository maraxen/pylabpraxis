# <filename>praxis/backend/api/decks.py</filename>
#
# This file contains the FastAPI router for all deck-related endpoints,
# including deck type definitions and deck instanceurations.

from functools import partial
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import UUID

# Import the service layer, aliased as 'svc' for convenience
import praxis.backend.services as svc

# Import dependencies from the local 'api' package
from praxis.backend.api.dependencies import get_db

# Import all necessary Pydantic models from the central models package
from praxis.backend.models import (
  DeckCreate,
  DeckPositionDefinitionCreate,
  DeckPositionDefinitionResponse,
  DeckPositionDefinitionUpdate,
  DeckPositionResourceCreate,
  DeckPositionResourceResponse,
  DeckResponse,
  DeckTypeDefinitionCreate,
  DeckTypeDefinitionResponse,
  DeckTypeDefinitionUpdate,
  DeckUpdate,
)
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)
router = APIRouter()

log_deck_api_errors = partial(
  log_async_runtime_errors, logger_instance=logger, raises_exception=PraxisAPIError
)

# --- Deck Type Definition Endpoints ---


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
async def create_deck_type_definition(
  request: DeckTypeDefinitionCreate, db: AsyncSession = Depends(get_db)
):
  """Create a new deck type definition."""
  try:
    return await svc.create_or_update_deck_type_definition(
      db=db, **request.model_dump()
    )
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list deck type definitions: ",
)
@router.get(
  "/types",
  response_model=List[DeckTypeDefinitionResponse],
  tags=["Deck Type Definitions"],
)
async def list_deck_type_definitions(
  db: AsyncSession = Depends(get_db), limit: int = 100, offset: int = 0
):
  """List all available deck type definitions."""
  return await svc.list_deck_type_definitions(db, limit=limit, offset=offset)


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
async def get_deck_type_definition(
  accession: str | UUID, db: AsyncSession = Depends(get_db)
):
  """Retrieve a deck type definition by its ID (UUID) or fully-qualified name (FQN)."""
  if isinstance(accession, UUID):
    db_def = await svc.get_deck_type_definition(db, accession)
  else:
    db_def = await svc.get_deck_type_definition_by_fqn(db, accession)

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
async def update_deck_type_definition(
  accession: str,
  request: DeckTypeDefinitionUpdate,
  db: AsyncSession = Depends(get_db),
):
  """Update an existing deck type definition."""
  update_data = request.model_dump(exclude_unset=True)
  try:
    updated_def = await svc.create_or_update_deck_type_definition(
      db=db, deck_type=accession, **update_data
    )
    if not updated_def:
      raise HTTPException(
        status_code=404, detail=f"Deck type definition '{accession}' not found."
      )
    return updated_def
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- Deck Configuration Endpoints ---


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create deck instanceuration: ",
)
@router.post(
  "/configurations",
  response_model=DeckResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Deck Configurations"],
)
async def create_deck_instance(request: DeckCreate, db: AsyncSession = Depends(get_db)):
  """Create a new deck instanceuration."""
  try:
    return await svc.create_deck_config(db=db, **request.model_dump())
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list deck instanceurations: ",
)
@router.get(
  "/configurations", response_model=List[DeckResponse], tags=["Deck Configurations"]
)
async def list_deck_instances(
  db: AsyncSession = Depends(get_db), limit: int = 100, offset: int = 0
):
  """List all deck instanceurations."""
  return await svc.list_deck_configs(db, limit=limit, offset=offset)


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get deck instanceuration: ",
)
@router.get(
  "/configurations/{accession}",
  response_model=DeckResponse,
  tags=["Deck Configurations"],
)
async def get_deck_instance(accession: str | UUID, db: AsyncSession = Depends(get_db)):
  """Retrieve a deck instanceuration by its ID (UUID) or name."""
  if isinstance(accession, UUID):
    deck = await svc.read_deck_instance(db, accession)
  else:
    deck = await svc.get_deck_config_by_name(db, accession)

  if not deck:
    raise HTTPException(status_code=404, detail="Deck configuration not found")
  return deck


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update deck instanceuration: ",
)
@router.put(
  "/configurations/{accession}",
  response_model=DeckResponse,
  tags=["Deck Configurations"],
)
async def update_deck_instance(
  accession: str | UUID, request: DeckUpdate, db: AsyncSession = Depends(get_db)
):
  """Update an existing deck instanceuration."""
  update_data = request.model_dump(exclude_unset=True)
  try:
    if not isinstance(accession, UUID) and isinstance(accession, str):
      deck = await svc.get_deck_config_by_name(db, accession)
      if not deck:
        raise HTTPException(status_code=404, detail="Deck configuration not found")
      accession = deck.id  # Convert name to UUID for update
    updated_deck = await svc.update_deck_config(db=db, deck_id=accession, **update_data)
    if not updated_deck:
      raise HTTPException(status_code=404, detail="Deck configuration not found")
    return updated_deck
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete deck instanceuration: ",
)
@router.delete(
  "/configurations/{accession}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Deck Configurations"],
)
async def delete_deck_instance(
  accession: str | UUID, db: AsyncSession = Depends(get_db)
):
  """Delete a deck instanceuration."""
  if isinstance(accession, str) and not isinstance(accession, UUID):
    deck = await svc.get_deck_config_by_name(db, accession)
    if not deck:
      raise HTTPException(status_code=404, detail="Deck configuration not found")
    accession = deck.id  # Convert name to UUID for deletion
  if not await svc.delete_deck_config(db, accession):
    raise HTTPException(status_code=404, detail="Deck configuration not found")
  return None


# --- Deck Configuration Position Item Endpoints ---


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create item in deck instanceuration: ",
)
@router.post(
  "/configurations/{config_accession}/positions",
  response_model=DeckPositionResourceResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Deck Configurations"],
)
async def create_deck_instance_position_item(
  config_accession: str | UUID,
  request: DeckPositionResourceCreate,
  db: AsyncSession = Depends(get_db),
):
  """Add a resource item to a position in a deck instanceuration."""
  try:
    return await svc.create_deck_position_item(
      db, config_accession, **request.model_dump()
    )
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update item in deck instanceuration: ",
)
@router.put(
  "/configurations/{config_accession}/positions/{item_id}",
  response_model=DeckPositionResourceResponse,
  tags=["Deck Configurations"],
)
async def update_deck_instance_position_item(
  item_id: UUID, request: DeckPositionResourceCreate, db: AsyncSession = Depends(get_db)
):
  """Update an item in a deck instanceuration position."""
  updated_item = await svc.update_deck_instance_position_item(
    db, item_id, **request.model_dump(exclude_unset=True)
  )
  if not updated_item:
    raise HTTPException(status_code=404, detail="Deck position item not found")
  return updated_item


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete item from deck instanceuration: ",
)
@router.delete(
  "/configurations/{config_accession}/positions/{item_id}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Deck Configurations"],
)
async def delete_deck_instance_position_item(
  item_id: UUID, db: AsyncSession = Depends(get_db)
):
  """Delete an item from a deck instanceuration position."""
  if not await svc.delete_deck_instance_position_item(db, item_id):
    raise HTTPException(status_code=404, detail="Deck position item not found")
  return None


'''

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
async def delete_deck_type_definition(
  accession: str | UUID, db: AsyncSession = Depends(get_db)
):
  """Delete a deck type definition."""
  if not await svc.delete_deck_type_definition(db, accession):
    raise HTTPException(
      status_code=404, detail=f"Deck type definition '{accession}' not found."
    )
  return None

# --- Deck Position Definition Endpoints (within a Type) ---


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create deck position definition: ",
)
@router.post(
  "/types/{type_accession}/positions",
  response_model=DeckPositionDefinitionResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Deck Type Definitions"],
)
async def create_deck_position_definition(
  type_accession: str | UUID,
  request: DeckPositionDefinitionCreate,
  db: AsyncSession = Depends(get_db),
):
  """Add a new position definition to a deck type."""
  try:
    return await svc.create_deck_position_definition(
      db, type_accession, **request.model_dump()
    )
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list deck position definitions: ",
)
@router.get(
  "/types/{type_accession}/positions",
  response_model=List[DeckPositionDefinitionResponse],
  tags=["Deck Type Definitions"],
)
async def list_deck_position_definitions(
  type_accession: str | UUID,
  db: AsyncSession = Depends(get_db),
  limit: int = 100,
  offset: int = 0,
):
  """List all position definitions for a given deck type."""
  return await svc.list_deck_position_definitions(
    db, type_accession, limit=limit, offset=offset
  )


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get deck position definition: ",
)
@router.get(
  "/types/{type_accession}/positions/{position_id}",
  response_model=DeckPositionDefinitionResponse,
  tags=["Deck Type Definitions"],
)
async def read_deck_position_definition(
  type_accession: str | UUID, position_id: UUID, db: AsyncSession = Depends(get_db)
):
  """Retrieve a specific position definition from a deck type."""
  position = await svc.read_deck_position_definition(db, type_accession, position_id)
  if not position:
    raise HTTPException(status_code=404, detail="Position definition not found")
  return position


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update deck position definition: ",
)
@router.put(
  "/types/{type_accession}/positions/{position_id}",
  response_model=DeckPositionDefinitionResponse,
  tags=["Deck Type Definitions"],
)
async def update_deck_position_definition(
  type_accession: str | UUID,
  position_id: UUID,
  request: DeckPositionDefinitionUpdate,
  db: AsyncSession = Depends(get_db),
):
  """Update an existing position definition within a deck type."""
  updated_pos = await svc.update_deck_position_definition(
    db, type_accession, position_id, **request.model_dump(exclude_unset=True)
  )
  if not updated_pos:
    raise HTTPException(status_code=404, detail="Position definition not found")
  return updated_pos


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete deck position definition: ",
)
@router.delete(
  "/types/{type_accession}/positions/{position_id}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Deck Type Definitions"],
)
async def delete_deck_position_definition(
  type_accession: str | UUID, position_id: UUID, db: AsyncSession = Depends(get_db)
):
  """Delete a position definition from a deck type."""
  if not await svc.delete_deck_position_definition(db, type_accession, position_id):
    raise HTTPException(status_code=404, detail="Position definition not found")
  return None
'''
