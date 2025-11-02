"""Service layer for API Key management."""
import secrets
import json
from typing import List, Optional
from datetime import datetime, UTC, timedelta

from sqlalchemy.orm import Session

from app.db.models import APIKey, APIKeyAuditLog
from . import schemas


class AuditService:
    """Service for audit logging."""
    
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        api_key_id: Optional[int] = None,
        performed_by_key_id: Optional[int] = None,
        performed_by_ip: Optional[str] = None,
        details: Optional[dict] = None
    ) -> APIKeyAuditLog:
        """Log an API key action."""
        audit_entry = APIKeyAuditLog(
            api_key_id=api_key_id,
            action=action,
            performed_by_key_id=performed_by_key_id,
            performed_by_ip=performed_by_ip,
            details=json.dumps(details) if details else None,
            timestamp=datetime.now(UTC)
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry
    
    @staticmethod
    def get_audit_logs(
        db: Session,
        api_key_id: Optional[int] = None,
        action: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[APIKeyAuditLog]:
        """Get audit logs with optional filters."""
        query = db.query(APIKeyAuditLog)
        
        if api_key_id:
            query = query.filter(APIKeyAuditLog.api_key_id == api_key_id)
        
        if action:
            query = query.filter(APIKeyAuditLog.action == action)
        
        return query.order_by(APIKeyAuditLog.timestamp.desc()).offset(skip).limit(limit).all()


class APIKeyService:
    """Service for managing API keys."""
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure random API key."""
        # Generate a 32-byte (256-bit) random key and encode as hex
        return f"octopus_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def create_api_key(
        db: Session,
        api_key_data: schemas.APIKeyCreate,
        created_by_user_id: Optional[int] = None,
        performed_by_key_id: Optional[int] = None,
        performed_by_ip: Optional[str] = None
    ) -> APIKey:
        """Create a new API key."""
        # Generate the actual key
        key = APIKeyService.generate_api_key()
        
        db_api_key = APIKey(
            key=key,
            name=api_key_data.name,
            description=api_key_data.description,
            scopes=api_key_data.scopes,
            expires_at=api_key_data.expires_at,
            allowed_ips=api_key_data.allowed_ips,
            created_by_user_id=created_by_user_id,
            is_active=True,
            created_at=datetime.now(UTC)
        )
        
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        
        # Audit log
        AuditService.log_action(
            db=db,
            action="create",
            api_key_id=db_api_key.id,
            performed_by_key_id=performed_by_key_id,
            performed_by_ip=performed_by_ip,
            details={
                "name": db_api_key.name,
                "scopes": db_api_key.scopes,
                "expires_at": db_api_key.expires_at.isoformat() if db_api_key.expires_at else None
            }
        )
        
        return db_api_key
    
    @staticmethod
    def get_api_key_by_id(db: Session, api_key_id: int) -> Optional[APIKey]:
        """Get an API key by ID (without exposing the actual key)."""
        return db.query(APIKey).filter(APIKey.id == api_key_id).first()
    
    @staticmethod
    def get_api_keys(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[APIKey]:
        """Get all API keys."""
        query = db.query(APIKey)
        
        if not include_inactive:
            query = query.filter(APIKey.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_api_key(
        db: Session,
        api_key_id: int,
        api_key_update: schemas.APIKeyUpdate,
        performed_by_key_id: Optional[int] = None,
        performed_by_ip: Optional[str] = None
    ) -> Optional[APIKey]:
        """Update an API key."""
        db_api_key = APIKeyService.get_api_key_by_id(db, api_key_id)
        
        if not db_api_key:
            return None
        
        # Track changes for audit log
        changes = {}
        
        # Update only provided fields
        update_data = api_key_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            old_value = getattr(db_api_key, field)
            if old_value != value:
                changes[field] = {"old": str(old_value), "new": str(value)}
            setattr(db_api_key, field, value)
        
        db.commit()
        db.refresh(db_api_key)
        
        # Audit log if there were changes
        if changes:
            AuditService.log_action(
                db=db,
                action="update",
                api_key_id=api_key_id,
                performed_by_key_id=performed_by_key_id,
                performed_by_ip=performed_by_ip,
                details={"changes": changes}
            )
        
        return db_api_key
    
    @staticmethod
    def deactivate_api_key(
        db: Session,
        api_key_id: int,
        performed_by_key_id: Optional[int] = None,
        performed_by_ip: Optional[str] = None
    ) -> Optional[APIKey]:
        """Deactivate an API key (soft delete)."""
        db_api_key = APIKeyService.get_api_key_by_id(db, api_key_id)
        
        if not db_api_key:
            return None
        
        db_api_key.is_active = False
        db.commit()
        db.refresh(db_api_key)
        
        # Audit log
        AuditService.log_action(
            db=db,
            action="deactivate",
            api_key_id=api_key_id,
            performed_by_key_id=performed_by_key_id,
            performed_by_ip=performed_by_ip,
            details={"name": db_api_key.name}
        )
        
        return db_api_key
    
    @staticmethod
    def delete_api_key(
        db: Session,
        api_key_id: int,
        performed_by_key_id: Optional[int] = None,
        performed_by_ip: Optional[str] = None
    ) -> bool:
        """Permanently delete an API key."""
        db_api_key = APIKeyService.get_api_key_by_id(db, api_key_id)
        
        if not db_api_key:
            return False
        
        # Store name for audit log before deletion
        key_name = db_api_key.name
        
        # Audit log before deletion
        AuditService.log_action(
            db=db,
            action="delete",
            api_key_id=api_key_id,
            performed_by_key_id=performed_by_key_id,
            performed_by_ip=performed_by_ip,
            details={"name": key_name}
        )
        
        db.delete(db_api_key)
        db.commit()
        return True
    
    @staticmethod
    def verify_key_has_scope(api_key: APIKey, required_scope: str) -> bool:
        """Check if an API key has a specific scope."""
        scopes = [s.strip() for s in api_key.scopes.split(",")]
        return required_scope in scopes or "admin" in scopes
    
    @staticmethod
    def rotate_api_key(
        db: Session,
        old_key_id: int,
        performed_by_key_id: Optional[int] = None,
        performed_by_ip: Optional[str] = None
    ) -> Optional[APIKey]:
        """Rotate an API key - creates new key with same properties, deactivates old one."""
        old_key = APIKeyService.get_api_key_by_id(db, old_key_id)
        
        if not old_key:
            return None
        
        # Create new key with same properties
        new_key_data = schemas.APIKeyCreate(
            name=f"{old_key.name} (rotated)",
            description=old_key.description,
            scopes=old_key.scopes,
            expires_at=old_key.expires_at,
            allowed_ips=old_key.allowed_ips
        )
        
        new_key = APIKeyService.create_api_key(
            db=db,
            api_key_data=new_key_data,
            created_by_user_id=old_key.created_by_user_id,
            performed_by_key_id=performed_by_key_id,
            performed_by_ip=performed_by_ip
        )
        
        # Deactivate old key
        APIKeyService.deactivate_api_key(
            db=db,
            api_key_id=old_key_id,
            performed_by_key_id=performed_by_key_id,
            performed_by_ip=performed_by_ip
        )
        
        # Audit log for rotation
        AuditService.log_action(
            db=db,
            action="rotate",
            api_key_id=old_key_id,
            performed_by_key_id=performed_by_key_id,
            performed_by_ip=performed_by_ip,
            details={
                "old_key_id": old_key_id,
                "new_key_id": new_key.id,
                "old_key_name": old_key.name,
                "new_key_name": new_key.name
            }
        )
        
        return new_key
    
    @staticmethod
    def get_expiring_keys(db: Session, days: int = 7) -> List[APIKey]:
        """Get keys that will expire within specified days."""
        expiry_threshold = datetime.now(UTC) + timedelta(days=days)
        return db.query(APIKey).filter(
            APIKey.is_active == True,
            APIKey.expires_at.isnot(None),
            APIKey.expires_at <= expiry_threshold,
            APIKey.expires_at > datetime.now(UTC)
        ).all()
    
    @staticmethod
    def cleanup_expired_keys(
        db: Session,
        performed_by_key_id: Optional[int] = None,
        performed_by_ip: Optional[str] = None
    ) -> int:
        """Deactivate all expired keys. Returns count of deactivated keys."""
        expired_keys = db.query(APIKey).filter(
            APIKey.is_active == True,
            APIKey.expires_at.isnot(None),
            APIKey.expires_at <= datetime.now(UTC)
        ).all()
        
        count = 0
        for key in expired_keys:
            APIKeyService.deactivate_api_key(
                db=db,
                api_key_id=key.id,
                performed_by_key_id=performed_by_key_id,
                performed_by_ip=performed_by_ip
            )
            count += 1
        
        return count
