"""Query building utilities for applying common filters to SQLAlchemy select statements.

This module provides a set of reusable functions to build SQLAlchemy queries
based on a standardized SearchFilters model, promoting consistency and
reducing boilerplate code in the service layer.
"""

from datetime import datetime
from typing import Any, TypeVar

from sqlalchemy import Select, and_
from sqlalchemy.orm import InstrumentedAttribute

from praxis.backend.models.domain.filters import SearchFilters
from praxis.backend.utils.db import Base

BaseModel = TypeVar("BaseModel", bound=Base)


def apply_pagination(query: Select, filters: SearchFilters) -> Select:
  """Apply limit and offset for pagination to a SQLAlchemy query.

  Args:
      query: The SQLAlchemy Select statement.
      filters: The SearchFilters object containing pagination parameters.

  Returns:
      The modified Select statement with limit and offset applied.

  """
  if filters.limit > 0:
    query = query.limit(filters.limit)
  if filters.offset > 0:
    query = query.offset(filters.offset)
  return query


def apply_date_range_filters(
  query: Select,
  filters: SearchFilters,
  model_model_timestamp_field: InstrumentedAttribute[datetime] | datetime,
) -> Select:
  """Apply date range filters to a SQLAlchemy query.

  Args:
      query: The SQLAlchemy Select statement.
      filters: The SearchFilters object containing date range parameters.
      model_model_timestamp_field: The timestamp column of the ORM model to filter on
                                  (e.g., MyModel.created_at).

  Returns:
      The modified Select statement with date range filters applied.

  """
  conditions = []
  if filters.date_range_start:
    conditions.append(model_model_timestamp_field >= filters.date_range_start)
  if filters.date_range_end:
    conditions.append(model_model_timestamp_field <= filters.date_range_end)

  if conditions:
    query = query.filter(and_(*conditions))

  return query


def apply_property_filters(
  query: Select,
  filters: SearchFilters,
  model_model_properties_field: InstrumentedAttribute[dict[str, Any]] | dict[str, Any] | None,
) -> Select:
  """Apply key-value property filters to a JSONB column in a SQLAlchemy query.

  Note: This implementation currently supports exact matching for primitive values
  and containment (`@>`) for dictionary/object values. It can be extended to support
  more complex operators (e.g., gt, lt) by parsing the filter values.

  Example `property_filters` for extension:
  {
      "status": "active",  # exact match
      "metadata": {"tags": ["important"]}, // containment
      "value": {">": 100} // operator-based
  }

  Args:
      query: The SQLAlchemy Select statement.
      filters: The SearchFilters object containing property filters.
      model_model_properties_field: The JSONB column of the ORM model
                                  (e.g., MyModel.properties_json).

  Returns:
      The modified Select statement with property filters applied.

  """
  if not filters.property_filters or not model_model_properties_field:
    return query

  conditions = []
  for key, value in filters.property_filters.items():
    if isinstance(value, dict):
      conditions.append((key, value) in model_model_properties_field.items())
    else:
      conditions.append(model_model_properties_field[key].astext == str(value))

  if conditions:
    query = query.filter(and_(*conditions))

  return query


def apply_specific_id_filters(
  query: Select,
  filters: SearchFilters,
  model_model: type[BaseModel],
) -> Select:
  """Apply filters for common relationship IDs to a SQLAlchemy query.

  This function checks for common ID fields on the SearchFilters object and applies
  a filter if the corresponding attribute exists on the target ORM model.

  Args:
      query: The SQLAlchemy Select statement.
      filters: The SearchFilters object containing specific ID filters.
      model_model: The ORM model class to which the query applies.

  Returns:
      The modified Select statement with specific ID filters applied.

  """
  id_filters = {
    "protocol_run_accession_id": filters.protocol_run_accession_id,
    "machine_accession_id": filters.machine_accession_id,
    "resource_accession_id": filters.resource_accession_id,
  }

  conditions = []
  for filter_key, filter_value in id_filters.items():
    if filter_value and hasattr(model_model, filter_key):
      conditions.append(getattr(model_model, filter_key) == filter_value)

  if conditions:
    query = query.filter(and_(*conditions))

  return query


def apply_plr_category_filter(
  query: Select,
  filters: SearchFilters,
  orm_model: type[BaseModel],
) -> Select:
  """Apply a filter for the plr_category to a SQLAlchemy query.

  Args:
      query: The SQLAlchemy Select statement.
      filters: The SearchFilters object containing the plr_category.
      orm_model: The ORM model class to which the query applies.

  Returns:
      The modified Select statement with the plr_category filter applied.

  """
  value = filters.plr_category
  if not value and filters.search_filters:
    value = filters.search_filters.get("plr_category")

  if value and hasattr(orm_model, "plr_category"):
    query = query.filter(orm_model.plr_category == value)
  return query


def apply_search_filters(
  query: Select,
  model_model: type[BaseModel],
  filters: SearchFilters,
  properties_field: str = "properties_json",
  timestamp_field: str = "timestamp_field",
) -> Select:
  """Apply search filters to a SQLAlchemy query.

  This function applies pagination, date range, property, and specific ID filters
  to the provided SQLAlchemy Select statement based on the SearchFilters object.

  Args:
      query: The SQLAlchemy Select statement.
      model_model: The ORM model class to which the query applies.
      filters: The SearchFilters object containing various filter parameters.
      properties_field: The name of the JSONB properties field on the ORM model.
      timestamp_field: The name of the timestamp field on the ORM model.

  Returns:
      The modified Select statement with all applicable filters applied.

  """
  properties_col = getattr(model_model, properties_field, None)
  timestamp_col = getattr(model_model, timestamp_field, None)

  q = apply_specific_id_filters(query, filters, model_model)
  q = apply_plr_category_filter(q, filters, model_model)
  if properties_col is not None:
    q = apply_property_filters(q, filters, properties_col)
  if timestamp_col is not None:
    q = apply_date_range_filters(q, filters, timestamp_col)
  return apply_pagination(q, filters)


def apply_sorting(query: Select, model_model: type[BaseModel], sort_by: str | None) -> Select:
  """Apply sorting to a SQLAlchemy query based on the sort_by parameter.

  Args:
      query: The SQLAlchemy Select statement.
      model_model: The ORM model class to which the query applies.
      sort_by: The field name to sort by, prefixed with '-' for descending order.

  Returns:
      The modified Select statement with sorting applied.

  """
  if not sort_by:
    return query

  if sort_by.startswith("-"):
    column = getattr(model_model, sort_by[1:], None)
    if column is None:
      msg = f"Invalid sort field: {sort_by[1:]}"
      raise ValueError(msg)
    query = query.order_by(column.desc())
  else:
    column = getattr(model_model, sort_by, None)
    if column is None:
      msg = f"Invalid sort field: {sort_by}"
      raise ValueError(msg)
    query = query.order_by(column)

  return query
