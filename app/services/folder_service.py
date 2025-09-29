"""
Folder Service

This module implements the business logic for folder management.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.folder import Folder
from app.schemas.folder import FolderCreate, FolderUpdate


class FolderService:
    """
    Service class for Folder business logic and data access.
    """
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    def create_folder(
        self, 
        user_id: UUID, 
        folder_data: FolderCreate
    ) -> Folder:
        """
        Create a new folder.
        
        Args:
            user_id: UUID of the user creating the folder
            folder_data: Validated folder creation data
            
        Returns:
            Folder: The created folder
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            db_folder = Folder(
                user_id=user_id,
                name=folder_data.name
            )
            
            self.db.add(db_folder)
            self.db.commit()
            self.db.refresh(db_folder)
            
            return db_folder
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def get_folder_by_id(
        self, 
        folder_id: UUID, 
        user_id: UUID
    ) -> Optional[Folder]:
        """
        Retrieve a folder by its ID (only if it belongs to the user).
        
        Args:
            folder_id: UUID of the folder to retrieve
            user_id: UUID of the user requesting the folder
            
        Returns:
            Folder | None: The folder if found and owned by user
        """
        return self.db.query(Folder).filter(
            Folder.folder_id == folder_id,
            Folder.user_id == user_id
        ).first()
    
    def get_all_folders_for_user(self, user_id: UUID) -> List[Folder]:
        """
        Retrieve all folders for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List[Folder]: List of folders
        """
        return self.db.query(Folder).filter(
            Folder.user_id == user_id
        ).all()
    
    def update_folder(
        self,
        folder_id: UUID,
        user_id: UUID,
        folder_data: FolderUpdate
    ) -> Optional[Folder]:
        """
        Update an existing folder.
        
        Args:
            folder_id: UUID of the folder to update
            user_id: UUID of the user (for ownership check)
            folder_data: Updated folder data
            
        Returns:
            Folder | None: Updated folder if found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            db_folder = self.get_folder_by_id(folder_id, user_id)
            
            if not db_folder:
                return None
            
            db_folder.name = folder_data.name
            
            self.db.commit()
            self.db.refresh(db_folder)
            
            return db_folder
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def delete_folder(
        self, 
        folder_id: UUID, 
        user_id: UUID
    ) -> bool:
        """
        Delete a folder (entries will have folder_id set to NULL).
        
        Args:
            folder_id: UUID of the folder to delete
            user_id: UUID of the user (for ownership check)
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            db_folder = self.get_folder_by_id(folder_id, user_id)
            
            if not db_folder:
                return False
            
            self.db.delete(db_folder)
            self.db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e


def get_folder_service(db: Session) -> FolderService:
    """Dependency injection helper for getting service instance."""
    return FolderService(db)