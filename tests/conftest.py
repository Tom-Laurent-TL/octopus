import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, UTC

from app.db.database import Base, get_db
from app.db.models import APIKey
from app.main import app, limiter
from app.core.config import settings
from app.core import security
from app.features.api_keys import router as api_keys_router

# Disable rate limiting for tests
limiter.enabled = False
security.limiter.enabled = False
api_keys_router.limiter.enabled = False

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Check if test API key already exists (for tests that use both client and db_session fixtures)
    existing_key = db.query(APIKey).filter(APIKey.key == settings.master_api_key).first()
    if not existing_key:
        # Create a test API key in the database
        test_api_key = APIKey(
            key=settings.master_api_key,
            name="Test API Key",
            description="API key for testing",
            scopes="admin,read,write",
            is_active=True,
            created_at=datetime.now(UTC)
        )
        db.add(test_api_key)
        db.commit()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create a test client with overridden dependencies."""
    Base.metadata.create_all(bind=engine)
    
    # Create a test API key in the database
    db = TestingSessionLocal()
    test_api_key = APIKey(
        key=settings.master_api_key,
        name="Test API Key",
        description="API key for testing",
        scopes="admin,read,write",
        is_active=True,
        created_at=datetime.now(UTC)
    )
    db.add(test_api_key)
    db.commit()
    db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def api_key():
    """Return the API key for authenticated requests."""
    return settings.master_api_key


@pytest.fixture
def auth_headers(api_key):
    """Return headers with API key authentication."""
    return {"Octopus-API-Key": api_key}
