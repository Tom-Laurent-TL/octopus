import pytest
from datetime import datetime
from app.db import models


def test_create_conversation(db_session):
    """Test creating a conversation model."""
    conversation = models.Conversation(title="Test Chat")
    db_session.add(conversation)
    db_session.commit()
    
    assert conversation.id is not None
    assert conversation.title == "Test Chat"
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_create_message(db_session):
    """Test creating a message model."""
    # Create conversation first
    conversation = models.Conversation(title="Test")
    db_session.add(conversation)
    db_session.commit()
    
    # Create message
    message = models.Message(
        conversation_id=conversation.id,
        role="user",
        content="Hello world"
    )
    db_session.add(message)
    db_session.commit()
    
    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.role == "user"
    assert message.content == "Hello world"
    assert isinstance(message.created_at, datetime)


def test_conversation_message_relationship(db_session):
    """Test the relationship between conversations and messages."""
    # Create conversation
    conversation = models.Conversation(title="Test Chat")
    db_session.add(conversation)
    db_session.commit()
    
    # Add messages
    msg1 = models.Message(
        conversation_id=conversation.id,
        role="user",
        content="First message"
    )
    msg2 = models.Message(
        conversation_id=conversation.id,
        role="assistant",
        content="Second message"
    )
    db_session.add(msg1)
    db_session.add(msg2)
    db_session.commit()
    
    # Refresh conversation to load messages
    db_session.refresh(conversation)
    
    assert len(conversation.messages) == 2
    assert conversation.messages[0].content == "First message"
    assert conversation.messages[1].content == "Second message"


def test_cascade_delete(db_session):
    """Test that deleting a conversation deletes its messages."""
    # Create conversation with messages
    conversation = models.Conversation(title="Test")
    db_session.add(conversation)
    db_session.commit()
    
    msg = models.Message(
        conversation_id=conversation.id,
        role="user",
        content="Test"
    )
    db_session.add(msg)
    db_session.commit()
    
    conversation_id = conversation.id
    message_id = msg.id
    
    # Delete conversation
    db_session.delete(conversation)
    db_session.commit()
    
    # Verify conversation is deleted
    assert db_session.query(models.Conversation).filter_by(id=conversation_id).first() is None
    
    # Verify messages are also deleted
    assert db_session.query(models.Message).filter_by(id=message_id).first() is None
