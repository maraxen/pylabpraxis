# praxis/backend/database_models/user_management_orm.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship # If relationships are needed later

# Ensure this import path for Base is correct for your project structure.
try:
    from praxis.backend.utils.db import Base # Import your project's Base
except ImportError:
    # This is a fallback for cases where the model might be used standalone
    # or if the path changes. For actual application runs, the above import should work.
    print("WARNING: Could not import Base from praxis.backend.utils.db. Using a local Base for UserOrm definition only.")
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

class UserOrm(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    phone_number = Column(String, nullable=True, index=True, comment="User's phone number for SMS notifications")
    phone_carrier = Column(String, nullable=True, comment="User's phone carrier for SMS gateway emails, e.g., 'verizon', 'att'")
    # TODO: Add is_superuser or roles if needed for authorization

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Example of a relationship if UserOrm links to other tables in the future
    # protocol_runs = relationship("ProtocolRunOrm", back_populates="created_by_user")

    def __repr__(self):
        return f"<UserOrm(id={self.id}, username='{self.username}', email='{self.email}', is_active={self.is_active})>"
