# <filename>praxis/backend/api/decks.py</filename>
#
# This file contains the FastAPI router for all deck-related endpoints,
# including deck type definitions and deck instanceurations.

from functools import partial
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import the service layer, aliased as 'svc' for convenience
import praxis.backend.services as svc

# Import dependencies from the local 'api' package
from praxis.backend.api.dependencies import get_db

# Import all necessary Pydantic models from the central models package
from praxis.backend.models import (
  DeckInstanceCreate,
  DeckInstanceResponse,
  DeckInstanceUpdate,
  DeckPositionResourceCreate,
  DeckPositionResourceResponse,
  DeckTypeDefinitionCreate,
  DeckTypeDefinitionResponse,
  DeckTypeDefinitionUpdate,
)
from praxis.backend.utils.accession_resolver import get_accession_id_from_accession
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)
router = APIRouter()

log_deck_api_errors = partial(
  log_async_runtime_errors, logger_instance=logger, raises_exception=PraxisAPIError
)

# --- Deck Type Definition Endpoints ---
deck_type_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=svc.read_deck_type_definition,
  get_by_name_func=svc.read_deck_type_definition_by_fqn,
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
async def create_deck_type_definition(
  request: DeckTypeDefinitionCreate, db: AsyncSession = Depends(get_db)
):
  """Create a new deck type definition."""
  try:
    return await svc.create_deck_type_definition(db=db, **request.model_dump())
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
async def read_deck_type_definition(
  accession: str | UUID, db: AsyncSession = Depends(get_db)
):
  """Retrieve a deck type definition by its ID (UUID) or fully-qualified name (FQN)."""
  deck_type_definition_accession_id = await deck_type_accession_resolver(
    accession=accession, db=db
  )
  db_def = await svc.read_deck_type_definition(db, deck_type_definition_accession_id)
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
  deck_type_definition_accession_id = await deck_type_accession_resolver(
    accession=accession, db=db
  )
  try:
    updated_def = await svc.update_deck_type_definition(
      db=db,
      deck_type_accession_id=deck_type_definition_accession_id,
      **update_data,
    )
    if not updated_def:
      raise HTTPException(
        status_code=404, detail=f"Deck type definition '{accession}' not found."
      )
    return updated_def
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


deck_instance_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=svc.read_deck_instance,
  get_by_name_func=svc.read_deck_instance_by_name,
  entity_type_name="Deck Instance",
)


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create deck instance: ",
)
@router.post(
  "/instances",
  response_model=DeckInstanceResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Deck Instances"],
)
async def create_deck_instance(
  request: DeckInstanceCreate, db: AsyncSession = Depends(get_db)
):
  """Create a new deck instance."""
  try:
    return await svc.create_deck_instance(db=db, **request.model_dump())
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list deck instances: ",
)
@router.get(
  "/instances", response_model=List[DeckInstanceResponse], tags=["Deck Instances"]
)
async def list_deck_instances(
  db: AsyncSession = Depends(get_db), limit: int = 100, offset: int = 0
):
  """List all deck instances."""
  return await svc.list_deck_instances(db, limit=limit, offset=offset)


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get deck instance: ",
)
@router.get(
  "/instances/{accession}",
  response_model=DeckInstanceResponse,
  tags=["Deck Instances"],
)
async def get_deck_instance(accession: str | UUID, db: AsyncSession = Depends(get_db)):
  """Retrieve a deck instance by its ID (UUID) or name."""
  deck_instance_accession_id = await deck_instance_accession_resolver(
    accession=accession, db=db
  )
  deck = await svc.read_deck_instance(db, deck_instance_accession_id)

  if not deck:
    raise HTTPException(status_code=404, detail="Deck instance not found")
  return deck


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update deck instance: ",
)
@router.put(
  "/instances/{accession}",
  response_model=DeckInstanceResponse,
  tags=["Deck Instances"],
)
async def update_deck_instance(
  accession: str | UUID, request: DeckInstanceUpdate, db: AsyncSession = Depends(get_db)
):
  """Update an existing deck instance."""
  update_data = request.model_dump(exclude_unset=True)
  try:
    deck_instance_accession_id = await deck_instance_accession_resolver(
      accession=accession, db=db
    )
    updated_deck = await svc.update_deck_instance(
      db=db, deck_accession_id=deck_instance_accession_id, **update_data
    )
    if not updated_deck:
      raise HTTPException(status_code=404, detail="Deck instance not found")
    return updated_deck
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete deck instance: ",
)
@router.delete(
  "/instances/{accession}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Deck Instances"],
)
async def delete_deck_instance(
  accession: str | UUID, db: AsyncSession = Depends(get_db)
):
  """Delete a deck instance."""
  deck_instance_accession_id = await deck_instance_accession_resolver(
    accession=accession, db=db
  )
  if not await svc.delete_deck_instance(db, deck_instance_accession_id):
    raise HTTPException(status_code=404, detail="Deck instance not found")
  return None


