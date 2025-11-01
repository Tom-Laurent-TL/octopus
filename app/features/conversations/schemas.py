from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# User info for conversations
class UserInfo(BaseModel):
    """Minimal user info for conversations."""
    id: int
    username: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)


# Message Schemas
class MessageBase(BaseModel):
    role: str  # 'user', 'assistant', 'system'
    content: str


class MessageCreate(MessageBase):
    user_id: Optional[int] = None  # Optional for backward compatibility


class Message(MessageBase):
    id: int
    conversation_id: int
    user_id: Optional[int] = None
    user: Optional[UserInfo] = None  # Include user info if available
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Conversation Schemas
class ConversationBase(BaseModel):
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    participant_ids: List[int] = []  # User IDs to add as participants


class ConversationUpdate(BaseModel):
    title: Optional[str] = None


class ConversationAddParticipant(BaseModel):
    user_id: int


class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    participants: List[UserInfo] = []
    messages: List[Message] = []
    
    model_config = ConfigDict(from_attributes=True)


class ConversationList(ConversationBase):
    """Simplified conversation for list views."""
    id: int
    created_at: datetime
    updated_at: datetime
    participants: List[UserInfo] = []
    message_count: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)
