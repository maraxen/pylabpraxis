# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Asset Management ORM Models.

praxis/database_models/asset_management_orm.py

SQLAlchemy ORM Base models for managing physical assets in the lab,
including:
- AssetInstanceOrm (Abstract base for all physical assets)
"""

from datetime import datetime
from typing import Optional

import uuid
from sqlalchemy import (
  JSON,
  UUID,
  DateTime,
  Integer,
  String,
  UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base  # Import your project's Base


class AssetInstanceOrm(Base):
  """Abstract base class representing any physical asset in the lab.

  This serves as an umbrella for both machines and resource instances.
  """

  __tablename__ = "asset_instances"

  accession_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  asset_type: Mapped[str] = mapped_column(
    String, nullable=False, index=True
  )  # 'machine', 'resource', etc.
  asset_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID, nullable=False, index=True
  )  # FK to concrete asset table (interpreted based on asset_type)

  barcode: Mapped[Optional[str]] = mapped_column(
    String, nullable=True, unique=True, index=True
  )
  serial_number: Mapped[Optional[str]] = mapped_column(
    String, nullable=True, unique=True, index=True
  )

  acquisition_date: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  warranty_expiry: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  last_maintenance: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  next_maintenance_due: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )

  owner: Mapped[Optional[str]] = mapped_column(
    String, nullable=True
  )  # Person or group responsible for this asset
  # cost_center = Column(String, nullable=True)
  # purchase_value = Column(Float, nullable=True)

  metadata_json: Mapped[Optional[dict]] = mapped_column(
    JSON, nullable=True, comment="Additional asset metadata"
  )

  created_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )

  __table_args__ = (
    UniqueConstraint("asset_type", "asset_accession_id", name="uq_asset_instance"),
  )

  def __repr__(self):
    """Render string representation of the AssetInstanceOrm."""
    return f"<AssetInstanceOrm(id={self.accession_id}, type='{self.asset_type}', \
          asset_accession_id={self.asset_accession_id})>"
