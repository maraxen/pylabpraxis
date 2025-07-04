"""Asset Management ORM Models.

praxis/backend/models/orm/asset.py

SQLAlchemy ORM Base models for managing physical assets in the lab,
including:
- Asset (Abstract base for all physical assets)
"""

from typing import ClassVar

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from praxis.backend.models.enums import AssetType
from praxis.backend.utils.db import Base


class Asset(Base):
  """Abstract base class representing any physical asset in the lab.

  This serves as an umbrella for both machines and resource instances.
  """

  __tablename__ = "assets"

  asset_type: Mapped[AssetType] = mapped_column(
    Enum(AssetType),
    nullable=False,
    index=True,
    default=AssetType.ASSET,
    comment="Type of asset, e.g., machine, resource, etc.",
  )
  name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="Name of the asset.",
    init=False,
  )
  fqn: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    comment="Fully qualified name of the asset's class, if applicable.",
    default=None,
  )
  location: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    default=None,
    comment="Location of the asset in the lab.",
  )
  plr_state: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="PLR state of the asset, if applicable.",
    default=None,
  )
  plr_definition: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="PLR definition of the asset, if applicable.",
    default=None,
  )

  __mapper_args__: ClassVar[dict] = {"polymorphic_on": asset_type, "polymorphic_identity": "asset"}  # type: ignore[override]

  def __repr__(self) -> str:
    """Render string representation of the Asset."""
    return f"<Asset(id={self.accession_id}, type='{self.asset_type.value}', name='{self.name}')>"
