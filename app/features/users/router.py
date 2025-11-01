from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.features.users import schemas
from app.features.users.service import UserService
from app.db.database import get_db
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user (public endpoint for registration)."""
    created_user = UserService.create_user(
        db,
        email=user.email,
        username=user.username,
        password=user.password,
        full_name=user.full_name
    )
    
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    return created_user


@router.get("/", response_model=List[schemas.UserPublic], dependencies=[Depends(verify_api_key)])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all users (protected endpoint)."""
    return UserService.list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.User, dependencies=[Depends(verify_api_key)])
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific user by ID (protected endpoint)."""
    user = UserService.get_user(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/username/{username}", response_model=schemas.UserPublic)
async def get_user_by_username(
    username: str,
    db: Session = Depends(get_db)
):
    """Get public user info by username (public endpoint)."""
    user = UserService.get_user_by_username(db, username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=schemas.User, dependencies=[Depends(verify_api_key)])
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """Update a user (protected endpoint)."""
    updated_user = UserService.update_user(
        db,
        user_id,
        email=user_update.email,
        username=user_update.username,
        full_name=user_update.full_name,
        password=user_update.password,
        is_active=user_update.is_active
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or email/username already taken"
        )
    
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_api_key)])
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete a user (protected endpoint)."""
    deleted = UserService.delete_user(db, user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return None
