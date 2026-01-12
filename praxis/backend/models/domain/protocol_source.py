# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for ProtocolSource variants."""

import uuid

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums import ProtocolSourceStatusEnum


# =============================================================================
# Protocol Source Repository (Git)
# =============================================================================


class ProtocolSourceRepositoryBase(PraxisBase):
    """Base schema for ProtocolSourceRepository - shared fields for create/update/response."""

    git_url: str = Field(default="", index=True, description="Git repository URL")
    default_ref: str = Field(default="main", description="Default branch or tag")
    local_checkout_path: str | None = Field(default=None, description="Local checkout path")
    last_synced_commit: str | None = Field(default=None, description="Last synced commit SHA")
    status: ProtocolSourceStatusEnum = Field(
        default=ProtocolSourceStatusEnum.ACTIVE,
        sa_column=Column(SAEnum(ProtocolSourceStatusEnum, name="ps_status_enum_repo_v3"), nullable=False),
    )
    auto_sync_enabled: bool = Field(default=True, description="Whether auto-sync is enabled")


class ProtocolSourceRepository(ProtocolSourceRepositoryBase, table=True):
    """ProtocolSourceRepository ORM model - tracks Git repository protocol sources."""

    __tablename__ = "protocol_source_repositories"


class ProtocolSourceRepositoryCreate(ProtocolSourceRepositoryBase):
    """Schema for creating a ProtocolSourceRepository."""
    pass


class ProtocolSourceRepositoryRead(ProtocolSourceRepositoryBase):
    """Schema for reading a ProtocolSourceRepository (API response)."""
    accession_id: uuid.UUID


class ProtocolSourceRepositoryUpdate(SQLModel):
    """Schema for updating a ProtocolSourceRepository (partial update)."""

    name: str | None = None
    git_url: str | None = None
    default_ref: str | None = None
    local_checkout_path: str | None = None
    status: ProtocolSourceStatusEnum | None = None
    auto_sync_enabled: bool | None = None


# =============================================================================
# File System Protocol Source
# =============================================================================


class FileSystemProtocolSourceBase(PraxisBase):
    """Base schema for FileSystemProtocolSource - shared fields for create/update/response."""

    base_path: str = Field(default="", description="Base path for file system source")
    is_recursive: bool = Field(default=True, description="Whether to scan subdirectories recursively")
    status: ProtocolSourceStatusEnum = Field(
        default=ProtocolSourceStatusEnum.ACTIVE,
        sa_column=Column(SAEnum(ProtocolSourceStatusEnum, name="ps_status_enum_fs_v3"), nullable=False),
    )


class FileSystemProtocolSource(FileSystemProtocolSourceBase, table=True):
    """FileSystemProtocolSource ORM model - tracks file system protocol sources."""

    __tablename__ = "file_system_protocol_sources"


class FileSystemProtocolSourceCreate(FileSystemProtocolSourceBase):
    """Schema for creating a FileSystemProtocolSource."""
    pass


class FileSystemProtocolSourceRead(FileSystemProtocolSourceBase):
    """Schema for reading a FileSystemProtocolSource (API response)."""
    accession_id: uuid.UUID


class FileSystemProtocolSourceUpdate(SQLModel):
    """Schema for updating a FileSystemProtocolSource (partial update)."""

    name: str | None = None
    base_path: str | None = None
    is_recursive: bool | None = None
    status: ProtocolSourceStatusEnum | None = None
