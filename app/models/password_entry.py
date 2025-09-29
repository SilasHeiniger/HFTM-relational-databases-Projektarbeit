"""
Password Entry Model

Represents a password entry with credentials and metadata.
"""

import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PasswordEntry(Base):
    """
    Password Entry entity representing stored credentials.
    
    Attributes:
        entry_id: UUID primary key, automatically generated
        user_id: Foreign key to users table
        folder_id: Optional foreign key to folders table
        name: Entry name (max 100 characters)
        username: Optional username (max 100 characters)
        password: Optional password (TEXT field for encrypted data)
        website_url: Optional website URL (max 500 characters)
        notes: Optional notes (TEXT field)
    """
    
    __tablename__ = "password_entries"
    
    # Primary key
    entry_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the password entry"
    )
    
    # Foreign key to users (required)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="Owner of the password entry"
    )
    
    # Foreign key to folders (optional)
    folder_id = Column(
        UUID(as_uuid=True),
        ForeignKey("folders.folder_id", ondelete="SET NULL"),
        nullable=True,
        comment="Folder containing this entry (optional)"
    )
    
    # Entry name
    name = Column(
        String(100),
        nullable=False,
        comment="Name/title of the password entry"
    )
    
    # Username
    username = Column(
        String(100),
        nullable=True,
        comment="Username or email for the service"
    )
    
    # Password (should be encrypted)
    password = Column(
        Text,
        nullable=True,
        comment="Encrypted password"
    )
    
    # Website URL
    website_url = Column(
        String(500),
        nullable=True,
        comment="URL of the website/service"
    )
    
    # Notes
    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes about the entry"
    )
    
    # Relationships
    user = relationship("User", back_populates="password_entries")
    folder = relationship("Folder", back_populates="password_entries")