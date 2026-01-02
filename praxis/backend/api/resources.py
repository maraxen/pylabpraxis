"""FastAPI router for all resource-related endpoints.

This module defines endpoints for managing resource definitions and resources,
including creation, retrieval, updating, and deletion. It uses the service layer
to interact with the database and handle business logic.
"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.dependencies import get_db
from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.orm.resource import ResourceDefinitionOrm
from praxis.backend.models.pydantic_internals.resource import (
  ResourceCreate,
  ResourceDefinitionCreate,
  ResourceDefinitionResponse,
  ResourceDefinitionUpdate,
  ResourceResponse,
  ResourceUpdate,
)
from praxis.backend.services.resource import resource_service
from praxis.backend.services.resource_type_definition import ResourceTypeDefinitionCRUDService

router = APIRouter()


@router.get(
  "/definitions/facets",
  tags=["Resource Definitions"],
  summary="Get facet values with counts for filtering",
  response_model=dict[str, list[dict[str, Any]]],
)
async def get_resource_definition_facets(
  plr_category: str | None = None,
  vendor: str | None = None,
  num_items: int | None = None,
  plate_type: str | None = None,
  db: AsyncSession = Depends(get_db),
) -> dict[str, list[dict[str, Any]]]:
  """Return unique values and counts for filterable resource definition fields.

  Used for dynamically generating filter chips in the frontend.
  Returns facets for: plr_category, vendor, num_items, plate_type, well_volume_ul, tip_volume_ul.

  Supports dynamic filtering: passing a filter (e.g. plr_category='plate') will update
  the counts for other facets (e.g. only showing vendors that make plates).
  """
  facets: dict[str, list[dict[str, Any]]] = {}

  # Define facet fields to query
  facet_fields = {
    "plr_category": ResourceDefinitionOrm.plr_category,
    "vendor": ResourceDefinitionOrm.vendor,
    "num_items": ResourceDefinitionOrm.num_items,
    "plate_type": ResourceDefinitionOrm.plate_type,
    "well_volume_ul": ResourceDefinitionOrm.well_volume_ul,
    "tip_volume_ul": ResourceDefinitionOrm.tip_volume_ul,
  }

  model = ResourceDefinitionOrm

  # Helper to build base query with filters applied
  def build_query(exclude_field: str | None = None):
    q = select(model)

    # Apply all active filters EXCEPT the one we are currently calculating counts for.
    # This allows seeing other options within a selected category (e.g. seeing other Vendors even if one is selected)
    # BUT for the progressive disclosure flow, we might want strict filtering.
    # Let's start with strict filtering but exclude the current field to allow switching.

    if plr_category and exclude_field != "plr_category":
      q = q.where(model.plr_category == plr_category)
    if vendor and exclude_field != "vendor":
      q = q.where(model.vendor == vendor)
    if num_items is not None and exclude_field != "num_items":
      q = q.where(model.num_items == num_items)
    if plate_type and exclude_field != "plate_type":
      q = q.where(model.plate_type == plate_type)

    return q

  for facet_name in facet_fields:
    # Build query excluding the current facet field (so we get counts for all options in this facet)
    base_query = build_query(exclude_field=facet_name)
    subq = base_query.subquery()

    # Get the column from the subquery
    # Note: DB columns match the keys in facet_fields
    subq_col = getattr(subq.c, facet_name)

    # Select column and count from the subquery
    stmt = (
      select(subq_col, func.count().label("count"))
      .where(subq_col.isnot(None))
      .group_by(subq_col)
      .order_by(func.count().desc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    facets[facet_name] = [{"value": row[0], "count": row[1]} for row in rows]

  return facets


# IMPORTANT: Include /definitions router BEFORE / router to ensure
# more specific routes are matched first
router.include_router(
  create_crud_router(
    service=ResourceTypeDefinitionCRUDService(ResourceDefinitionOrm),
    prefix="/definitions",
    tags=["Resource Definitions"],
    create_schema=ResourceDefinitionCreate,
    update_schema=ResourceDefinitionUpdate,
    response_schema=ResourceDefinitionResponse,
  ),
)

router.include_router(
  create_crud_router(
    service=resource_service,
    prefix="/",
    tags=["Resources"],
    create_schema=ResourceCreate,
    update_schema=ResourceUpdate,
    response_schema=ResourceResponse,
  ),
)
