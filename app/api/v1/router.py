from fastapi import APIRouter, Depends

from app.features.conversations.router import router as conversations_router
from app.features.items.router import router as items_router
from app.features.users.router import router as users_router
from app.features.admin.router import router as admin_router
from app.core.security import verify_api_key

api_router = APIRouter()

# Include all feature routers
api_router.include_router(conversations_router)
api_router.include_router(items_router)
api_router.include_router(users_router)
api_router.include_router(
    admin_router, 
    prefix="/admin", 
    tags=["admin"],
    dependencies=[Depends(verify_api_key)]
)
