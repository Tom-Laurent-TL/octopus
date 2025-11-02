"""Bootstrap endpoint for initial setup."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, UTC

from app.db.database import get_db
from app.db.models import APIKey
from app.core.config import settings
from app.features.api_keys.service import APIKeyService


router = APIRouter(tags=["bootstrap"])


@router.post("/bootstrap")
async def bootstrap(db: Session = Depends(get_db)):
    """
    Bootstrap the application with a master API key.
    
    This endpoint can only be called once - when no API keys exist in the database.
    Returns the master API key that should be saved securely.
    """
    # Check if any API keys already exist
    existing_keys = db.query(APIKey).count()
    
    if existing_keys > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Bootstrap already completed. Database has {existing_keys} API key(s). Use the existing master key to create additional keys."
        )
    
    # Create master API key from environment variable
    master_key = settings.master_api_key
    if master_key == "default-api-key":
        # Generate a new secure key if using default
        master_key = APIKeyService.generate_api_key()
    
    db_api_key = APIKey(
        key=master_key,
        name="Master API Key",
        description="Initial master key with full admin access",
        scopes="admin,read,write",
        is_active=True,
        created_at=datetime.now(UTC)
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return {
        "message": "Bootstrap successful! Save this API key securely - it will not be shown again.",
        "api_key": db_api_key.key,
        "name": db_api_key.name,
        "scopes": db_api_key.scopes,
        "instructions": {
            "1": "Add this key to your .env file: MASTER_API_KEY=<key>",
            "2": "Use this key in the Octopus-API-Key header for authenticated requests",
            "3": "Create additional keys via POST /api/v1/api-keys/ with this master key"
        }
    }
