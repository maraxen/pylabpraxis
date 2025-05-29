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
    slot_items = relationship(
        "DeckConfigurationSlotItemOrm",
        back_populates="deck_configuration",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<DeckConfigurationOrm(id={self.id}, name='{self.layout_name}')>"


class DeckConfigurationSlotItemOrm(Base):
    __tablename__ = "deck_configuration_slot_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    deck_configuration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deck_configurations.id"), nullable=False
    )
    slot_name: Mapped[str] = mapped_column(
        String, nullable=False, comment="Slot name on the deck (e.g., A1, SLOT_7)"
    )

    # This links to a specific physical piece of resource
    resource_instance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resource_instances.id"), nullable=False
    )

    # Optional: for validation, store the expected type of resource for this slot in this layout
    expected_resource_definition_name: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey("resource_definition_catalog.pylabrobot_definition_name"),
        nullable=True,
    )
    deck_slot_definition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("deck_slot_definitions.id"), nullable=True, index=True
    )

    deck_configuration = relationship(
        "DeckConfigurationOrm", back_populates="slot_items"
    )
    resource_instance = relationship(
        "ResourceInstanceOrm", back_populates="deck_configuration_items"
    )
    expected_resource_definition = relationship(
        "ResourceDefinitionCatalogOrm"
    )  # Simple relationship
    deck_slot_definition = relationship("DeckSlotDefinitionOrm")

    __table_args__ = (
        UniqueConstraint(
            "deck_configuration_id", "slot_name", name="uq_deck_slot_item"
        ),
    )

    def __repr__(self):
        return f"<DeckConfigurationSlotItemOrm(deck_config_id={self.deck_configuration_id}, slot='{self.slot_name}', lw_instance_id={self.resource_instance_id})>"


class DeckSlotDefinitionOrm(Base):
    __tablename__ = "deck_slot_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_type_definition_id: Mapped[int] = mapped_column(
        ForeignKey("deck_type_definitions.id"), nullable=False
    )
    slot_name: Mapped[str] = mapped_column(String, nullable=False)
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
    slot_specific_details_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Relationship
    deck_type_definition: Mapped["DeckTypeDefinitionOrm"] = relationship(
        back_populates="slot_definitions"
    )

    # Unique constraint for slot_name within a deck_type_definition
    __table_args__ = (
        UniqueConstraint(
            "deck_type_definition_id", "slot_name", name="uq_deck_slot_definition"
        ),
    )

    def __repr__(self):
        return f"<DeckSlotDefinitionOrm(id={self.id}, name='{self.slot_name}', \
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
    slot_definitions: Mapped[list[DeckSlotDefinitionOrm]] = relationship(
        back_populates="deck_type_definition", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DeckTypeDefinitionOrm(id={self.id}, fqn='{self.pylabrobot_deck_fqn}', \
          name='{self.display_name}')>"
