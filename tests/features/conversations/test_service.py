import pytest
from sqlalchemy.orm import Session

from app.features.conversations.service import ConversationService, MessageService
from app.features.users.service import UserService
from app.db import models


def test_create_conversation_service(db_session: Session):
    """Test creating a conversation via service."""
    conversation = ConversationService.create_conversation(db_session, title="Test")
    
    assert conversation.id is not None
    assert conversation.title == "Test"
    assert len(conversation.participants) == 0


def test_create_conversation_with_participants(db_session: Session):
    """Test creating a conversation with participants."""
    # Create users
    user1 = UserService.create_user(db_session, "user1@test.com", "user1", "password", "User One")
    user2 = UserService.create_user(db_session, "user2@test.com", "user2", "password", "User Two")
    
    # Create conversation with participants
    conversation = ConversationService.create_conversation(
        db_session, 
        title="Group Chat",
        participant_ids=[user1.id, user2.id]
    )
    
    assert conversation.id is not None
    assert len(conversation.participants) == 2
    assert user1 in conversation.participants
    assert user2 in conversation.participants


def test_get_conversation_service(db_session: Session):
    """Test getting a conversation via service."""
    # Create a conversation
    created = ConversationService.create_conversation(db_session, title="Test")
    
    # Get it back
    conversation = ConversationService.get_conversation(db_session, created.id)
    
    assert conversation is not None
    assert conversation.id == created.id
    assert conversation.title == "Test"


def test_get_nonexistent_conversation_service(db_session: Session):
    """Test getting a conversation that doesn't exist."""
    conversation = ConversationService.get_conversation(db_session, 999)
    assert conversation is None


def test_list_conversations_service(db_session: Session):
    """Test listing conversations via service."""
    ConversationService.create_conversation(db_session, title="Conv 1")
    ConversationService.create_conversation(db_session, title="Conv 2")
    
    conversations = ConversationService.list_conversations(db_session)
    
    assert len(conversations) == 2


def test_list_conversations_with_pagination(db_session: Session):
    """Test listing conversations with pagination."""
    for i in range(5):
        ConversationService.create_conversation(db_session, title=f"Conv {i}")
    
    conversations = ConversationService.list_conversations(db_session, skip=2, limit=2)
    
    assert len(conversations) == 2


def test_update_conversation_service(db_session: Session):
    """Test updating a conversation via service."""
    conversation = ConversationService.create_conversation(db_session, title="Original")
    
    updated = ConversationService.update_conversation(
        db_session, 
        conversation.id, 
        title="Updated"
    )
    
    assert updated is not None
    assert updated.title == "Updated"


def test_update_nonexistent_conversation_service(db_session: Session):
    """Test updating a conversation that doesn't exist."""
    result = ConversationService.update_conversation(db_session, 999, title="Test")
    assert result is None


def test_delete_conversation_service(db_session: Session):
    """Test deleting a conversation via service."""
    conversation = ConversationService.create_conversation(db_session, title="To Delete")
    
    deleted = ConversationService.delete_conversation(db_session, conversation.id)
    
    assert deleted is True
    
    # Verify it's gone
    result = ConversationService.get_conversation(db_session, conversation.id)
    assert result is None


def test_delete_nonexistent_conversation_service(db_session: Session):
    """Test deleting a conversation that doesn't exist."""
    deleted = ConversationService.delete_conversation(db_session, 999)
    assert deleted is False


def test_add_message_service(db_session: Session):
    """Test adding a message via service."""
    conversation = ConversationService.create_conversation(db_session, title="Chat")
    
    message = MessageService.add_message(
        db_session,
        conversation_id=conversation.id,
        role="user",
        content="Hello!"
    )
    
    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.role == "user"
    assert message.content == "Hello!"


def test_get_messages_service(db_session: Session):
    """Test getting messages via service."""
    conversation = ConversationService.create_conversation(db_session, title="Chat")
    
    MessageService.add_message(db_session, conversation.id, "user", "Message 1")
    MessageService.add_message(db_session, conversation.id, "assistant", "Message 2")
    
    messages = MessageService.get_messages(db_session, conversation.id)
    
    assert len(messages) == 2
    assert messages[0].content == "Message 1"
    assert messages[1].content == "Message 2"


