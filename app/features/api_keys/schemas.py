"""Pydantic schemas for API Key management."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class APIKeyBase(BaseModel):
    """Base schema for API Key."""
    name: str = Field(..., min_length=1, max_length=255, description="Friendly name for the API key")
    description: Optional[str] = Field(None, description="Optional description of the API key purpose")
    scopes: str = Field(default="read", description="Comma-separated list of scopes (e.g., 'read,write,admin')")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")
    allowed_ips: Optional[str] = Field(None, description="Comma-separated list of allowed IP addresses")


class APIKeyCreate(APIKeyBase):
    """Schema for creating a new API Key."""
    pass


class APIKeyUpdate(BaseModel):
    """Schema for updating an API Key."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scopes: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    allowed_ips: Optional[str] = None


class APIKey(APIKeyBase):
    """Schema for API Key response (without the actual key)."""
    id: int
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    last_used_ip: Optional[str]
    created_by_user_id: Optional[int]
    
    model_config = {"from_attributes": True}


class APIKeyWithKey(APIKey):
    """Schema for API Key response with the actual key (only shown once on creation)."""
    key: str
    
    model_config = {"from_attributes": True}


class APIKeyAuditLog(BaseModel):
    """Schema for API Key audit log entry."""
    id: int
    api_key_id: Optional[int]
    action: str
    performed_by_key_id: Optional[int]
    performed_by_ip: Optional[str]
    details: Optional[str]
    timestamp: datetime
    
    model_config = {"from_attributes": True}
