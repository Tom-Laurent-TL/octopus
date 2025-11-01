from typing import List, Optional
from sqlalchemy.orm import Session
import bcrypt

from app.db import models


class UserService:
    """Service layer for user operations."""
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[models.User]:
        """Get a user by ID."""
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        """Get a user by email."""
        return db.query(models.User).filter(models.User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
        """Get a user by username."""
        return db.query(models.User).filter(models.User.username == username).first()
    
    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
        """List all users with pagination."""
        return db.query(models.User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(
        db: Session, 
        email: str, 
        username: str, 
        password: str,
        full_name: Optional[str] = None,
        is_superuser: bool = False
    ) -> Optional[models.User]:
        """Create a new user."""
        # Check if email or username already exists
        if UserService.get_user_by_email(db, email):
            return None
        if UserService.get_user_by_username(db, username):
            return None
        
        hashed_password = UserService.get_password_hash(password)
        user = models.User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            is_superuser=is_superuser
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        email: Optional[str] = None,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        password: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[models.User]:
        """Update a user."""
        user = UserService.get_user(db, user_id)
        if not user:
            return None
        
        # Check for email/username conflicts
        if email and email != user.email:
            if UserService.get_user_by_email(db, email):
                return None
            user.email = email
        
        if username and username != user.username:
            if UserService.get_user_by_username(db, username):
                return None
            user.username = username
        
        if full_name is not None:
            user.full_name = full_name
        
        if password:
            user.hashed_password = UserService.get_password_hash(password)
        
        if is_active is not None:
            user.is_active = is_active
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user. Returns True if deleted, False if not found."""
        user = UserService.get_user(db, user_id)
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
        """Authenticate a user by email and password."""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not UserService.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
