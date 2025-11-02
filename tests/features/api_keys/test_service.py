"""Tests for API Key service layer."""
import pytest
from datetime import datetime, UTC, timedelta

from app.features.api_keys.service import APIKeyService
from app.features.api_keys import schemas
from app.db.models import APIKey


def test_generate_api_key():
    """Test API key generation."""
    key = APIKeyService.generate_api_key()
    
    assert key.startswith("octopus_")
    assert len(key) > 20  # Should be reasonably long


def test_create_api_key(db_session):
    """Test creating a new API key."""
    api_key_data = schemas.APIKeyCreate(
        name="Test Key",
        description="A test API key",
        scopes="read,write"
    )
    
    db_api_key = APIKeyService.create_api_key(db_session, api_key_data)
    
    assert db_api_key.id is not None
    assert db_api_key.name == "Test Key"
    assert db_api_key.description == "A test API key"
    assert db_api_key.scopes == "read,write"
    assert db_api_key.is_active is True
    assert db_api_key.key.startswith("octopus_")


def test_create_api_key_with_expiration(db_session):
    """Test creating an API key with expiration date."""
    expires_at = datetime.now(UTC) + timedelta(days=30)
    api_key_data = schemas.APIKeyCreate(
        name="Temporary Key",
        scopes="read",
        expires_at=expires_at
    )
    
    db_api_key = APIKeyService.create_api_key(db_session, api_key_data)
    
    assert db_api_key.expires_at is not None
    # SQLite doesn't store timezone, so compare as naive datetimes
    db_expires_naive = db_api_key.expires_at.replace(tzinfo=None) if db_api_key.expires_at.tzinfo else db_api_key.expires_at
    expires_naive = expires_at.replace(tzinfo=None)
    assert abs((db_expires_naive - expires_naive).total_seconds()) < 1


def test_get_api_key_by_id(db_session):
    """Test retrieving an API key by ID."""
    # Create a key first
    api_key_data = schemas.APIKeyCreate(name="Test Key", scopes="read")
    created_key = APIKeyService.create_api_key(db_session, api_key_data)
    
    # Retrieve it
    retrieved_key = APIKeyService.get_api_key_by_id(db_session, created_key.id)
    
    assert retrieved_key is not None
    assert retrieved_key.id == created_key.id
    assert retrieved_key.name == "Test Key"


def test_get_api_keys(db_session):
    """Test listing all API keys."""
    # Create multiple keys
    for i in range(3):
        api_key_data = schemas.APIKeyCreate(name=f"Test Key {i}", scopes="read")
        APIKeyService.create_api_key(db_session, api_key_data)
    
    # Retrieve all
    keys = APIKeyService.get_api_keys(db_session)
    
    # Should include the test key from conftest + 3 new ones
    assert len(keys) >= 3


def test_get_api_keys_exclude_inactive(db_session):
    """Test that inactive keys are excluded by default."""
    # Create active key
    api_key_data = schemas.APIKeyCreate(name="Active Key", scopes="read")
    active_key = APIKeyService.create_api_key(db_session, api_key_data)
    
    # Create inactive key
    api_key_data = schemas.APIKeyCreate(name="Inactive Key", scopes="read")
    inactive_key = APIKeyService.create_api_key(db_session, api_key_data)
    APIKeyService.deactivate_api_key(db_session, inactive_key.id)
    
    # Get only active keys
    active_keys = APIKeyService.get_api_keys(db_session, include_inactive=False)
    active_key_ids = [key.id for key in active_keys]
    
    assert active_key.id in active_key_ids
    assert inactive_key.id not in active_key_ids


def test_update_api_key(db_session):
    """Test updating an API key."""
    # Create a key
    api_key_data = schemas.APIKeyCreate(name="Original Name", scopes="read")
    db_api_key = APIKeyService.create_api_key(db_session, api_key_data)
    
    # Update it
    update_data = schemas.APIKeyUpdate(
        name="Updated Name",
        scopes="read,write"
    )
    updated_key = APIKeyService.update_api_key(db_session, db_api_key.id, update_data)
    
    assert updated_key.name == "Updated Name"
    assert updated_key.scopes == "read,write"
    assert updated_key.key == db_api_key.key  # Key itself shouldn't change


def test_deactivate_api_key(db_session):
    """Test deactivating an API key."""
    # Create a key
    api_key_data = schemas.APIKeyCreate(name="Test Key", scopes="read")
    db_api_key = APIKeyService.create_api_key(db_session, api_key_data)
    
    assert db_api_key.is_active is True
    
    # Deactivate it
    deactivated_key = APIKeyService.deactivate_api_key(db_session, db_api_key.id)
    
    assert deactivated_key.is_active is False


def test_delete_api_key(db_session):
    """Test permanently deleting an API key."""
    # Create a key
    api_key_data = schemas.APIKeyCreate(name="Test Key", scopes="read")
    db_api_key = APIKeyService.create_api_key(db_session, api_key_data)
    key_id = db_api_key.id
    
    # Delete it
    success = APIKeyService.delete_api_key(db_session, key_id)
    
    assert success is True
    
    # Verify it's gone
    deleted_key = APIKeyService.get_api_key_by_id(db_session, key_id)
    assert deleted_key is None


def test_verify_key_has_scope():
    """Test scope verification."""
    # Create a mock API key
    api_key = APIKey(
        key="test_key",
        name="Test",
        scopes="read,write",
        is_active=True,
        created_at=datetime.now(UTC)
    )
    
    assert APIKeyService.verify_key_has_scope(api_key, "read") is True
    assert APIKeyService.verify_key_has_scope(api_key, "write") is True
    assert APIKeyService.verify_key_has_scope(api_key, "admin") is False


def test_verify_key_has_admin_scope():
    """Test that admin scope grants all permissions."""
    # Create a mock API key with admin scope
    api_key = APIKey(
        key="test_key",
        name="Test",
        scopes="admin",
        is_active=True,
        created_at=datetime.now(UTC)
    )
    
    assert APIKeyService.verify_key_has_scope(api_key, "read") is True
    assert APIKeyService.verify_key_has_scope(api_key, "write") is True
    assert APIKeyService.verify_key_has_scope(api_key, "admin") is True
    assert APIKeyService.verify_key_has_scope(api_key, "anything") is True
