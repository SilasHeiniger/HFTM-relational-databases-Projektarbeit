"""
User Service

This module implements the business logic for user management.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    """
    Service class for User business logic and data access.
    """
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: Validated user creation data
            
        Returns:
            User: The created user
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # TODO: Hash the password before storing!
            # For now, storing plain text (DO NOT USE IN PRODUCTION!)
            db_user = User(
                username=user_data.username,
                password_hash=user_data.password  # Should be hashed!
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            return db_user
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by their ID."""
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def delete_user(self, user_id: UUID) -> bool:
        """
        Delete a user (will cascade delete all their data).
        
        Args:
            user_id: UUID of the user to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            db_user = self.get_user_by_id(user_id)
            
            if not db_user:
                return False
            
            self.db.delete(db_user)
            self.db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e


def get_user_service(db: Session) -> UserService:
    """Dependency injection helper for getting service instance."""
    return UserService(db)