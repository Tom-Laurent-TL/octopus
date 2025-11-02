from typing import Annotated
from datetime import datetime, UTC
import logging

from fastapi import Header, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import settings
from app.db.database import get_db
from app.db.models import APIKey

# Configure logging
logger = logging.getLogger(__name__)

# Define API Key header
api_key_header = APIKeyHeader(name="Octopus-API-Key", auto_error=True)

# Initialize rate limiter for authentication
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
async def verify_api_key(
    request: Request,
    octopus_api_key: Annotated[str, Header(alias="Octopus-API-Key")],
    db: Session = Depends(get_db)
):
    """Verify the API key from the Octopus-API-Key header with rate limiting."""
    client_ip = get_remote_address(request)
    
    # Check against database
    db_key = db.query(APIKey).filter(
        APIKey.key == octopus_api_key,
        APIKey.is_active == True
    ).first()
    
    if not db_key:
        # Log failed authentication attempt
        logger.warning(
            f"Failed authentication attempt",
            extra={
                "ip": client_ip,
                "key_prefix": octopus_api_key[:12] + "..." if len(octopus_api_key) > 12 else octopus_api_key,
                "reason": "invalid_or_inactive"
            }
        )
        raise HTTPException(
            status_code=403, 
            detail="Invalid or inactive API Key"
        )
    
    # Check if key has expired
    if db_key.expires_at:
        # Convert expires_at to UTC if it's naive
        expires_at = db_key.expires_at.replace(tzinfo=UTC) if db_key.expires_at.tzinfo is None else db_key.expires_at
        if expires_at < datetime.now(UTC):
            logger.warning(
                f"Expired key authentication attempt",
                extra={
                    "ip": client_ip,
                    "key_id": db_key.id,
                    "key_name": db_key.name,
                    "expired_at": expires_at.isoformat()
                }
            )
            raise HTTPException(
                status_code=403,
                detail="API Key has expired"
            )
    
    # Check IP whitelist if configured
    if db_key.allowed_ips:
        allowed_ips = [ip.strip() for ip in db_key.allowed_ips.split(",")]
        if client_ip not in allowed_ips:
            logger.warning(
                f"IP not in whitelist",
                extra={
                    "ip": client_ip,
                    "key_id": db_key.id,
                    "key_name": db_key.name,
                    "allowed_ips": allowed_ips
                }
            )
            raise HTTPException(
                status_code=403,
                detail="API Key not authorized from this IP address"
            )
    
    # Update last used timestamp and IP
    db_key.last_used_at = datetime.now(UTC)
    db_key.last_used_ip = client_ip
    db.commit()
    
    # Log successful authentication
    logger.info(
        f"Successful authentication",
        extra={
            "ip": client_ip,
            "key_id": db_key.id,
            "key_name": db_key.name,
            "scopes": db_key.scopes
        }
    )
    
    return db_key
