"""
User Pydantic Schemas

This module contains Pydantic models for User data validation and serialization.
"""

from uuid import UUID
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base schema for User with common fields."""
    
    username: str = Field(
        min_length=3,
        max_length=50,
        description="Unique username for login",
        examples=["john_doe", "alice123"]
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(
        min_length=6,
        description="Password for the account (will be hashed)",
        examples=["SecurePass123!"]
    )


class UserResponse(UserBase):
    """Schema for user responses (without password hash)."""
    
    user_id: UUID
    
    model_config = {"from_attributes": True}