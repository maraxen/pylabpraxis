import os
import subprocess
import time
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.pool import NullPool

from praxis.backend.utils.db import Base
from tests.factories import (
    FunctionCallLogFactory,
    FunctionDataOutputFactory,
    FunctionProtocolDefinitionFactory,
    ProtocolRunFactory,
    ResourceDefinitionFactory,
    ResourceFactory,
    WellDataOutputFactory,
    WorkcellFactory,
)

# Use PostgreSQL test database - NO SQLITE FALLBACK
# The application uses PostgreSQL-specific features (JSONB) that SQLite doesn't support.
# Tests must run against the actual production database to ensure compatibility.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test_user:test_password@127.0.0.1:5433/test_db",
)


@pytest.fixture(scope="session", autouse=True)
def docker_db(worker_id):
    """Starts the test database container before running tests and stops it afterwards.

    This fixture is session-scoped and autouse, so it runs automatically.

    When using pytest-xdist, only the master process manages the Docker container.
    Worker processes skip this fixture and connect to the existing database.
    """
    # Only run docker operations on the main worker or if not using xdist
    # worker_id is "master" when not using xdist or on the coordinator process
    if worker_id != "master":
        # We're a worker process - the master already started the DB
        yield
        return

    docker_compose_file = "docker-compose.test.yml"

    # Check if docker-compose file exists
    if not os.path.exists(docker_compose_file):
        print(f"Warning: {docker_compose_file} not found. Assuming DB is managed externally.")
        yield
        return

    # Start the DB
    try:
        subprocess.run(
            ["docker", "compose", "-f", docker_compose_file, "up", "-d", "test_db"],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        yield
        return

    # Wait for DB to be healthy
    max_retries = 30
    ready = False
    for _ in range(max_retries):
        try:
            # Check container health
            # Using 'wait' command if available is better, but 'up -d --wait' is cleaner if supported.
            # Re-running up with wait
            subprocess.run(
                ["docker", "compose", "-f", docker_compose_file, "up", "-d", "--wait", "test_db"],
                check=True,
                capture_output=True,
                timeout=2
            )
            ready = True
            break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
             time.sleep(1)

    if not ready:
        print("Warning: Timed out waiting for DB healthcheck. Tests might fail.")

    yield

    subprocess.run(
        ["docker", "compose", "-f", docker_compose_file, "down"],
        check=False,
        capture_output=True
    )




@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Creates a session-scoped test database engine.

    Session scope creates the database once for all tests, significantly
    speeding up test execution. Individual tests use transaction rollback
    to maintain isolation.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

    async with engine.begin() as conn:
        # Aggressively clean schema to prevent Type persistence errors
        # Explicitly drop the problematic enum type that persists
        await conn.execute(text("DROP TYPE IF EXISTS assettype CASCADE"))
        # Force drop all tables just in case, ignoring errors
        try:
            await conn.run_sync(Base.metadata.drop_all)
        except Exception:
            pass
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup: drop all tables after session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(
    db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Yields a single, transacted session for one test function.
    The transaction is rolled back after the test completes.

    Uses connection-level transactions to ensure proper rollback.
    This is a performance optimization: the database schema is created
    once per session (in db_engine), and each test gets a clean slate
    via transaction rollback instead of recreating tables.
    """
    async with db_engine.connect() as connection, connection.begin() as transaction:
        # Create session bound to this connection
        session = AsyncSession(bind=connection, expire_on_commit=False)

        # Set up factories to use this session
        WorkcellFactory._meta.sqlalchemy_session = session
        ResourceDefinitionFactory._meta.sqlalchemy_session = session
        ResourceFactory._meta.sqlalchemy_session = session
        FunctionProtocolDefinitionFactory._meta.sqlalchemy_session = session
        ProtocolRunFactory._meta.sqlalchemy_session = session
        FunctionCallLogFactory._meta.sqlalchemy_session = session
        FunctionDataOutputFactory._meta.sqlalchemy_session = session
        WellDataOutputFactory._meta.sqlalchemy_session = session

        try:
            yield session
        finally:
            # Clean up session and transaction
            # Catch all errors to prevent test failures from cleanup operations
            try:
                session.expunge_all()
            except Exception:
                pass

            try:
                await session.close()
            except Exception:
                pass

            # Rollback transaction, catching circular dependency errors
            # These can occur when tests delete objects with complex cascade relationships
            try:
                await transaction.rollback()
            except Exception:
                # Ignore rollback errors - transaction will be cleaned up when connection closes
                pass


# ============================================================================
# Auth Test Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create active test user with known password for auth testing.

    Username: testuser
    Password: testpass123
    Email: testuser@example.com
    Active: True
    """
    from praxis.backend.models.pydantic_internals.user import UserCreate
    from praxis.backend.services.user import UserService

    user_service = UserService(db_session)
    user_data = UserCreate(
        username="testuser",
        email="testuser@example.com",
        password="testpass123",
        is_active=True,
    )
    user = await user_service.create(db=db_session, obj_in=user_data)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_inactive_user(db_session: AsyncSession):
    """Create inactive test user for rejection testing.

    Username: inactiveuser
    Password: testpass123
    Email: inactive@example.com
    Active: False
    """
    from praxis.backend.models.pydantic_internals.user import UserCreate
    from praxis.backend.services.user import UserService

    user_service = UserService(db_session)
    user_data = UserCreate(
        username="inactiveuser",
        email="inactive@example.com",
        password="testpass123",
        is_active=False,
    )
    user = await user_service.create(db=db_session, obj_in=user_data)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def valid_auth_headers(test_user):
    """Generate valid Authorization headers for test_user.

    Returns:
        dict: {"Authorization": "Bearer <token>"}
    """
    from praxis.backend.utils.auth import create_access_token

    token = create_access_token(
        data={"sub": test_user.username, "user_id": str(test_user.accession_id)}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def expired_token(test_user):
    """Generate expired token for testing expiration handling.

    Creates a token that expired 1 second ago.

    Returns:
        str: Expired JWT token
    """
    from datetime import timedelta
    from praxis.backend.utils.auth import create_access_token

    return create_access_token(
        data={"sub": test_user.username, "user_id": str(test_user.accession_id)},
        expires_delta=timedelta(seconds=-1),
    )
