"""API endpoints for API Key management."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.database import get_db
from app.core.security import verify_api_key
from app.db.models import APIKey as APIKeyModel
from . import schemas
from .service import APIKeyService, AuditService

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("/", response_model=schemas.APIKeyWithKey, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_api_key(
    request: Request,
    api_key_data: schemas.APIKeyCreate,
    db: Session = Depends(get_db),
    current_key: APIKeyModel = Depends(verify_api_key)
):
    """
    Create a new API key.
    
    **Note:** The actual key value is only returned once during creation.
    Store it securely - you won't be able to retrieve it again.
    
    Requires: Admin scope
    Rate limit: 5 requests per minute
    """
    # Check if current key has admin scope
    if not APIKeyService.verify_key_has_scope(current_key, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required to create API keys"
        )
    
    db_api_key = APIKeyService.create_api_key(
        db=db,
        api_key_data=api_key_data,
        created_by_user_id=current_key.created_by_user_id,
        performed_by_key_id=current_key.id,
        performed_by_ip=get_remote_address(request)
    )
    return db_api_key


@router.get("/", response_model=List[schemas.APIKey])
def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_key: APIKeyModel = Depends(verify_api_key)
):
    """
    List all API keys.
    
    The actual key values are never returned after creation.
    
    Requires: Admin scope
    """
    # Check if current key has admin scope
    if not APIKeyService.verify_key_has_scope(current_key, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required to list API keys"
        )
    
    return APIKeyService.get_api_keys(
        db=db,
        skip=skip,
        limit=limit,
        include_inactive=include_inactive
    )


@router.get("/{api_key_id}", response_model=schemas.APIKey)
def get_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_key: APIKeyModel = Depends(verify_api_key)
):
    """
    Get details of a specific API key.
    
    The actual key value is not included in the response.
    
    Requires: Admin scope
    """
    # Check if current key has admin scope
    if not APIKeyService.verify_key_has_scope(current_key, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required to view API keys"
        )
    
    db_api_key = APIKeyService.get_api_key_by_id(db, api_key_id)
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return db_api_key


@router.patch("/{api_key_id}", response_model=schemas.APIKey)
def update_api_key(
    request: Request,
    api_key_id: int,
    api_key_update: schemas.APIKeyUpdate,
    db: Session = Depends(get_db),
    current_key: APIKeyModel = Depends(verify_api_key)
):
    """
    Update an API key's metadata.
    
    You can update the name, description, scopes, active status, expiration, and allowed IPs.
    The actual key value cannot be changed.
    
    Requires: Admin scope
    """
    # Check if current key has admin scope
    if not APIKeyService.verify_key_has_scope(current_key, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required to update API keys"
        )
    
    db_api_key = APIKeyService.update_api_key(
        db, 
        api_key_id, 
        api_key_update,
        performed_by_key_id=current_key.id,
        performed_by_ip=get_remote_address(request)
    )
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return db_api_key


@router.post("/{api_key_id}/deactivate", response_model=schemas.APIKey)
def deactivate_api_key(
    request: Request,
    api_key_id: int,
    db: Session = Depends(get_db),
    current_key: APIKeyModel = Depends(verify_api_key)
):
    """
    Deactivate an API key (soft delete).
    
    The key will no longer work for authentication but remains in the database
    for audit purposes.
    
    Requires: Admin scope
    """
    # Check if current key has admin scope
    if not APIKeyService.verify_key_has_scope(current_key, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required to deactivate API keys"
        )
    
    # Prevent deactivating the current key
    if current_key.id == api_key_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate the API key you're currently using"
        )
    
    db_api_key = APIKeyService.deactivate_api_key(
        db, 
        api_key_id,
        performed_by_key_id=current_key.id,
        performed_by_ip=get_remote_address(request)
    )
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return db_api_key


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    request: Request,
    api_key_id: int,
    db: Session = Depends(get_db),
    current_key: APIKeyModel = Depends(verify_api_key)
):
    """
    Permanently delete an API key.
    
    **Warning:** This action cannot be undone. Consider deactivating instead.
    
    Requires: Admin scope
    """
    # Check if current key has admin scope
    if not APIKeyService.verify_key_has_scope(current_key, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required to delete API keys"
        )
    
    # Prevent deleting the current key
    if current_key.id == api_key_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the API key you're currently using"
        )
    
    success = APIKeyService.delete_api_key(
        db, 
        api_key_id,
        performed_by_key_id=current_key.id,
        performed_by_ip=get_remote_address(request)
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )


@router.post("/{api_key_id}/rotate", response_model=schemas.APIKeyWithKey)
def rotate_api_key(
    request: Request,
    api_key_id: int,
    db: Session = Depends(get_db),
    current_key: APIKeyModel = Depends(verify_api_key)
):
    """
    Rotate an API key.
    
    Creates a new key with the same properties as the old one and deactivates the old key.
    The new key is returned with its value (only shown once).
    
    **Use case:** Regular key rotation for security best practices.
    
    Requires: Admin scope
    """
    # Check if current key has admin scope
    if not APIKeyService.verify_key_has_scope(current_key, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required to rotate API keys"
        )
    
    new_key = APIKeyService.rotate_api_key(
        db,
        api_key_id,
        performed_by_key_id=current_key.id,
        performed_by_ip=get_remote_address(request)
    )
    
    if not new_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return new_key


@router.get("/audit-logs/", response_model=List[schemas.APIKeyAuditLog])
def get_audit_logs(
    api_key_id: int = None,
    action: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_key: APIKeyModel = Depends(verify_api_key)
):
    """
    Get audit logs for API key operations.
    
    Optional filters: api_key_id, action
    
    Requires: Admin scope
    """
    # Check if current key has admin scope
    if not APIKeyService.verify_key_has_scope(current_key, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required to view audit logs"
        )
    
    return AuditService.get_audit_logs(
        db=db,
        api_key_id=api_key_id,
        action=action,
        skip=skip,
        limit=limit
    )


@router.get("/expiring/", response_model=List[schemas.APIKey])
def get_expiring_keys(
    days: int = 7,
    db: Session = Depends(get_db),
    current_key: APIKeyModel = Depends(verify_api_key)
):
    """
    Get API keys that will expire within the specified number of days.
    
    Default: 7 days
    
    Requires: Admin scope
    """
    # Check if current key has admin scope
    if not APIKeyService.verify_key_has_scope(current_key, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required to view expiring keys"
        )
    
    return APIKeyService.get_expiring_keys(db, days)


@router.post("/cleanup-expired/", status_code=status.HTTP_200_OK)
def cleanup_expired_keys(
    request: Request,
    db: Session = Depends(get_db),
    current_key: APIKeyModel = Depends(verify_api_key)
):
    """
    Deactivate all expired API keys.
    
    Returns the count of deactivated keys.
    
    Requires: Admin scope
    """
    # Check if current key has admin scope
    if not APIKeyService.verify_key_has_scope(current_key, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required to cleanup expired keys"
        )
    
    count = APIKeyService.cleanup_expired_keys(
        db,
        performed_by_key_id=current_key.id,
        performed_by_ip=get_remote_address(request)
    )
    
    return {"deactivated_count": count, "message": f"Deactivated {count} expired key(s)"}
