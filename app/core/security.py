from typing import Annotated

from fastapi import Header, HTTPException
from fastapi.security import APIKeyHeader

from .config import settings

# Define API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def verify_api_key(x_api_key: Annotated[str, Header(alias="X-API-Key")]):
    """Verify the API key from the X-API-Key header."""
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=403, 
            detail="Invalid API Key"
        )
    return x_api_key
