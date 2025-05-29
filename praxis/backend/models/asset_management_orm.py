# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""
praxis/database_models/asset_management_orm.py

SQLAlchemy ORM models for Asset Management, including:
- MachineOrm (Instruments/Hardware)
- ResourceDefinitionCatalogOrm (Types of Resource from PLR)
- ResourceInstanceOrm (Specific physical resource items)
- DeckConfigurationOrm (Named deck layouts)
- DeckConfigurationSlotItemOrm (Resource in a slot for a layout)
"""

# TODO: refactor to align with PLR and be more modular
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    JSON,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base  # Import your project's Base


class AssetInstanceOrm(Base):
    """
    Abstract base class representing any physical asset in the lab.
    This serves as an umbrella for both machines and resource instances.
    """

    __tablename__ = "asset_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_type: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )  # 'machine', 'resource', etc.
    asset_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
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
        UniqueConstraint("asset_type", "asset_id", name="uq_asset_instance"),
    )

    def __repr__(self):
        return f"<AssetInstanceOrm(id={self.id}, type='{self.asset_type}', asset_id={self.asset_id})>"
