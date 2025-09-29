"""
Password Entry Pydantic Schemas

This module contains Pydantic models for Password Entry data validation and serialization.
"""

from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class PasswordEntryBase(BaseModel):
    """Base schema for Password Entry with common fields."""
    
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Name/title of the password entry",
        examples=["Gmail Account", "GitHub", "Amazon"]
    )
    username: Optional[str] = Field(
        None,
        max_length=100,
        description="Username or email for the service",
        examples=["user@example.com", "myusername"]
    )
    password: Optional[str] = Field(
        None,
        description="Password (will be encrypted before storage)",
        examples=["MySecurePassword123!"]
    )
    website_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL of the website/service",
        examples=["https://www.google.com", "https://github.com"]
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the entry",
        examples=["Personal account", "Work email account"]
    )
    folder_id: Optional[UUID] = Field(
        None,
        description="Optional folder to organize this entry"
    )


class PasswordEntryCreate(PasswordEntryBase):
    """Schema for creating a new password entry."""
    pass


class PasswordEntryUpdate(BaseModel):
    """Schema for updating an existing password entry (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    username: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = None
    website_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    folder_id: Optional[UUID] = None


class PasswordEntryResponse(BaseModel):
    """Schema for password entry responses (without the actual password)."""
    
    entry_id: UUID
    user_id: UUID
    folder_id: Optional[UUID]
    name: str
    username: Optional[str]
    website_url: Optional[str]
    notes: Optional[str]
    
    model_config = {"from_attributes": True}


class PasswordEntryWithPassword(PasswordEntryResponse):
    """Schema that includes the decrypted password (use carefully!)."""
    
    password: Optional[str]