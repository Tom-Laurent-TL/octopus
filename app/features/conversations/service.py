from typing import List, Optional
from sqlalchemy.orm import Session

from app.db import models


class ConversationService:
    """Service layer for conversation operations."""
    
    @staticmethod
    def get_conversation(db: Session, conversation_id: int) -> Optional[models.Conversation]:
        """Get a conversation by ID."""
        return db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id
        ).first()
    
    @staticmethod
    def list_conversations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Conversation]:
        """List all conversations with pagination."""
        return db.query(models.Conversation).offset(skip).limit(limit).all()
    
    @staticmethod
    def list_user_conversations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Conversation]:
        """List all conversations for a specific user."""
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return []
        return user.conversations[skip:skip + limit]
    
    @staticmethod
    def create_conversation(
        db: Session, 
        title: Optional[str] = None,
        participant_ids: List[int] = None
    ) -> models.Conversation:
        """Create a new conversation with optional participants."""
        conversation = models.Conversation(title=title)
        
        # Add participants if provided
        if participant_ids:
            users = db.query(models.User).filter(models.User.id.in_(participant_ids)).all()
            conversation.participants.extend(users)
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def add_participant(
        db: Session, 
        conversation_id: int, 
        user_id: int
    ) -> Optional[models.Conversation]:
        """Add a user to a conversation."""
        conversation = ConversationService.get_conversation(db, conversation_id)
        if not conversation:
            return None
        
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return None
        
        # Check if user is already a participant
        if user not in conversation.participants:
            conversation.participants.append(user)
            db.commit()
            db.refresh(conversation)
        
        return conversation
    
    @staticmethod
    def remove_participant(
        db: Session, 
        conversation_id: int, 
        user_id: int
    ) -> Optional[models.Conversation]:
        """Remove a user from a conversation."""
        conversation = ConversationService.get_conversation(db, conversation_id)
        if not conversation:
            return None
        
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return None
        
        if user in conversation.participants:
            conversation.participants.remove(user)
            db.commit()
            db.refresh(conversation)
        
        return conversation
    
    @staticmethod
    def update_conversation(
        db: Session, 
        conversation_id: int, 
        title: Optional[str] = None
    ) -> Optional[models.Conversation]:
        """Update a conversation."""
        conversation = ConversationService.get_conversation(db, conversation_id)
        if not conversation:
            return None
        
        if title is not None:
            conversation.title = title
        
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: int) -> bool:
        """Delete a conversation. Returns True if deleted, False if not found."""
        conversation = ConversationService.get_conversation(db, conversation_id)
        if not conversation:
            return False
        
        db.delete(conversation)
        db.commit()
        return True


class MessageService:
    """Service layer for message operations."""
    
    @staticmethod
    def get_messages(
        db: Session, 
        conversation_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.Message]:
        """Get all messages from a conversation."""
        return db.query(models.Message).filter(
            models.Message.conversation_id == conversation_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def add_message(
        db: Session, 
        conversation_id: int, 
        role: str, 
        content: str,
        user_id: Optional[int] = None
    ) -> models.Message:
        """Add a message to a conversation."""
        message = models.Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            user_id=user_id
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