def test_add_message_with_user_id(db_session: Session):
    """Test adding a message with user_id tracking."""
    user = UserService.create_user(db_session, "user@test.com", "user", "password", "User")
    conversation = ConversationService.create_conversation(
        db_session, 
        title="Chat",
        participant_ids=[user.id]
    )
    
    message = MessageService.add_message(
        db_session,
        conversation_id=conversation.id,
        role="user",
        content="Hello from user!",
        user_id=user.id
    )
    
    assert message.id is not None
    assert message.user_id == user.id
    assert message.user is not None
    assert message.user.username == "user"


def test_add_participant_service(db_session: Session):
    """Test adding a participant to a conversation."""
    user = UserService.create_user(db_session, "user@test.com", "user", "password", "User")
    conversation = ConversationService.create_conversation(db_session, title="Chat")
    
    # Add participant
    updated = ConversationService.add_participant(db_session, conversation.id, user.id)
    
    assert updated is not None
    assert len(updated.participants) == 1
    assert user in updated.participants


def test_add_participant_already_in_conversation(db_session: Session):
    """Test adding a participant who is already in the conversation."""
    user = UserService.create_user(db_session, "user@test.com", "user", "password", "User")
    conversation = ConversationService.create_conversation(
        db_session, 
        title="Chat",
        participant_ids=[user.id]
    )
    
    # Try to add again
    updated = ConversationService.add_participant(db_session, conversation.id, user.id)
    
    assert updated is not None
    assert len(updated.participants) == 1  # Should still be 1


def test_add_participant_nonexistent_conversation(db_session: Session):
    """Test adding a participant to a non-existent conversation."""
    user = UserService.create_user(db_session, "user@test.com", "user", "password", "User")
    result = ConversationService.add_participant(db_session, 999, user.id)
    
    assert result is None


def test_add_participant_nonexistent_user(db_session: Session):
    """Test adding a non-existent user to a conversation."""
    conversation = ConversationService.create_conversation(db_session, title="Chat")
    result = ConversationService.add_participant(db_session, conversation.id, 999)
    
    assert result is None


def test_remove_participant_service(db_session: Session):
    """Test removing a participant from a conversation."""
    user = UserService.create_user(db_session, "user@test.com", "user", "password", "User")
    conversation = ConversationService.create_conversation(
        db_session, 
        title="Chat",
        participant_ids=[user.id]
    )
    
    # Remove participant
    updated = ConversationService.remove_participant(db_session, conversation.id, user.id)
    
    assert updated is not None
    assert len(updated.participants) == 0


def test_remove_participant_not_in_conversation(db_session: Session):
    """Test removing a participant who is not in the conversation."""
    user = UserService.create_user(db_session, "user@test.com", "user", "password", "User")
    conversation = ConversationService.create_conversation(db_session, title="Chat")
    
    # Try to remove user who was never added
    updated = ConversationService.remove_participant(db_session, conversation.id, user.id)
    
    assert updated is not None
    assert len(updated.participants) == 0


def test_list_user_conversations_service(db_session: Session):
    """Test listing conversations for a specific user."""
    user1 = UserService.create_user(db_session, "user1@test.com", "user1", "password", "User One")
    user2 = UserService.create_user(db_session, "user2@test.com", "user2", "password", "User Two")
    
    # Create conversations with different participants
    conv1 = ConversationService.create_conversation(db_session, "Conv 1", participant_ids=[user1.id])
    conv2 = ConversationService.create_conversation(db_session, "Conv 2", participant_ids=[user1.id, user2.id])
    conv3 = ConversationService.create_conversation(db_session, "Conv 3", participant_ids=[user2.id])
    
    # Get user1's conversations
    user1_convs = ConversationService.list_user_conversations(db_session, user1.id)
    
    assert len(user1_convs) == 2
    assert conv1 in user1_convs
    assert conv2 in user1_convs
    assert conv3 not in user1_convs


def test_list_user_conversations_nonexistent_user(db_session: Session):
    """Test listing conversations for a non-existent user."""
    conversations = ConversationService.list_user_conversations(db_session, 999)
    assert conversations == []


def test_get_messages_with_pagination(db_session: Session):
    """Test getting messages with pagination."""
    conversation = ConversationService.create_conversation(db_session, title="Chat")
    
    for i in range(5):
        MessageService.add_message(db_session, conversation.id, "user", f"Message {i}")
    
    messages = MessageService.get_messages(db_session, conversation.id, skip=2, limit=2)
    
    assert len(messages) == 2
