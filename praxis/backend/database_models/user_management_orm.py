# praxis/backend/database_models/user_management_orm.py
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Boolean, DateTime, func # Removed Column
from sqlalchemy.orm import Mapped, mapped_column # Added Mapped, mapped_column

from praxis.backend.utils.db import Base # Import your project's Base

class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True, comment="User's phone number for SMS notifications")
    phone_carrier: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="User's phone carrier for SMS gateway emails, e.g., 'verizon', 'att'")
    # TODO: Add is_superuser or roles if needed for authorization

    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Example of a relationship if UserOrm links to other tables in the future
    # protocol_runs = relationship("ProtocolRunOrm", back_populates="created_by_user")

    def __repr__(self):
        return f"<UserOrm(id={self.id}, username='{self.username}', email='{self.email}', is_active={self.is_active})>"
