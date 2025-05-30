# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""
praxis/database_models/asset_management_orm.py

SQLAlchemy ORM models for Asset Management, including:
- MachineOrm (Instruments/Hardware)
- ResourceDefinitionCatalogOrm (Types of Resource from PLR)
- ResourceInstanceOrm (Specific physical resource items)
- DeckConfigurationOrm (Named deck layouts)
- DeckConfigurationPoseItemOrm (Resource in a pose for a layout)
"""

from datetime import datetime
from typing import Optional, Any

from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey,
    JSON,
    DateTime,
    UniqueConstraint,
    Float,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base  # Import your project's Base


class DeckConfigurationOrm(Base):
    __tablename__ = "deck_configurations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )  # praxis_deck_config_id
    layout_name: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )

    # A Deck itself is a Machine
    deck_machine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("machines.id"), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    deck_machine = relationship("MachineOrm", back_populates="deck_configurations")
    pose_items = relationship(
        "DeckConfigurationPoseItemOrm",
        back_populates="deck_configuration",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<DeckConfigurationOrm(id={self.id}, name='{self.layout_name}')>"


class DeckConfigurationPoseItemOrm(Base):
    __tablename__ = "deck_configuration_pose_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    deck_configuration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deck_configurations.id"), nullable=False
    )
    pose_id: Mapped[str] = mapped_column(
        String, nullable=False, comment="Pose name on the deck (e.g., A1, SLOT_7)"
    )

    # This links to a specific physical piece of resource
    resource_instance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resource_instances.id"), nullable=False
    )

    # Optional: for validation, store the expected type of resource for this pose in this layout
    expected_resource_definition_name: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey("resource_definition_catalog.pylabrobot_definition_name"),
        nullable=True,
    )
    deck_pose_definition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("deck_pose_definitions.id"), nullable=True, index=True
    )

    deck_configuration = relationship(
        "DeckConfigurationOrm", back_populates="pose_items"
    )
    resource_instance = relationship(
        "ResourceInstanceOrm", back_populates="deck_configuration_items"
    )
    expected_resource_definition = relationship(
        "ResourceDefinitionCatalogOrm"
    )  # Simple relationship
    deck_pose_definition = relationship("DeckPoseDefinitionOrm")

    __table_args__ = (
        UniqueConstraint("deck_configuration_id", "pose_id", name="uq_deck_pose_item"),
    )

    def __repr__(self):
        return f"<DeckConfigurationPoseItemOrm(deck_config_id={self.deck_configuration_id}, \
          pose='{self.pose_id}', lw_instance_id={self.resource_instance_id})>"


class DeckPoseDefinitionOrm(Base):
    __tablename__ = "deck_pose_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_type_definition_id: Mapped[int] = mapped_column(
        ForeignKey("deck_type_definitions.id"), nullable=False
    )
    pose_id: Mapped[str] = mapped_column(String, nullable=False)
    nominal_x_mm: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # From plan, but PLR might always provide these
    nominal_y_mm: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # From plan
    nominal_z_mm: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # From plan
    accepted_resource_categories_json: Mapped[Optional[list[str]]] = mapped_column(
        JSON, nullable=True
    )
    pose_specific_details_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Relationship
    deck_type_definition: Mapped["DeckTypeDefinitionOrm"] = relationship(
        back_populates="pose_definitions"
    )

    # Unique constraint for pose_id within a deck_type_definition
    __table_args__ = (
        UniqueConstraint(
            "deck_type_definition_id", "pose_id", name="uq_deck_pose_definition"
        ),
    )

    def __repr__(self):
        return f"<DeckPoseDefinitionOrm(id={self.id}, name='{self.pose_id}', \
          deck_type_id={self.deck_type_definition_id})>"


class DeckTypeDefinitionOrm(Base):
    __tablename__ = "deck_type_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pylabrobot_deck_fqn: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    plr_category: Mapped[Optional[str]] = mapped_column(
        String, default="deck"
    )  # If PLR provides it, could be nullable=False
    default_size_x_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    default_size_y_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    default_size_z_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    serialized_to_location_method_json: Mapped[Optional[dict[str, Any]]] = (
        mapped_column(JSON, nullable=True)
    )
    pose_to_location_method_name: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, comment="Name of the method to convert pose to location"
    )
    pose_argument_name: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, comment="Name of the argument for pose in the method"
    )
    serialized_constructor_args_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    serialized_assignment_methods_json: Mapped[Optional[dict[str, Any]]] = (
        mapped_column(JSON, nullable=True)
    )
    serialized_constructor_layout_hints_json: Mapped[Optional[dict[str, Any]]] = (
        mapped_column(JSON, nullable=True)
    )
    additional_properties_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Relationships
    pose_definitions: Mapped[list[DeckPoseDefinitionOrm]] = relationship(
        back_populates="deck_type_definition", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DeckTypeDefinitionOrm(id={self.id}, fqn='{self.pylabrobot_deck_fqn}', \
          name='{self.display_name}')>"
