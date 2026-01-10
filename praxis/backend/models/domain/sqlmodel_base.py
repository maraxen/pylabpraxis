"""Unified base class for all Praxis domain models using SQLModel.

This module provides the `PraxisBase` class, which combines SQLAlchemy ORM
capabilities with Pydantic serialization.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import ConfigDict
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel

from praxis.backend.utils.db import JsonVariant
from praxis.backend.utils.uuid import uuid7


def json_field(
  default: Any = None,
  default_factory: Any = None,
  nullable: bool = True,
  **kwargs: Any,
) -> Any:
  """Create a SQLModel-compatible JSON field using JsonVariant.

  Args:
      default: The default value for the field.
      default_factory: A callable to generate the default value.
      nullable: Whether the column is nullable.
      **kwargs: Additional arguments for SQLModel.Field.

  Returns:
      A SQLModel Field instance configured with JsonVariant.

  """
  if default_factory is not None:
    return Field(
      default_factory=default_factory,
      sa_column=Column(JsonVariant, nullable=nullable),
      **kwargs,
    )
  return Field(
    default=default,
    sa_column=Column(JsonVariant, nullable=nullable),
    **kwargs,
  )


class PraxisBase(SQLModel):
  """Unified base for all Praxis domain models.

  Provides:
  - UUID7 accession_id as primary key (when table=True)
  - Timestamps (created_at, updated_at)
  - Generic properties_json field
  - Pydantic config for serialization
  """

  model_config = ConfigDict(
    from_attributes=True,
    use_enum_values=True,
    validate_assignment=True,
  )

  # When subclassed with table=True, these become columns
  accession_id: uuid.UUID = Field(
    default_factory=uuid7,
    primary_key=True,
    index=True,
    description="The unique accession ID of the record.",
  )

  created_at: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    sa_column_kwargs={"server_default": func.now()},
    description="The time the record was created.",
  )

  updated_at: datetime | None = Field(
    default=None,
    sa_column_kwargs={"onupdate": func.now()},
    description="The time the record was last updated.",
  )

  name: str = Field(
    index=True,
    description="An optional name for the record.",
  )

  properties_json: dict[str, Any] | None = json_field(
    default=None,
    description="Arbitrary metadata associated with the record.",
  )
