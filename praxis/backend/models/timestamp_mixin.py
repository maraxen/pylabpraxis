"""TimestampMixin for created_at and updated_at columns."""

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class TimestampMixin:
  """Mixin for created_at and updated_at columns."""

  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(),
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
  )
