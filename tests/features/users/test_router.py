import pytest
from fastapi.testclient import TestClient


def test_create_user(client: TestClient):
    """Test creating a new user (public endpoint)."""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned


def test_create_user_duplicate_email(client: TestClient):
    """Test that creating a user with duplicate email fails."""
    # Create first user
    client.post(
        "/api/v1/users/",
        json={
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "pass123"
        }
    )
    
    # Try to create second user with same email
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "pass123"
        }
    )
    assert response.status_code == 400


def test_create_user_duplicate_username(client: TestClient):
    """Test that creating a user with duplicate username fails."""
    # Create first user
    client.post(
        "/api/v1/users/",
        json={
            "email": "user1@example.com",
            "username": "sameusername",
            "password": "pass123"
        }
    )
    
    # Try to create second user with same username
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "user2@example.com",
            "username": "sameusername",
            "password": "pass123"
        }
    )
    assert response.status_code == 400


def test_list_users(client: TestClient, auth_headers):
    """Test listing users (protected endpoint)."""
    # Create some users
    client.post("/api/v1/users/", json={"email": "user1@test.com", "username": "user1", "password": "pass"})
    client.post("/api/v1/users/", json={"email": "user2@test.com", "username": "user2", "password": "pass"})
    
    response = client.get("/api/v1/users/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_user(client: TestClient, auth_headers):
    """Test getting a specific user by ID (protected endpoint)."""
    # Create a user
    create_response = client.post(
        "/api/v1/users/",
        json={"email": "getuser@test.com", "username": "getuser", "password": "pass"}
    )
    user_id = create_response.json()["id"]
    
    # Get the user
    response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "getuser@test.com"


def test_get_nonexistent_user(client: TestClient, auth_headers):
    """Test getting a user that doesn't exist."""
    response = client.get("/api/v1/users/999", headers=auth_headers)
    assert response.status_code == 404


def test_get_user_by_username(client: TestClient):
    """Test getting public user info by username (public endpoint)."""
    # Create a user
    client.post(
        "/api/v1/users/",
        json={"email": "public@test.com", "username": "publicuser", "password": "pass", "full_name": "Public User"}
    )
    
    # Get by username
    response = client.get("/api/v1/users/username/publicuser")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "publicuser"
    assert data["full_name"] == "Public User"
    assert "email" not in data  # Should not expose email in public endpoint
    assert "hashed_password" not in data


def test_update_user(client: TestClient, auth_headers):
    """Test updating a user (protected endpoint)."""
    # Create a user
    create_response = client.post(
        "/api/v1/users/",
        json={"email": "update@test.com", "username": "updateuser", "password": "pass"}
    )
    user_id = create_response.json()["id"]
    
    # Update the user
    response = client.put(
        f"/api/v1/users/{user_id}",
        json={"full_name": "Updated Name", "email": "newemail@test.com"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == "newemail@test.com"


def test_delete_user(client: TestClient, auth_headers):
    """Test deleting a user (protected endpoint)."""
    # Create a user
    create_response = client.post(
        "/api/v1/users/",
        json={"email": "delete@test.com", "username": "deleteuser", "password": "pass"}
    )
    user_id = create_response.json()["id"]
    
    # Delete the user
    response = client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify user is deleted
    get_response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert get_response.status_code == 404
