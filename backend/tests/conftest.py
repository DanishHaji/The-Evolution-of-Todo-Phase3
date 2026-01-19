"""Pytest configuration and fixtures for Phase 3 tests."""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
import jwt
from datetime import datetime, timedelta
import os


@pytest.fixture(name="test_engine")
def test_engine_fixture():
    """Create SQLite in-memory engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="test_session")
def test_session_fixture(test_engine):
    """Create database session for testing."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="mock_jwt_secret", autouse=True)
def mock_jwt_secret_fixture(monkeypatch):
    """Mock JWT secret for testing."""
    secret = "test_secret_key_for_jwt_testing_only"
    # Set environment variable for any code that reads it at runtime
    monkeypatch.setenv("JWT_SECRET", secret)
    # Patch the JWT_SECRET in the auth module directly
    from app import auth
    monkeypatch.setattr(auth, "JWT_SECRET", secret)
    return secret


@pytest.fixture(name="mock_user_id")
def mock_user_id_fixture():
    """Mock user ID for testing."""
    return 1


@pytest.fixture(name="mock_jwt_token")
def mock_jwt_token_fixture(mock_jwt_secret, mock_user_id):
    """Generate mock JWT token for testing."""
    payload = {
        "sub": str(mock_user_id),  # JWT RFC 7519 requires sub to be a string
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, mock_jwt_secret, algorithm="HS256")
    return token


@pytest.fixture(name="expired_jwt_token")
def expired_jwt_token_fixture(mock_jwt_secret, mock_user_id):
    """Generate expired JWT token for testing."""
    payload = {
        "sub": str(mock_user_id),  # JWT RFC 7519 requires sub to be a string
        "exp": datetime.utcnow() - timedelta(days=1),  # Expired yesterday
        "iat": datetime.utcnow() - timedelta(days=8),
    }
    token = jwt.encode(payload, mock_jwt_secret, algorithm="HS256")
    return token


@pytest.fixture(name="test_user")
def test_user_fixture(test_session):
    """Create test user in database."""
    from app.models import User

    user = User(
        email="test@example.com",
        password_hash="hashed_password_here",
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture(name="test_task")
def test_task_fixture(test_session, test_user):
    """Create test task in database."""
    from app.models import Task

    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test task description",
        priority="high",
        tags=["test", "example"],
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    return task
