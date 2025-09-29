"""
Password Entry Service

This module implements the business logic for password entries.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.password_entry import PasswordEntry
from app.schemas.password_entry import PasswordEntryCreate, PasswordEntryUpdate


class PasswordEntryService:
    """
    Service class for Password Entry business logic and data access.
    """
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    def create_entry(
        self, 
        user_id: UUID, 
        entry_data: PasswordEntryCreate
    ) -> PasswordEntry:
        """
        Create a new password entry.
        
        Args:
            user_id: UUID of the user creating the entry
            entry_data: Validated entry creation data
            
        Returns:
            PasswordEntry: The created entry
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # Create new entry instance
            db_entry = PasswordEntry(
                user_id=user_id,
                name=entry_data.name,
                username=entry_data.username,
                password=entry_data.password,  # TODO: Encrypt this!
                website_url=entry_data.website_url,
                notes=entry_data.notes,
                folder_id=entry_data.folder_id
            )
            
            self.db.add(db_entry)
            self.db.commit()
            self.db.refresh(db_entry)
            
            return db_entry
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def get_entry_by_id(
        self, 
        entry_id: UUID, 
        user_id: UUID
    ) -> Optional[PasswordEntry]:
        """
        Retrieve a password entry by its ID (only if it belongs to the user).
        
        Args:
            entry_id: UUID of the entry to retrieve
            user_id: UUID of the user requesting the entry
            
        Returns:
            PasswordEntry | None: The entry if found and owned by user
        """
        return self.db.query(PasswordEntry).filter(
            PasswordEntry.entry_id == entry_id,
            PasswordEntry.user_id == user_id
        ).first()
    
    def get_all_entries_for_user(
        self, 
        user_id: UUID,
        folder_id: Optional[UUID] = None
    ) -> List[PasswordEntry]:
        """
        Retrieve all password entries for a user.
        
        Args:
            user_id: UUID of the user
            folder_id: Optional folder filter
            
        Returns:
            List[PasswordEntry]: List of entries
        """
        query = self.db.query(PasswordEntry).filter(
            PasswordEntry.user_id == user_id
        )
        
        if folder_id is not None:
            query = query.filter(PasswordEntry.folder_id == folder_id)
        
        return query.all()
    
    def update_entry(
        self,
        entry_id: UUID,
        user_id: UUID,
        entry_data: PasswordEntryUpdate
    ) -> Optional[PasswordEntry]:
        """
        Update an existing password entry.
        
        Args:
            entry_id: UUID of the entry to update
            user_id: UUID of the user (for ownership check)
            entry_data: Updated entry data
            
        Returns:
            PasswordEntry | None: Updated entry if found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            db_entry = self.get_entry_by_id(entry_id, user_id)
            
            if not db_entry:
                return None
            
            # Update fields that were provided
            update_data = entry_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_entry, field, value)
            
            self.db.commit()
            self.db.refresh(db_entry)
            
            return db_entry
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def delete_entry(
        self, 
        entry_id: UUID, 
        user_id: UUID
    ) -> bool:
        """
        Delete a password entry.
        
        Args:
            entry_id: UUID of the entry to delete
            user_id: UUID of the user (for ownership check)
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            db_entry = self.get_entry_by_id(entry_id, user_id)
            
            if not db_entry:
                return False
            
            self.db.delete(db_entry)
            self.db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e


def get_password_entry_service(db: Session) -> PasswordEntryService:
    """Dependency injection helper for getting service instance."""
    return PasswordEntryService(db)