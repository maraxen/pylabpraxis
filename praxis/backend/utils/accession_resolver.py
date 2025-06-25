"""Shared utility function for the service layer to resolve accessions to UUIDs.

praxis/backend/services/utils.py
"""

from typing import Awaitable, Callable, Optional, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


async def get_accession_id_from_accession(
  *,
  accession: str | UUID,
  db: AsyncSession,
  get_func: Callable[[AsyncSession, UUID], Awaitable[Optional[T]]],
  get_by_name_func: Callable[[AsyncSession, str], Awaitable[Optional[T]]],
  entity_type_name: str,
) -> UUID:
  """Resolve a string or UUID accession to a specific entity's UUID.

  This utility function centralizes the logic for fetching an entity by either its
  unique ID or a user-assigned name, returning the definitive UUID if found.

  Args:
      accession: The UUID or user-assigned name of the entity to resolve.
      db: The async database session.
      get_func: The service function used to get the entity by its UUID.
                      Example: `svc.get_resource_instance`
      get_by_name_func: The service function used to get the entity by its name.
                        Example: `svc.get_resource_instance_by_name`
      entity_type_name: The user-friendly name of the entity type (e.g., "Resource
                        Instance") used for creating clear error messages.

  Returns:
      The UUID of the found entity.

  Raises:
      ValueError: If an entity cannot be found with the given accession.
      TypeError: If the accession type is invalid.
      RuntimeError: If there is an unexpected error during resolution.

  """
  obj: Optional[T] = None
  if isinstance(accession, UUID):
    # If it's already a UUID, we just need to confirm it exists.
    obj = await get_func(db, accession)
    if obj:
      # The object exists, so the UUID is valid.
      return accession
  elif isinstance(accession, str):
    # If it's a string, we fetch the object to get its ID.
    obj = await get_by_name_func(db, accession)
    if obj and hasattr(obj, "id"):
      # The object was found by name, return its ID.
      return getattr(obj, "id")  # Ensure we get the ID attribute safely
  else:
    # This case should not be hit if using FastAPI's type hints correctly,
    # but it's good practice to handle it.
    raise TypeError(f"Invalid accession type provided: {type(accession)}")

  # If we reach this point, 'obj' is None, meaning no entity was found.
  raise ValueError(f"{entity_type_name} with accession '{accession}' not found.")
