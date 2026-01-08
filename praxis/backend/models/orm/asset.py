"""Asset Management ORM Models.

praxis/backend/models/orm/asset.py

SQLAlchemy ORM Base models for managing physical assets in the lab,
including:
- Asset (Abstract base for all physical assets)
"""

from typing import TYPE_CHECKING, ClassVar

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.enums import AssetType
from praxis.backend.models.orm.types import JsonVariant
from praxis.backend.utils.db import Base

if TYPE_CHECKING:
  from praxis.backend.models.orm.schedule import AssetReservationOrm


class AssetOrm(Base):
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
    unique=True,
    index=True,
    comment="Name of the asset.",
    kw_only=True,
  )
  fqn: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="Fully qualified name of the asset's class, if applicable.",
    kw_only=True,
    default="",
  )
  location: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    default=None,
    comment="Location of the asset in the lab.",
  )
  plr_state: Mapped[dict | None] = mapped_column(
    JsonVariant,
    nullable=True,
    comment="PLR state of the asset, if applicable.",
    default=None,
  )
  plr_definition: Mapped[dict | None] = mapped_column(
    JsonVariant,
    nullable=True,
    comment="PLR definition of the asset, if applicable.",
    default=None,
  )

  asset_reservations: Mapped[list["AssetReservationOrm"]] = relationship(
    "AssetReservationOrm",
    foreign_keys="[AssetReservationOrm.asset_accession_id]",
    back_populates="asset",
    cascade="all, delete-orphan",
    default_factory=list,
  )

  __mapper_args__: ClassVar[dict] = {
    "polymorphic_on": asset_type,
    "polymorphic_identity": AssetType.ASSET,
  }  # type: ignore[override]

  def __repr__(self) -> str:
    """Render string representation of the Asset."""
    return f"<Asset(id={self.accession_id}, type='{self.asset_type.value}', name='{self.name}')>"
