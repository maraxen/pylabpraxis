"""Service layer for User management.

This module provides the UserService class for managing user-related operations
including creation, retrieval, updates, and deletion. It includes password hashing
for secure credential storage.
"""

import logging
import uuid
from typing import Any

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.user import UserOrm
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.user import UserCreate, UserUpdate
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import apply_pagination
from praxis.backend.utils.db_decorator import handle_db_transaction

logger = logging.getLogger(__name__)

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(CRUDBase[UserOrm, UserCreate, UserUpdate]):
    """Service for user-related operations.

    Provides CRUD operations for users with additional functionality for:
    - Password hashing and verification
    - Retrieval by username or email
    - User activation/deactivation
    """

    def _hash_password(self, password: str) -> str:
        """Hash a plain text password.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password suitable for storage
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @handle_db_transaction
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> UserOrm:
        """Create a new user with hashed password.

        Args:
            db: Database session
            obj_in: User creation data including plain text password

        Returns:
            Created UserOrm instance

        Raises:
            IntegrityError: If username or email already exists
        """
        logger.info("Attempting to create user '%s'.", obj_in.username)

        # Hash the password before storing
        user_data = obj_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = self._hash_password(obj_in.password)

        # Filter to only valid constructor parameters
        import inspect as py_inspect
        init_signature = py_inspect.signature(UserOrm.__init__)
        valid_params = {p.name for p in init_signature.parameters.values()}
        filtered_data = {key: value for key, value in user_data.items() if key in valid_params}

        user_orm = UserOrm(**filtered_data)
        db.add(user_orm)
        await db.flush()
        await db.refresh(user_orm)

        logger.info(
            "Successfully created user '%s' with ID %s.",
            obj_in.username,
            user_orm.accession_id,
        )
        return user_orm

    async def get(self, db: AsyncSession, accession_id: uuid.UUID) -> UserOrm | None:
        """Retrieve a specific user by ID.

        Args:
            db: Database session
            accession_id: User's UUID

        Returns:
            UserOrm instance if found, None otherwise
        """
        logger.info("Attempting to retrieve user with ID: %s.", accession_id)
        user = await super().get(db, accession_id)
        if user:
            logger.info(
                "Successfully retrieved user ID %s: '%s'.",
                accession_id,
                user.username,
            )
        else:
            logger.info("User with ID %s not found.", accession_id)
        return user

    async def get_by_username(self, db: AsyncSession, username: str) -> UserOrm | None:
        """Retrieve a user by username.

        Args:
            db: Database session
            username: Username to search for

        Returns:
            UserOrm instance if found, None otherwise
        """
        logger.info("Attempting to retrieve user by username: %s.", username)
        stmt = select(self.model).where(self.model.username == username)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user:
            logger.info("Successfully found user '%s'.", username)
        else:
            logger.info("User with username '%s' not found.", username)
        return user

    async def get_by_email(self, db: AsyncSession, email: str) -> UserOrm | None:
        """Retrieve a user by email.

        Args:
            db: Database session
            email: Email address to search for

        Returns:
            UserOrm instance if found, None otherwise
        """
        logger.info("Attempting to retrieve user by email: %s.", email)
        stmt = select(self.model).where(self.model.email == email)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user:
            logger.info("Successfully found user with email '%s'.", email)
        else:
            logger.info("User with email '%s' not found.", email)
        return user

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        filters: SearchFilters,
    ) -> list[UserOrm]:
        """List users with pagination.

        Args:
            db: Database session
            filters: Search filters including pagination parameters

        Returns:
            List of UserOrm instances
        """
        logger.info("Listing users with filters: %s", filters.model_dump_json())
        stmt = select(self.model).order_by(self.model.username)
        stmt = apply_pagination(stmt, filters)
        result = await db.execute(stmt)
        users = list(result.scalars().all())
        logger.info("Found %d users.", len(users))
        return users

    @handle_db_transaction
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: UserOrm,
        obj_in: UserUpdate | dict[str, Any],
    ) -> UserOrm:
        """Update an existing user.

        If password is included in the update, it will be hashed before storage.

        Args:
            db: Database session
            db_obj: Existing UserOrm instance
            obj_in: Update data (UserUpdate or dict)

        Returns:
            Updated UserOrm instance
        """
        logger.info("Attempting to update user with ID: %s.", db_obj.accession_id)

        # Convert to model if dict
        obj_in_model = UserUpdate(**obj_in) if isinstance(obj_in, dict) else obj_in

        # Handle password hashing if password is being updated
        update_data = obj_in_model.model_dump(exclude_unset=True)
        if "password" in update_data:
            hashed_password = self._hash_password(update_data.pop("password"))
            update_data["hashed_password"] = hashed_password

        # Apply updates
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)

        logger.info(
            "Successfully updated user ID %s: '%s'.",
            db_obj.accession_id,
            db_obj.username,
        )
        return db_obj

    @handle_db_transaction
    async def remove(self, db: AsyncSession, *, accession_id: uuid.UUID) -> UserOrm | None:
        """Delete a specific user by ID.

        Args:
            db: Database session
            accession_id: User's UUID

        Returns:
            Deleted UserOrm instance if found, None otherwise
        """
        logger.info("Attempting to delete user with ID: %s.", accession_id)
        user_orm = await super().remove(db, accession_id=accession_id)
        if not user_orm:
            logger.warning("User with ID %s not found for deletion.", accession_id)
            return None

        logger.info(
            "Successfully deleted user ID %s: '%s'.",
            accession_id,
            user_orm.username,
        )
        return user_orm

    async def authenticate(
        self,
        db: AsyncSession,
        *,
        username: str,
        password: str,
    ) -> UserOrm | None:
        """Authenticate a user by username and password.

        Args:
            db: Database session
            username: Username to authenticate
            password: Plain text password to verify

        Returns:
            UserOrm instance if authentication succeeds, None otherwise
        """
        logger.info("Attempting to authenticate user: %s.", username)
        user = await self.get_by_username(db, username=username)
        if not user:
            logger.info("Authentication failed: user '%s' not found.", username)
            return None

        if not self.verify_password(password, user.hashed_password):
            logger.info("Authentication failed: invalid password for user '%s'.", username)
            return None

        if not user.is_active:
            logger.info("Authentication failed: user '%s' is inactive.", username)
            return None

        logger.info("Successfully authenticated user '%s'.", username)
        return user

    @handle_db_transaction
    async def set_active(
        self,
        db: AsyncSession,
        *,
        user: UserOrm,
        is_active: bool,
    ) -> UserOrm:
        """Activate or deactivate a user.

        Args:
            db: Database session
            user: UserOrm instance to update
            is_active: New active status

        Returns:
            Updated UserOrm instance
        """
        logger.info(
            "Setting user '%s' (ID %s) active status to %s.",
            user.username,
            user.accession_id,
            is_active,
        )
        user.is_active = is_active
        db.add(user)
        await db.flush()
        await db.refresh(user)
        logger.info("Successfully updated active status for user '%s'.", user.username)
        return user


# Singleton instance
user_service = UserService(UserOrm)
