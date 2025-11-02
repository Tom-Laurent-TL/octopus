from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship

from app.db.database import Base


def utcnow():
    """Get current UTC time."""
    return datetime.now(UTC)


# Association table for many-to-many relationship between users and conversations
conversation_participants = Table(
    'conversation_participants',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('conversation_id', Integer, ForeignKey('conversations.id'), primary_key=True),
    Column('joined_at', DateTime, default=utcnow, nullable=False)
)


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    
    # Relationships
    conversations = relationship(
        "Conversation",
        secondary=conversation_participants,
        back_populates="participants"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class Conversation(Base):
    """Chat conversation model."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    
    # Relationships
    participants = relationship(
        "User",
        secondary=conversation_participants,
        back_populates="conversations"
    )
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"


class Message(Base):
    """Chat message model."""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # User who sent the message
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, user_id={self.user_id}, conversation_id={self.conversation_id})>"


class APIKey(Base):
    """API Key model for authentication."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)  # Friendly name for the key
    description = Column(Text, nullable=True)  # Optional description
    scopes = Column(String(500), nullable=False, default="read")  # Comma-separated scopes
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    last_used_ip = Column(String(45), nullable=True)  # IPv4 or IPv6 address
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    allowed_ips = Column(Text, nullable=True)  # Comma-separated list of allowed IPs
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, name={self.name}, is_active={self.is_active})>"


class APIKeyAuditLog(Base):
    """Audit log for API Key operations."""
    __tablename__ = "api_key_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)  # Nullable for failed lookups
    action = Column(String(50), nullable=False)  # create, update, delete, deactivate, auth_success, auth_failed
    performed_by_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)  # Which key performed the action
    performed_by_ip = Column(String(45), nullable=True)  # IP address of the request
    details = Column(Text, nullable=True)  # JSON string with additional details
    timestamp = Column(DateTime, default=utcnow, nullable=False, index=True)
    
    # Relationships
    api_key = relationship("APIKey", foreign_keys=[api_key_id])
    performed_by = relationship("APIKey", foreign_keys=[performed_by_key_id])
    
    def __repr__(self):
        return f"<APIKeyAuditLog(id={self.id}, action={self.action}, timestamp={self.timestamp})>"
