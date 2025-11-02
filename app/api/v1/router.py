from fastapi import APIRouter

from app.features.conversations.router import router as conversations_router
from app.features.users.router import router as users_router
from app.features.api_keys.router import router as api_keys_router

api_router = APIRouter()

# Include all feature routers
api_router.include_router(conversations_router)
api_router.include_router(users_router)
api_router.include_router(api_keys_router)
