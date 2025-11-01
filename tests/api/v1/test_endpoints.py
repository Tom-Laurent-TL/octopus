import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint(client: TestClient):
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_key_authentication(client: TestClient, auth_headers):
    """Test API key authentication works."""
    response = client.get("/api/v1/items/", headers=auth_headers)
    assert response.status_code == 200


def test_api_key_authentication_fails(client: TestClient):
    """Test that requests without API key fail."""
    response = client.get("/api/v1/items/")
    assert response.status_code == 422  # Missing required header


def test_api_key_authentication_invalid(client: TestClient):
    """Test that requests with invalid API key fail."""
    response = client.get("/api/v1/items/", headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 403


def test_users_endpoint(client: TestClient, auth_headers):
    """Test users endpoint (protected endpoint)."""
    response = client.get("/api/v1/users/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_items_endpoint_protected(client: TestClient, auth_headers):
    """Test items endpoint is protected."""
    response = client.get("/api/v1/items/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "plumbus" in data
    assert "gun" in data


def test_admin_endpoint_protected(client: TestClient, auth_headers):
    """Test admin endpoint is protected."""
    response = client.post("/api/v1/admin/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
