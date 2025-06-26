"""Query building utilities for applying common filters to SQLAlchemy select statements.

This module provides a set of reusable functions to build SQLAlchemy queries
based on a standardized SearchFilters model, promoting consistency and
reducing boilerplate code in the service layer.
"""

from sqlalchemy import Column, Select, and_
from sqlalchemy.dialects.postgresql import JSONB

from praxis.backend.models.filters import SearchFilters
from praxis.backend.utils.db import Base


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
  orm_model_timestamp_field: Column,
) -> Select:
  """Apply date range filters to a SQLAlchemy query.

  Args:
      query: The SQLAlchemy Select statement.
      filters: The SearchFilters object containing date range parameters.
      orm_model_timestamp_field: The timestamp column of the ORM model to filter on
                                  (e.g., MyModel.created_at).

  Returns:
      The modified Select statement with date range filters applied.

  """
  conditions = []
  if filters.date_range_start:
    conditions.append(orm_model_timestamp_field >= filters.date_range_start)
  if filters.date_range_end:
    conditions.append(orm_model_timestamp_field <= filters.date_range_end)

  if conditions:
    query = query.filter(and_(*conditions))

  return query


def apply_property_filters(
  query: Select,
  filters: SearchFilters,
  orm_model_properties_field: Column[JSONB],
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
      orm_model_properties_field: The JSONB column of the ORM model
                                  (e.g., MyModel.properties_json).

  Returns:
      The modified Select statement with property filters applied.

  """
  if not filters.property_filters:
    return query

  conditions = []
  for key, value in filters.property_filters.items():
    if isinstance(value, dict):
      # Use JSONB containment operator `@>` for nested objects
      conditions.append(orm_model_properties_field.contains({key: value}))
    else:
      # For primitive types, check for equality within the JSON structure.
      # The `->>` operator casts the value to text for comparison.
      conditions.append(orm_model_properties_field[key].astext == str(value))

  if conditions:
    query = query.filter(and_(*conditions))

  return query


def apply_specific_id_filters(query: Select, filters: SearchFilters, orm_model: Base) -> Select:
  """Apply filters for common relationship IDs to a SQLAlchemy query.

  This function checks for common ID fields on the SearchFilters object and applies
  a filter if the corresponding attribute exists on the target ORM model.

  Args:
      query: The SQLAlchemy Select statement.
      filters: The SearchFilters object containing specific ID filters.
      orm_model: The ORM model class to which the query applies.

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
    if filter_value and hasattr(orm_model, filter_key):
      conditions.append(getattr(orm_model, filter_key) == filter_value)

  if conditions:
    query = query.filter(and_(*conditions))

  return query
