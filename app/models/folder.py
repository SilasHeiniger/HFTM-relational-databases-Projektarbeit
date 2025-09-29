"""
Folder Model

Represents a folder for organizing password entries.
"""

import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Folder(Base):
    """
    Folder entity for organizing password entries.
    
    Attributes:
        folder_id: UUID primary key, automatically generated
        user_id: Foreign key to users table
        name: Folder name (max 100 characters)
    """
    
    __tablename__ = "folders"
    
    # Primary key
    folder_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the folder"
    )
    
    # Foreign key to users
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="Owner of the folder"
    )
    
    # Folder name
    name = Column(
        String(100),
        nullable=False,
        comment="Name of the folder"
    )
    
    # Relationships
    user = relationship("User", back_populates="folders")
    
    password_entries = relationship(
        "PasswordEntry",
        back_populates="folder",
        cascade="all, delete-orphan"
    )