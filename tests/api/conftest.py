from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from praxis.backend.main import app
from praxis.backend.utils.db import SessionLocal, create_tables_if_not_exist, engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_database_session() -> None:
    """Create test tables once per session."""
    create_tables_if_not_exist()
    # Base.metadata.drop_all(bind=engine) # Uncomment if you want to drop tables after all tests

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provides a test database session, rolling back changes after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provides a TestClient instance for FastAPI, with DB session override."""
    from praxis.backend.api.dependencies import get_db

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    del app.dependency_overrides[get_db]
