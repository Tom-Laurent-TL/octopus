import pytest
from fastapi.testclient import TestClient


def test_create_conversation(client: TestClient, auth_headers):
    """Test creating a new conversation."""
    response = client.post(
        "/api/v1/conversations/",
        json={"title": "Test Conversation"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Conversation"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_conversation_without_title(client: TestClient, auth_headers):
    """Test creating a conversation without a title."""
    response = client.post(
        "/api/v1/conversations/",
        json={},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] is None


def test_create_conversation_without_auth(client: TestClient):
    """Test that creating a conversation requires authentication."""
    response = client.post(
        "/api/v1/conversations/",
        json={"title": "Test"}
    )
    assert response.status_code == 422  # Missing required header


def test_list_conversations(client: TestClient, auth_headers):
    """Test listing all conversations."""
    # Create some conversations
    client.post("/api/v1/conversations/", json={"title": "Conv 1"}, headers=auth_headers)
    client.post("/api/v1/conversations/", json={"title": "Conv 2"}, headers=auth_headers)
    
    response = client.get("/api/v1/conversations/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Conv 1"
    assert data[1]["title"] == "Conv 2"


def test_get_conversation(client: TestClient, auth_headers):
    """Test getting a specific conversation."""
    # Create a conversation
    create_response = client.post(
        "/api/v1/conversations/",
        json={"title": "Test Conv"},
        headers=auth_headers
    )
    conversation_id = create_response.json()["id"]
    
    # Get the conversation
    response = client.get(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conversation_id
    assert data["title"] == "Test Conv"
    assert data["messages"] == []


def test_get_nonexistent_conversation(client: TestClient, auth_headers):
    """Test getting a conversation that doesn't exist."""
    response = client.get("/api/v1/conversations/999", headers=auth_headers)
    assert response.status_code == 404


def test_update_conversation(client: TestClient, auth_headers):
    """Test updating a conversation title."""
    # Create a conversation
    create_response = client.post(
        "/api/v1/conversations/",
        json={"title": "Original Title"},
        headers=auth_headers
    )
    conversation_id = create_response.json()["id"]
    
    # Update the conversation
    response = client.put(
        f"/api/v1/conversations/{conversation_id}",
        json={"title": "Updated Title"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


def test_delete_conversation(client: TestClient, auth_headers):
    """Test deleting a conversation."""
    # Create a conversation
    create_response = client.post(
        "/api/v1/conversations/",
        json={"title": "To Delete"},
        headers=auth_headers
    )
    conversation_id = create_response.json()["id"]
    
    # Delete the conversation
    response = client.delete(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_add_message(client: TestClient, auth_headers):
    """Test adding a message to a conversation."""
    # Create a conversation
    create_response = client.post(
        "/api/v1/conversations/",
        json={"title": "Chat"},
        headers=auth_headers
    )
    conversation_id = create_response.json()["id"]
    
    # Add a message
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Hello!"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "user"
    assert data["content"] == "Hello!"
    assert data["conversation_id"] == conversation_id


def test_add_message_invalid_role(client: TestClient, auth_headers):
    """Test that adding a message with invalid role fails."""
    # Create a conversation
    create_response = client.post(
        "/api/v1/conversations/",
        json={"title": "Chat"},
        headers=auth_headers
    )
    conversation_id = create_response.json()["id"]
    
    # Try to add a message with invalid role
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "invalid", "content": "Hello!"},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_get_messages(client: TestClient, auth_headers):
    """Test getting all messages from a conversation."""
    # Create a conversation
    create_response = client.post(
        "/api/v1/conversations/",
        json={"title": "Chat"},
        headers=auth_headers
    )
    conversation_id = create_response.json()["id"]
    
    # Add some messages
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Hello!"},
        headers=auth_headers
    )
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "assistant", "content": "Hi there!"},
        headers=auth_headers
    )
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "How are you?"},
        headers=auth_headers
    )
    
    # Get messages
    response = client.get(f"/api/v1/conversations/{conversation_id}/messages", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["role"] == "user"
    assert data[0]["content"] == "Hello!"
    assert data[1]["role"] == "assistant"
    assert data[2]["role"] == "user"


def test_full_conversation_flow(client: TestClient, auth_headers):
    """Test a complete conversation flow."""
    # Create conversation
    create_response = client.post(
        "/api/v1/conversations/",
        json={"title": "Complete Chat"},
        headers=auth_headers
    )
    conversation_id = create_response.json()["id"]
    
    # Add messages
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "What's the weather?"},
        headers=auth_headers
    )
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "assistant", "content": "I don't have access to weather data."},
        headers=auth_headers
    )
    
    # Get full conversation
    response = client.get(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Complete Chat"
    assert len(data["messages"]) == 2
    assert data["messages"][0]["content"] == "What's the weather?"
    assert data["messages"][1]["content"] == "I don't have access to weather data."


def test_delete_conversation_cascades_messages(client: TestClient, auth_headers):
    """Test that deleting a conversation also deletes its messages."""
    # Create conversation with messages
    create_response = client.post(
        "/api/v1/conversations/",
        json={"title": "To Delete"},
        headers=auth_headers
    )
    conversation_id = create_response.json()["id"]
    
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Test"},
        headers=auth_headers
    )
    
    # Delete conversation
    client.delete(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)
    
    # Verify messages are also gone
    response = client.get(f"/api/v1/conversations/{conversation_id}/messages", headers=auth_headers)
    assert response.status_code == 404


def test_add_message_with_user_id(client: TestClient, auth_headers, db_session):
    """Test adding a message with user_id tracking."""
    from app.features.users.service import UserService
    
    # Create a user
    user = UserService.create_user(db_session, "test@example.com", "testuser", "password", "Test User")
    
    # Create a conversation with the user as participant
    create_response = client.post(
        "/api/v1/conversations/",
        json={"title": "Chat", "participant_ids": [user.id]},
        headers=auth_headers
    )
    conversation_id = create_response.json()["id"]
    
    # Add a message with user_id
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Hello!", "user_id": user.id},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user.id
    assert data["user"]["username"] == "testuser"


def test_add_message_non_participant(client: TestClient, auth_headers, db_session):
    """Test that non-participants cannot add messages with their user_id."""
    from app.features.users.service import UserService
    
    # Create two users
    user1 = UserService.create_user(db_session, "user1@example.com", "user1", "password", "User One")
    user2 = UserService.create_user(db_session, "user2@example.com", "user2", "password", "User Two")
    
    # Create a conversation with only user1 as participant
    create_response = client.post(
        "/api/v1/conversations/",
        json={"title": "Chat", "participant_ids": [user1.id]},
        headers=auth_headers
    )
    conversation_id = create_response.json()["id"]
    
    # Try to add a message as user2 (who is not a participant)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Hello!", "user_id": user2.id},
        headers=auth_headers
    )
    assert response.status_code == 403
    assert "not a participant" in response.json()["detail"].lower()

