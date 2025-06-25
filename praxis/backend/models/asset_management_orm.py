# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Asset Management ORM Models.

praxis/database_models/asset_management_orm.py

SQLAlchemy ORM Base models for managing physical assets in the lab,
including:
- Asset (Abstract base for all physical assets)
"""

import uuid
from typing import Optional

from sqlalchemy import JSON, UUID, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from praxis.backend.models.enums import AssetType
from praxis.backend.models.timestamp_mixin import TimestampMixin
from praxis.backend.utils.db import Base  # Import your project's Base


class Asset(TimestampMixin, Base):
  """Abstract base class representing any physical asset in the lab.

  This serves as an umbrella for both machines and resource instances.
  """

  __tablename__ = "assets"

  accession_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  asset_type: Mapped[AssetType] = mapped_column(
    Enum(AssetType), nullable=False, index=True
  )
  name: Mapped[str] = mapped_column(String, nullable=False, index=True)
  fqn: Mapped[Optional[str]] = mapped_column(
    String,
    nullable=True,
    index=True,
    comment="Fully qualified name of the asset's class, if applicable.",
  )
  location: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
  plr_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  plr_definition: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  properties_json: Mapped[Optional[dict]] = mapped_column(
    JSON, nullable=True, comment="Arbitrary metadata about the asset."
  )

  __mapper_args__ = {"polymorphic_on": asset_type, "polymorphic_identity": "asset"}

  def __repr__(self):
    """Render string representation of the Asset."""
    return (
      f"<Asset(id={self.accession_id}, "
      f"type='{self.asset_type.value}', name='{self.name}')>"
    )
