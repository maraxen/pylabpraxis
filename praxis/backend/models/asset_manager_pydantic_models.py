# pylint: disable=too-few-public-methods
"""Pydantic models for the AssetManager.

This module provides Pydantic models for the AssetManager,
enabling proper validation and serialization for asset management.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AcquireResource(BaseModel):
    """Model for acquiring a resource."""

    protocol_run_accession_id: UUID
    requested_asset_name_in_protocol: str
    fqn: str
    user_choice_instance_accession_id: UUID | None = None
    location_constraints: dict[str, Any] | None = None
    property_constraints: dict[str, Any] | None = None


class ReleaseResource(BaseModel):
    """Model for releasing a resource."""

    resource_orm_accession_id: UUID
    final_status: str
    final_properties_json_update: dict[str, Any] | None = None
    clear_from_accession_id: UUID | None = None
    clear_from_position_name: str | None = None
    status_details: str | None = "Released from run"
