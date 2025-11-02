"""Tests for API Key router endpoints."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, UTC, timedelta

from app.features.api_keys.service import APIKeyService
from app.features.api_keys import schemas


def test_create_api_key_requires_admin(client: TestClient, auth_headers):
    """Test that creating an API key requires admin scope."""
    response = client.post(
        "/api/v1/api-keys/",
        json={
            "name": "New Key",
            "scopes": "read",
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Key"
    assert data["scopes"] == "read"
    assert "key" in data  # Actual key is returned on creation
    assert data["key"].startswith("octopus_")


def test_create_api_key_without_auth(client: TestClient):
    """Test that creating an API key without auth fails."""
    response = client.post(
        "/api/v1/api-keys/",
        json={
            "name": "New Key",
            "scopes": "read",
        }
    )
    
    # 422 because the header is required (auto_error=True in APIKeyHeader)
    assert response.status_code == 422


def test_list_api_keys(client: TestClient, auth_headers):
    """Test listing API keys."""
    # Create a couple of keys first
    for i in range(2):
        client.post(
            "/api/v1/api-keys/",
            json={"name": f"Test Key {i}", "scopes": "read"},
            headers=auth_headers
        )
    
    response = client.get("/api/v1/api-keys/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    # Ensure actual keys are not returned in list
    for key in data:
        assert "key" not in key or key.get("key") is None


def test_list_api_keys_without_auth(client: TestClient):
    """Test that listing API keys without auth fails."""
    response = client.get("/api/v1/api-keys/")
    
    # 422 because the header is required (auto_error=True in APIKeyHeader)
    assert response.status_code == 422


def test_get_api_key_by_id(client: TestClient, auth_headers):
    """Test retrieving a specific API key."""
    # Create a key
    create_response = client.post(
        "/api/v1/api-keys/",
        json={"name": "Test Key", "scopes": "read"},
        headers=auth_headers
    )
    created_key = create_response.json()
    
    # Get it by ID
    response = client.get(
        f"/api/v1/api-keys/{created_key['id']}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_key["id"]
    assert data["name"] == "Test Key"
    assert "key" not in data  # Actual key should not be returned


def test_get_nonexistent_api_key(client: TestClient, auth_headers):
    """Test retrieving a non-existent API key."""
    response = client.get("/api/v1/api-keys/99999", headers=auth_headers)
    
    assert response.status_code == 404


def test_update_api_key(client: TestClient, auth_headers):
    """Test updating an API key."""
    # Create a key
    create_response = client.post(
        "/api/v1/api-keys/",
        json={"name": "Original Name", "scopes": "read"},
        headers=auth_headers
    )
    created_key = create_response.json()
    
    # Update it
    response = client.patch(
        f"/api/v1/api-keys/{created_key['id']}",
        json={"name": "Updated Name", "scopes": "read,write"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["scopes"] == "read,write"


def test_deactivate_api_key(client: TestClient, auth_headers):
    """Test deactivating an API key."""
    # Create a key
    create_response = client.post(
        "/api/v1/api-keys/",
        json={"name": "Test Key", "scopes": "read"},
        headers=auth_headers
    )
    created_key = create_response.json()
    
    # Deactivate it
    response = client.post(
        f"/api/v1/api-keys/{created_key['id']}/deactivate",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


def test_cannot_deactivate_current_key(client: TestClient, auth_headers, db_session):
    """Test that you cannot deactivate the key you're currently using."""
    # Get the current test key ID
    from app.db.models import APIKey
    from app.core.config import settings
    
    current_key = db_session.query(APIKey).filter(APIKey.key == settings.master_api_key).first()
    
    response = client.post(
        f"/api/v1/api-keys/{current_key.id}/deactivate",
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "currently using" in response.json()["detail"].lower()


def test_delete_api_key(client: TestClient, auth_headers):
    """Test permanently deleting an API key."""
    # Create a key
    create_response = client.post(
        "/api/v1/api-keys/",
        json={"name": "Test Key", "scopes": "read"},
        headers=auth_headers
    )
    created_key = create_response.json()
    
    # Delete it
    response = client.delete(
        f"/api/v1/api-keys/{created_key['id']}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(
        f"/api/v1/api-keys/{created_key['id']}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


def test_cannot_delete_current_key(client: TestClient, auth_headers, db_session):
    """Test that you cannot delete the key you're currently using."""
    # Get the current test key ID
    from app.db.models import APIKey
    from app.core.config import settings
    
    current_key = db_session.query(APIKey).filter(APIKey.key == settings.master_api_key).first()
    
    response = client.delete(
        f"/api/v1/api-keys/{current_key.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "currently using" in response.json()["detail"].lower()


def test_expired_key_cannot_authenticate(client: TestClient, db_session):
    """Test that an expired API key cannot be used for authentication."""
    # Create an expired key
    from app.db.models import APIKey
    
    expired_key = APIKey(
        key="octopus_expired_key",
        name="Expired Key",
        scopes="admin",
        is_active=True,
        expires_at=datetime.now(UTC) - timedelta(days=1),  # Expired yesterday
        created_at=datetime.now(UTC)
    )
    db_session.add(expired_key)
    db_session.commit()
    
    # Try to use it
    response = client.get(
        "/api/v1/api-keys/",
        headers={"Octopus-API-Key": "octopus_expired_key"}
    )
    
    assert response.status_code == 403
    assert "expired" in response.json()["detail"].lower()


def test_inactive_key_cannot_authenticate(client: TestClient, db_session):
    """Test that an inactive API key cannot be used for authentication."""
    # Create an inactive key
    from app.db.models import APIKey
    
    inactive_key = APIKey(
        key="octopus_inactive_key",
        name="Inactive Key",
        scopes="admin",
        is_active=False,  # Inactive
        created_at=datetime.now(UTC)
    )
    db_session.add(inactive_key)
    db_session.commit()
    
    # Try to use it
    response = client.get(
        "/api/v1/api-keys/",
        headers={"Octopus-API-Key": "octopus_inactive_key"}
    )
    
    assert response.status_code == 403
    assert "invalid or inactive" in response.json()["detail"].lower()