# --- Deck Instance Position Item Endpoints ---


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create item in deck instance: ",
)
@router.post(
  "/instances/{instance_accession}/positions",
  response_model=DeckPositionResourceResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Deck Instances"],
)
async def create_deck_position_item(
  instance_accession: str | UUID,
  request: DeckPositionResourceCreate,
  db: AsyncSession = Depends(get_db),
):
  """Add a resource item to a position in a deck instance."""
  try:
    instance_accession_id = await deck_instance_accession_resolver(
      accession=instance_accession, db=db
    )
    return await svc.create_deck_position_item(
      db, instance_accession_id, **request.model_dump()
    )
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update item in deck instance: ",
)
@router.put(
  "/instances/{instance_accession}/positions/{item_accession_id}",
  response_model=DeckPositionResourceResponse,
  tags=["Deck Instances"],
)
async def update_deck_position_item(
  item_accession_id: UUID,
  request: DeckPositionResourceCreate,
  db: AsyncSession = Depends(get_db),
):
  """Update an item in a deck instance position."""
  updated_item = await svc.update_deck_position_item(
    db, item_accession_id, **request.model_dump(exclude_unset=True)
  )
  if not updated_item:
    raise HTTPException(status_code=404, detail="Deck position item not found")
  return updated_item


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete item from deck instance: ",
)
@router.delete(
  "/instances/{instance_accession}/positions/{item_accession_id}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Deck Instances"],
)
async def delete_deck_position_item(
  item_accession_id: UUID, db: AsyncSession = Depends(get_db)
):
  """Delete an item from a deck instance position."""
  if not await svc.delete_deck_position_item(db, item_accession_id):
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
  "/types/{type_accession}/positions/{position_accession_id}",
  response_model=DeckPositionDefinitionResponse,
  tags=["Deck Type Definitions"],
)
async def read_deck_position_definition(
  type_accession: str | UUID, position_accession_id: UUID, db: AsyncSession = Depends(get_db)
):
  """Retrieve a specific position definition from a deck type."""
  position = await svc.read_deck_position_definition(db, type_accession, position_accession_id)
  if not position:
    raise HTTPException(status_code=404, detail="Position definition not found")
  return position


@log_deck_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update deck position definition: ",
)
@router.put(
  "/types/{type_accession}/positions/{position_accession_id}",
  response_model=DeckPositionDefinitionResponse,
  tags=["Deck Type Definitions"],
)
async def update_deck_position_definition(
  type_accession: str | UUID,
  position_accession_id: UUID,
  request: DeckPositionDefinitionUpdate,
  db: AsyncSession = Depends(get_db),
):
  """Update an existing position definition within a deck type."""
  updated_pos = await svc.update_deck_position_definition(
    db, type_accession, position_accession_id, **request.model_dump(exclude_unset=True)
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
  "/types/{type_accession}/positions/{position_accession_id}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Deck Type Definitions"],
)
async def delete_deck_position_definition(
  type_accession: str | UUID, position_accession_id: UUID, db: AsyncSession = Depends(get_db)
):
  """Delete a position definition from a deck type."""
  if not await svc.delete_deck_position_definition(db, type_accession, position_accession_id):
    raise HTTPException(status_code=404, detail="Position definition not found")
  return None
'''
