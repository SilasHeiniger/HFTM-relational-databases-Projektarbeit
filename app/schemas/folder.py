"""
Folder Pydantic Schemas

This module contains Pydantic models for Folder data validation and serialization.
"""

from uuid import UUID
from pydantic import BaseModel, Field


class FolderBase(BaseModel):
    """Base schema for Folder with common fields."""
    
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Name of the folder",
        examples=["Work", "Personal", "Banking"]
    )


class FolderCreate(FolderBase):
    """Schema for creating a new folder."""
    pass


class FolderUpdate(FolderBase):
    """Schema for updating an existing folder."""
    pass


class FolderResponse(FolderBase):
    """Schema for folder responses."""
    
    folder_id: UUID
    user_id: UUID
    
    model_config = {"from_attributes": True}