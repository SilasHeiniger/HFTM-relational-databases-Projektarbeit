"""
User Model

Represents a user account in the password manager system.
"""

import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    User entity representing a user account.
    
    Attributes:
        user_id: UUID primary key, automatically generated
        username: Unique username (max 50 characters)
        password_hash: Hashed password (max 255 characters)
    """
    
    __tablename__ = "users"
    
    # Primary key
    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the user"
    )
    
    # Username field
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="Unique username for login"
    )
    
    # Password hash field
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hashed password for authentication"
    )
    
    # Relationships
    folders = relationship(
        "Folder",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    password_entries = relationship(
        "PasswordEntry",
        back_populates="user",
        cascade="all, delete-orphan"
    )