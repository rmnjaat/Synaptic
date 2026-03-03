"""
pytest fixtures: fresh in-memory SQLite DB per test via dependency override.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app
from app.database import get_db, Base

# Import all models so their tables are registered
import app.models.user  # noqa
import app.models.topic  # noqa
import app.models.subtopic  # noqa
import app.models.note  # noqa
import app.models.resource  # noqa
import app.models.project  # noqa
import app.models.streak  # noqa


@pytest.fixture()
def db_session():
    """Creates a brand-new in-memory database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """TestClient wired to the test DB session."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


# ── Small helper fixture: seed a user directly ────────────────────────────────
@pytest.fixture()
def seed_user(db_session):
    from app.models.user import User
    user = User(username="testuser", email="test@example.com", display_name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
